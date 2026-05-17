from langsmith import Client

langsmith_client = Client()

def send_feedback(run_id, key, score, comment=""):
    try:
        langsmith_client.create_feedback(run_id=run_id, key=key, score=score, comment=comment)
    except Exception as e:
        print(f"LangSmith feedback error: {e}")

def add_to_dataset(user_text, reply, score, run_id):
    try:
        dataset_name = "learning-hub-evals"
        datasets = list(langsmith_client.list_datasets(dataset_name=dataset_name))
        dataset = datasets[0] if datasets else langsmith_client.create_dataset(dataset_name)
        langsmith_client.create_example(
            inputs={"question": user_text},
            outputs={"answer": reply, "score": score},
            dataset_id=dataset.id
        )
    except Exception as e:
        print(f"LangSmith dataset error: {e}")
