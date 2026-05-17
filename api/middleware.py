from flask import request
import time

def register_middleware(app):
    @app.before_request
    def log_request():
        request.start_time = time.time()

    @app.after_request
    def log_response(response):
        duration = time.time() - getattr(request, 'start_time', time.time())
        print(f"{request.method} {request.path} {response.status_code} {duration:.3f}s")
        return response
