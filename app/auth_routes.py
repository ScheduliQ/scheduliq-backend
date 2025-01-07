from flask import Blueprint, jsonify, request
from models.database import get_collection
from firebase_admin import auth
from configs.firebaseConfig import firebaseApp  # לאתחול חד-פעמי
from app.middlewares.session_middleware import verify_token
from models.user_model import UserModel
from pymongo.errors import DuplicateKeyError

auth_api = Blueprint('auth_api', __name__)
# users_collection=get_collection('users')

#Register User
# @auth_api.route("/register-user", methods=["POST"])  # יצירת נתיב API עם HTTP POST
# @verify_token
# def register_user():
#     try:
#         # Extract the user details from the request body
#         user_data = request.json

#         # Check if the user already exists in the database
#         if users_collection.find_one({"uid":user_data.get("uid")}):
#             return jsonify({"message": "User already exists"}), 201

#         # Create the new user object
#         new_user = {
#             "uid": user_data.get("uid"),  # Firebase unique ID
#             "email": user_data.get("email"),  # User's email
#             "first_name": user_data.get("firstName"),  # First name
#             "last_name": user_data.get("lastName"),  # Last name
#             "phone": user_data.get("phone"),  # Phone number
#             "profile_picture": user_data.get("profilePicture"),  # Cloudinary URL
#             "gender": user_data.get("gender"),  # Gender
#             "jobs": user_data.get("jobs"),  # Job titles
#             "business_id": user_data.get("businessId"),  # Business ID
#             "role": "worker",  # Default role for new users
#             "created_at": user_data.get("createdAt"),  # Registration time from Firebase token
#         }

#         # Save the new user to MongoDB
#         users_collection.insert_one(new_user)

#         # Debugging: Print the new user details in the console
#         # print("New user registered:", new_user)

#         # Return success response to the front-end
#         return jsonify({"message": "User registered successfully"}), 201

#     except Exception as e:
#         # Handle errors and send appropriate response
#         print("Error during registration:", str(e))
#         return jsonify({"error": str(e)}), 401



@auth_api.route("/register-user", methods=["POST"])
# @verify_token #add later because this will be a button inside settings
def register_user():
    try:
        # Extract user data from the request
        user_data = request.get_json()
        role=user_data.get("role", "worker")    
        uid=user_data.get("uid")       
        # Create a new user
        user = UserModel.create(user_data)
        auth.set_custom_user_claims(uid, {"role": role})

        return jsonify({"message": "User registered successfully"}), 201

    except DuplicateKeyError:
        return jsonify({"error": "User with this UID already exists"}), 409  # Conflict

    except ValueError as e:
        return jsonify({"error": str(e)}), 400  # Validation or not found error.


    except Exception as e:
        print("Internal server error:", str(e))

        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@auth_api.route("/create-manager", methods=["POST"])
def create_admin():
    try:
        # Extract data from request
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        role = "manager"  # Role is hardcoded to 'admin'

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        

        # Create user in Firebase
        user_record = auth.create_user(email=data.get("email"),password=data.get("password"))
        print("*********0",user_record)
        # Set custom claims to make the user an admin
        auth.set_custom_user_claims(user_record.uid, {"role": role})

        # Add UID to the JSON data
        data["uid"] = user_record.uid
        data["role"] = role  # Ensure role is included
        data["created_at"] = user_record.user_metadata.creation_timestamp
        data.pop("password", None)

        # Save user in MongoDB
        users_collection = get_collection("users")
        new_user = data
        users_collection.insert_one(new_user)

        return jsonify({"message": "Manager user created successfully"}), 201

    except DuplicateKeyError:
        return jsonify({"error": "User with this email already exists"}), 409

    except Exception as e:
        print("Internal server error:", str(e))
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500