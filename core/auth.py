from flask_jwt_extended import JWTManager

jwt = JWTManager()

def init_auth(app):
    jwt.init_app(app)
