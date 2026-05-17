import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = 'eli3-secret-key'
    JWT_SECRET_KEY = 'fde-jwt-super-secret-key-learning-hub-2026'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    PROMETHEUS_METRICS_EXPORT_PORT = 5000
    LANGSMITH_API_KEY = os.getenv('LANGSMITH_API_KEY')
    LANGSMITH_PROJECT = os.getenv('LANGSMITH_PROJECT', 'learning-hub')
    USERS = {
        "kunal": "password123",
        "demo": "demo123",
        "admin": "admin123"
    }
