from flask import Blueprint, jsonify, request
from models.database import get_collection
from app.middlewares.session_middleware import verify_token
from cloudinary.uploader import upload
from configs.cloudinary_config import cloudinary


user_api = Blueprint('user_api', __name__)

#get all users
@user_api.route('/users', methods=['GET'])
def get_users():
    users_collection = get_collection('users')
    users = list(users_collection.find())  # שליפת כל המסמכים מהקולקשן
    for user in users:
        user['_id'] = str(user['_id'])  # המרה של ObjectId למחרוזת
    return jsonify(users), 200


@user_api.route('/dashboard', methods=['GET'])
@verify_token
def get_dash():
    user_email=request.user.get('email', 'Unknown user')
    message={'message':f"Welcome to the dashboard, {user_email}!"}

    return jsonify(message), 200


@user_api.route('/upload', methods=['POST'])
# @verify_token
def upload_file():
    try:
        # Ensure a file is provided in the request
        file = request.files.get('file')
        if not file:
            return jsonify({"error": "No file provided"}), 400

        # Use a folder name from the request or default to 'uploads'
        # folder_name = request.form.get('folder', 'uploads')
        print("Request Files:", request.files)
        print("File Received:", request.files.get('file'))

        # Upload the file stream directly to Cloudinary
        upload_result = upload(
            file,
            folder="profile_pictures" # Specify the folder
        )

        # Return the secure URL of the uploaded file
        return jsonify({
            "message": "File uploaded successfully",
            "url": upload_result['secure_url']
        }), 200

    except Exception as e:
        # Handle exceptions and return an error response
        print("Cloudinary Upload Error:", str(e))
        return jsonify({"error": str(e)}), 500

