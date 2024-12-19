from flask import request, jsonify
from firebase_admin import auth

def verify_token(f):
    """
    Decorator to verify Firebase token in cookies.
    """
    def wrapper(*args, **kwargs):
        token = request.cookies.get('token')  # Fetch the token from cookies
        if not token:
            return jsonify({"error": "Unauthorized"}), 401

        try:
            decoded_token = auth.verify_id_token(token)  # Verify the token
            request.user = decoded_token  # Attach user info to the request
        except Exception:
            return jsonify({"error": "Invalid session"}), 401

        return f(*args, **kwargs)  # Call the original function

    wrapper.__name__ = f.__name__  # Maintain the original function name
    return wrapper
