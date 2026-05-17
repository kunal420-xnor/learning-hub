from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
