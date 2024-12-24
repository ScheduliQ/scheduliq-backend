from flask import request, jsonify
from firebase_admin import auth

def verify_token(f):
    """
    Decorator to verify Firebase token from cookies or headers.
    """
    def wrapper(*args, **kwargs):
        # Check for token in cookies or headers
        token = request.cookies.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({"error": "Unauthorized: No token provided"}), 401

        try:
            # Verify the token
            decoded_token = auth.verify_id_token(token)
            request.user = decoded_token  # Attach user info to the request
        except auth.InvalidIdTokenError:
            return jsonify({"error": "Invalid ID token"}), 401
        except auth.ExpiredIdTokenError:
            return jsonify({"error": "Token has expired"}), 401
        except auth.RevokedIdTokenError:
            return jsonify({"error": "Token has been revoked"}), 401
        except Exception as e:
            return jsonify({"error": f"Authentication failed: {str(e)}"}), 401

        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper
