from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid
from agents.eli3.prompts import SYSTEM_PROMPT
from agents.eli3.service import explain
from core.observability import send_feedback, add_to_dataset

eli3_bp = Blueprint('eli3', __name__)

@eli3_bp.route('/explain', methods=['POST'])
@jwt_required()
def explain_route():
    current_user = get_jwt_identity()
    session_id = f"{current_user}_{session.get('session_id', str(uuid.uuid4()))}"
    data = request.json
    user_text = data['text']
    count = data['count']

    reply, run_id = explain(session_id, user_text, count, SYSTEM_PROMPT)
    return jsonify({"reply": reply, "run_id": run_id, "user": current_user})

@eli3_bp.route('/feedback', methods=['POST'])
@jwt_required()
def feedback():
    data = request.json
    send_feedback(data.get('run_id'), "user_feedback", data.get('score'), data.get('comment', ''))
    return jsonify({"status": "ok"})

@eli3_bp.route('/create_dataset', methods=['POST'])
@jwt_required()
def create_dataset():
    data = request.json
    add_to_dataset(data.get('user_text'), data.get('reply'), data.get('score'), data.get('run_id'))
    return jsonify({"status": "ok"})
