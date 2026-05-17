from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid
import os
from agents.spanish.prompts import SYSTEM_PROMPT
from agents.spanish.service import chat
from agents.spanish.rag import load_pdf, list_documents

spanish_bp = Blueprint('spanish', __name__)

@spanish_bp.route('/spanish/chat', methods=['POST'])
@jwt_required()
def spanish_chat():
    current_user = get_jwt_identity()
    session_id = f"{current_user}_{session.get('session_id', str(uuid.uuid4()))}"
    data = request.json
    user_text = data['text']

    reply, run_id, format_valid, context_used = chat(session_id, user_text, SYSTEM_PROMPT)
    return jsonify({
        "reply": reply,
        "run_id": run_id,
        "format_valid": format_valid,
        "context_used": context_used,
        "user": current_user
    })

@spanish_bp.route('/rag/upload', methods=['POST'])
@jwt_required()
def upload_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files['file']
    if not file.filename.endswith('.pdf'):
        return jsonify({"error": "Only PDF files supported"}), 400
    os.makedirs('documents', exist_ok=True)
    filepath = f"documents/{file.filename}"
    file.save(filepath)
    chunks = load_pdf(filepath, "spanish_docs")
    return jsonify({"message": f"Loaded {chunks} chunks from {file.filename}", "chunks": chunks})

@spanish_bp.route('/rag/status', methods=['GET'])
@jwt_required()
def rag_status():
    count = list_documents("spanish_docs")
    return jsonify({"chunks_loaded": count, "ready": count > 0})
