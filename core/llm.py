import ollama
from langsmith import traceable
from langsmith.run_helpers import get_current_run_tree

@traceable(name="LLM Call")
def call_llm(messages):
    run_tree = get_current_run_tree()
    run_id = str(run_tree.id) if run_tree else None
    result = ollama.chat(model="gemma3:4b", messages=messages)
    return result, run_id
