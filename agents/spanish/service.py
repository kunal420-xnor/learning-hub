import re
from core.llm import call_llm
from core.observability import send_feedback
from agents.spanish.rag import query_collection

spanish_histories = {}

def validate_format(reply):
    has_spanish = bool(re.search(r'SPANISH:\s*.+', reply, re.IGNORECASE))
    has_english = bool(re.search(r'ENGLISH:\s*.+', reply, re.IGNORECASE))
    has_tip = bool(re.search(r'TIP:\s*.+', reply, re.IGNORECASE))
    return has_spanish and has_english and has_tip

def get_or_create_history(session_id, system_prompt, context=""):
    if session_id not in spanish_histories:
        spanish_histories[session_id] = [
            {"role": "system", "content": system_prompt + context}
        ]
    return spanish_histories[session_id]

def chat(session_id, user_text, system_prompt):
    context_chunks = query_collection("spanish_docs", user_text, n_results=2)
    context = ""
    if context_chunks:
        context = "\n\nRelevant context:\n" + "\n---\n".join(context_chunks)

    history = get_or_create_history(session_id, system_prompt, context)
    history.append({"role": "user", "content": user_text})

    response, run_id = call_llm(history)
    reply = response["message"]["content"].strip()
    history.append({"role": "assistant", "content": reply})

    format_valid = validate_format(reply)
    if run_id:
        send_feedback(run_id, "format_check", 1.0 if format_valid else 0.0)

    return reply, run_id, format_valid, len(context_chunks) > 0
