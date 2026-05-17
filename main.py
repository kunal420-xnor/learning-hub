from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
from config import Config
from core.auth import init_auth
from core.database import init_db
from api.errors import register_error_handlers
from api.middleware import register_middleware
from agents.eli3.routes import eli3_bp
from agents.spanish.routes import spanish_bp

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)
init_auth(app)
init_db()
register_error_handlers(app)
register_middleware(app)

REQUEST_COUNT = Counter(
    'learning_hub_requests_total',
    'Total request count',
    ['method', 'endpoint', 'status']
)
REQUEST_LATENCY = Histogram(
    'learning_hub_request_latency_seconds',
    'Request latency in seconds',
    ['endpoint']
)
LLM_CALLS = Counter(
    'learning_hub_llm_calls_total',
    'Total LLM calls',
    ['agent']
)

@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def record_metrics(response):
    latency = time.time() - getattr(request, 'start_time', time.time())
    endpoint = request.path
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        status=response.status_code
    ).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
    return response

app.register_blueprint(eli3_bp)
app.register_blueprint(spanish_bp)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if username in Config.USERS and Config.USERS[username] == password:
        token = create_access_token(identity=username)
        return jsonify({"token": token, "username": username})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "version": "1.0.0"})

@app.route('/metrics', methods=['GET'])
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
