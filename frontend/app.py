from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from langsmith import traceable, Client
import ollama
import uuid
import re
from database import init_db, save_message

app = Flask(__name__)
app.secret_key = 'eli3-secret-key'
CORS(app)

init_db()
langsmith_client = Client()

conversation_histories = {}
spanish_histories = {}

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

@traceable(name="ELI3 Explanation")
def get_eli3_response(messages):
    return ollama.chat(model="gemma3:4b", messages=messages)

@traceable(name="Spanish Tutor Response")
def get_spanish_response(messages):
    return ollama.chat(model="gemma3:4b", messages=messages)

def validate_spanish_format(reply):
    has_spanish = bool(re.search(r'SPANISH:\s*.+', reply, re.IGNORECASE))
    has_english = bool(re.search(r'ENGLISH:\s*.+', reply, re.IGNORECASE))
    has_tip = bool(re.search(r'TIP:\s*.+', reply, re.IGNORECASE))
    return has_spanish and has_english and has_tip

@app.route('/explain', methods=['POST'])
def explain():
    session_id = session.get('session_id', str(uuid.uuid4()))
    data = request.json
    user_text = data['text']
    count = data['count']

    if session_id not in conversation_histories:
        conversation_histories[session_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    history = conversation_histories[session_id]
    history.append({"role": "user", "content": f"Explain this like I'm 3: {user_text}"})

    run_id = str(uuid.uuid4())
    response = get_eli3_response(history, langsmith_extra={"run_id": run_id})
    reply = response["message"]["content"].strip()

    passed = True
    if count > 3 and len(reply) > 400:
        passed = False
        history.append({"role": "assistant", "content": reply})
        history.append({"role": "user", "content": "Too long! Explain the same thing in under 400 characters. Very brief and simple."})
        retry = get_eli3_response(history)
        reply = retry["message"]["content"].strip()[:400]

    history.append({"role": "assistant", "content": reply})
    save_message(session_id, user_text, reply, passed)

    return jsonify({"reply": reply, "run_id": run_id})

@app.route('/spanish/chat', methods=['POST'])
def spanish_chat():
    import re
    session_id = session.get('session_id', str(uuid.uuid4()))
    data = request.json
    user_text = data['text']

    if session_id not in spanish_histories:
        spanish_histories[session_id] = [
            {"role": "system", "content": SPANISH_PROMPT}
        ]

    history = spanish_histories[session_id]
    history.append({"role": "user", "content": user_text})

    run_id = str(uuid.uuid4())
    response = get_spanish_response(history, langsmith_extra={"run_id": run_id})
    reply = response["message"]["content"].strip()

    history.append({"role": "assistant", "content": reply})

    format_valid = validate_spanish_format(reply)
    try:
        langsmith_client.create_feedback(
            run_id=run_id,
            key="format_check",
            score=1.0 if format_valid else 0.0,
            comment="SPANISH/ENGLISH/TIP format correct" if format_valid else "Missing required format sections"
        )
    except Exception as e:
        print(f"LangSmith feedback error: {e}")

    return jsonify({"reply": reply, "run_id": run_id, "format_valid": format_valid})

@app.route('/feedback', methods=['POST'])
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
        print(f"Feedback error: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/create_dataset', methods=['POST'])
def create_dataset():
    data = request.json
    run_id = data.get('run_id')
    score = data.get('score')
    user_text = data.get('user_text')
    reply = data.get('reply')

    try:
        dataset_name = "learning-hub-evals"
        datasets = list(langsmith_client.list_datasets(dataset_name=dataset_name))
        if datasets:
            dataset = datasets[0]
        else:
            dataset = langsmith_client.create_dataset(dataset_name)

        langsmith_client.create_example(
            inputs={"question": user_text},
            outputs={"answer": reply, "score": score},
            dataset_id=dataset.id
        )
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"Dataset error: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
