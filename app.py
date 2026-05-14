from flask import Flask, request, jsonify, render_template, session
import ollama
import uuid
from database import init_db, save_message

app = Flask(__name__)
app.secret_key = 'eli3-secret-key'

init_db()

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
    "SPANISH: <your spanish sentence here> "
    "ENGLISH: <english translation here> "
    "TIP: <one short encouragement or grammar tip in English> "
    "Rules: "
    "1. Always use the exact labels SPANISH:, ENGLISH:, TIP: on separate lines. "
    "2. Keep the SPANISH part short, max one or two sentences. "
    "3. Introduce one new word per message wrapped in asterisks like *hola*. "
    "4. If the user makes a mistake, correct it in the TIP line. "
    "5. Never mix Spanish and English on the same line. "
    "6. Start very simple with greetings and build up gradually."
)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/eli3')
def eli3():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('index.html')

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

    response = ollama.chat(model="gemma3:4b", messages=history)
    reply = response["message"]["content"].strip()

    passed = True
    if count > 3 and len(reply) > 400:
        passed = False
        history.append({"role": "assistant", "content": reply})
        history.append({
            "role": "user",
            "content": "Too long! Explain the same thing in under 400 characters. Very brief and simple."
        })
        retry = ollama.chat(model="gemma3:4b", messages=history)
        reply = retry["message"]["content"].strip()[:400]

    history.append({"role": "assistant", "content": reply})
    save_message(session_id, user_text, reply, passed)

    return jsonify({"reply": reply})

@app.route('/spanish')
def spanish():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('spanish.html')

@app.route('/spanish/chat', methods=['POST'])
def spanish_chat():
    session_id = session.get('session_id', str(uuid.uuid4()))
    data = request.json
    user_text = data['text']

    if session_id not in spanish_histories:
        spanish_histories[session_id] = [
            {"role": "system", "content": SPANISH_PROMPT}
        ]

    history = spanish_histories[session_id]
    history.append({"role": "user", "content": user_text})

    response = ollama.chat(model="gemma3:4b", messages=history)
    reply = response["message"]["content"].strip()

    history.append({"role": "assistant", "content": reply})

    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(debug=True)
