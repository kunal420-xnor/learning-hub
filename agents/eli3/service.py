from core.llm import call_llm
from core.database import save_message

conversation_histories = {}

def get_or_create_history(session_id, system_prompt):
    if session_id not in conversation_histories:
        conversation_histories[session_id] = [
            {"role": "system", "content": system_prompt}
        ]
    return conversation_histories[session_id]

def explain(session_id, user_text, count, system_prompt):
    history = get_or_create_history(session_id, system_prompt)
    history.append({"role": "user", "content": f"Explain this like I'm 3: {user_text}"})

    response, run_id = call_llm(history)
    reply = response["message"]["content"].strip()

    passed = True
    if count > 3 and len(reply) > 400:
        passed = False
        history.append({"role": "assistant", "content": reply})
        history.append({"role": "user", "content": "Too long! Under 400 characters. Very brief and simple."})
        retry, _ = call_llm(history)
        reply = retry["message"]["content"].strip()[:400]

    history.append({"role": "assistant", "content": reply})
    save_message(session_id, user_text, reply, passed)
    return reply, run_id
