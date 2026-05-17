from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from langsmith import traceable, Client
from langsmith.run_helpers import get_current_run_tree
import ollama
import uuid
import re
import os
from database import init_db, save_message

app = Flask(__name__)
app.secret_key = 'eli3-secret-key'
app.config['JWT_SECRET_KEY'] = 'fde-jwt-super-secret-2026'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False

CORS(app)
jwt = JWTManager(app)
init_db()
langsmith_client = Client()

conversation_histories = {}
spanish_histories = {}

USERS = {
    "kunal": "password123",
    "demo": "demo123",
    "admin": "admin123"
}

SYSTEM_PROMPT = (
    "You are a warm, friendly MIT and Harvard professor who makes complex ideas simple. "
    "Explain like the person is 3 years old using toys, food, animals, and everyday objects. "
    "Keep responses under 3 sentences, never more. "
    "If they dont understand, try a completely different analogy and never repeat yourself. "
    "Never give up or deflect, always make a genuine new attempt. "
    "Bring the enthusiasm of a world-class professor but the vocabulary of a childrens book. "
    "End with one playful question to check understanding."
)

SPANISH_PROMPT = (
    "You are a warm, encouraging Spanish tutor for a complete beginner. "
    "You MUST follow this exact format for EVERY response, no exceptions: "
    "SPANISH: <your spanish sentence here>\n"
    "ENGLISH: <english translation here>\n"
    "TIP: <one short encouragement or grammar tip in English>\n"
    "Rules: "
    "1. Always use the exact labels SPANISH:, ENGLISH:, TIP: on separate lines. "
    "2. Keep the SPANISH part short, max one or two sentences. "
    "3. Introduce one new word per message wrapped in asterisks like *hola*. "
    "4. If the user makes a mistake, correct it in the TIP line. "
    "5. Never mix Spanish and English on the same line. "
    "6. Start very simple with greetings and build up gradually."
)

def validate_spanish_format(reply):
    has_spanish = bool(re.search(r'SPANISH:\s*.+', reply, re.IGNORECASE))
    has_english = bool(re.search(r'ENGLISH:\s*.+', reply, re.IGNORECASE))
    has_tip = bool(re.search(r'TIP:\s*.+', reply, re.IGNORECASE))
    return has_spanish and has_english and has_tip

@traceable(name="ELI3 Explanation")
def get_eli3_response(messages):
    run_tree = get_current_run_tree()
    run_id = str(run_tree.id) if run_tree else None
    result = ollama.chat(model="gemma3:4b", messages=messages)
    return result, run_id

@traceable(name="Spanish Tutor Response")
def get_spanish_response(messages):
    run_tree = get_current_run_tree()
    run_id = str(run_tree.id) if run_tree else None
    result = ollama.chat(model="gemma3:4b", messages=messages)
    return result, run_id

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username in USERS and USERS[username] == password:
        token = create_access_token(identity=username)
        return jsonify({
            "token": token,
            "username": username,
            "message": f"Welcome {username}!"
        })
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/explain', methods=['POST'])
@jwt_required()
def explain():
    current_user = get_jwt_identity()
    session_id = f"{current_user}_{session.get('session_id', str(uuid.uuid4()))}"
    data = request.json
    user_text = data['text']
    count = data['count']

    if session_id not in conversation_histories:
        conversation_histories[session_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    history = conversation_histories[session_id]
    history.append({"role": "user", "content": f"Explain this like I'm 3: {user_text}"})

    response, run_id = get_eli3_response(history)
    reply = response["message"]["content"].strip()

    passed = True
    if count > 3 and len(reply) > 400:
        passed = False
        history.append({"role": "assistant", "content": reply})
        history.append({"role": "user", "content": "Too long! Explain the same thing in under 400 characters. Very brief and simple."})
        retry, _ = get_eli3_response(history)
        reply = retry["message"]["content"].strip()[:400]

    history.append({"role": "assistant", "content": reply})
    save_message(session_id, user_text, reply, passed)

    return jsonify({"reply": reply, "run_id": run_id, "user": current_user})

@app.route('/spanish/chat', methods=['POST'])
@jwt_required()
def spanish_chat():
    current_user = get_jwt_identity()
    session_id = f"{current_user}_{session.get('session_id', str(uuid.uuid4()))}"
    data = request.json
    user_text = data['text']

    if session_id not in spanish_histories:
        spanish_histories[session_id] = [
            {"role": "system", "content": SPANISH_PROMPT}
        ]

    history = spanish_histories[session_id]
    history.append({"role": "user", "content": user_text})

    response, run_id = get_spanish_response(history)
    reply = response["message"]["content"].strip()

    history.append({"role": "assistant", "content": reply})

    format_valid = validate_spanish_format(reply)
    if run_id:
        try:
            langsmith_client.create_feedback(
                run_id=run_id,
                key="format_check",
                score=1.0 if format_valid else 0.0,
                comment="Format correct" if format_valid else "Missing SPANISH/ENGLISH/TIP sections"
            )
        except Exception as e:
            print(f"LangSmith format feedback error: {e}")

    return jsonify({"reply": reply, "run_id": run_id, "format_valid": format_valid, "user": current_user})

@app.route('/feedback', methods=['POST'])
@jwt_required()
def feedback():
    data = request.json
    run_id = data.get('run_id')
    score = data.get('score')
    comment = data.get('comment', '')

    try:
        langsmith_client.create_feedback(
            run_id=run_id,
            key="user_feedback",
            score=score,
            comment=comment
        )
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/create_dataset', methods=['POST'])
@jwt_required()
def create_dataset():
    data = request.json
    run_id = data.get('run_id')
    score = data.get('score')
    user_text = data.get('user_text')
    reply = data.get('reply')

    try:
        dataset_name = "learning-hub-evals"
        datasets = list(langsmith_client.list_datasets(dataset_name=dataset_name))
        dataset = datasets[0] if datasets else langsmith_client.create_dataset(dataset_name)
        langsmith_client.create_example(
            inputs={"question": user_text},
            outputs={"answer": reply, "score": score},
            dataset_id=dataset.id
        )
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
