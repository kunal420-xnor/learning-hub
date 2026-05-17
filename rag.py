import chromadb
from sentence_transformers import SentenceTransformer
import pypdf
import os

model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path="./chroma_db")

def get_or_create_collection(name):
    return client.get_or_create_collection(name=name)

def load_pdf(filepath, collection_name):
    collection = get_or_create_collection(collection_name)
    reader = pypdf.PdfReader(filepath)
    chunks = []
    ids = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if not text:
            continue
        words = text.split()
        for j in range(0, len(words), 200):
            chunk = ' '.join(words[j:j+200])
            if len(chunk.strip()) > 50:
                chunks.append(chunk)
                ids.append(f"{os.path.basename(filepath)}_page{i}_chunk{j}")

    if not chunks:
        return 0

    embeddings = model.encode(chunks).tolist()
    collection.upsert(
        documents=chunks,
        embeddings=embeddings,
        ids=ids
    )
    return len(chunks)

def query_collection(collection_name, query, n_results=3):
    collection = get_or_create_collection(collection_name)
    count = collection.count()
    if count == 0:
        return []

    embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=embedding,
        n_results=min(n_results, count)
    )
    return results['documents'][0] if results['documents'] else []

def list_documents(collection_name):
    collection = get_or_create_collection(collection_name)
    return collection.count()
