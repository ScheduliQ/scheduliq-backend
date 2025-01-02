from flask import Blueprint, jsonify, request
from models.database import get_collection
from firebase_admin import auth
from configs.firebaseConfig import firebaseApp  # לאתחול חד-פעמי
from app.middlewares.session_middleware import verify_token

auth_api = Blueprint('auth_api', __name__)
users_collection=get_collection('users')

#Register User
@auth_api.route("/register-user", methods=["POST"])  # יצירת נתיב API עם HTTP POST
# @verify_token
def register_user():
    try:
        # Extract the user details from the request body
        user_data = request.json

        # Check if the user already exists in the database
        if users_collection.find_one({"uid":user_data.get("uid")}):
            return jsonify({"message": "User already exists"}), 201

        # Create the new user object
        new_user = {
            "uid": user_data.get("uid"),  # Firebase unique ID
            "email": user_data.get("email"),  # User's email
            "first_name": user_data.get("firstName"),  # First name
            "last_name": user_data.get("lastName"),  # Last name
            "phone": user_data.get("phone"),  # Phone number
            "profile_picture": user_data.get("profilePicture"),  # Cloudinary URL
            "gender": user_data.get("gender"),  # Gender
            "jobs": user_data.get("jobs"),  # Job titles
            "business_id": user_data.get("businessId"),  # Business ID
            "role": "worker",  # Default role for new users
            "created_at": user_data.get("createdAt"),  # Registration time from Firebase token
        }

        # Save the new user to MongoDB
        users_collection.insert_one(new_user)

        # Debugging: Print the new user details in the console
        # print("New user registered:", new_user)

        # Return success response to the front-end
        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        # Handle errors and send appropriate response
        print("Error during registration:", str(e))
        return jsonify({"error": str(e)}), 401
