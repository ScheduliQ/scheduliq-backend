from flask import Blueprint, jsonify, request
from models.database import get_collection
from app.middlewares.session_middleware import verify_token
from cloudinary.uploader import upload
from configs.cloudinary_config import cloudinary
from models.user_model import UserModel
from app.middlewares.email_sender import send_contact_email


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

@user_api.route('/userdata/<uid>', methods=['GET'])
def get_user_by_uid(uid):
    user = UserModel.find_by_uid(uid)
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify(user), 200

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
    

@user_api.route('/userSetting/<uid>', methods=['PUT'])
def update_user(uid):
    try:
        update_data = request.get_json()
        if not update_data:
            return jsonify({"error": "No update data provided"}), 400

        updated_user = UserModel.update(uid, update_data)
        return jsonify(updated_user), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_api.route('/contact', methods=['POST'])
def contact():
    data = request.get_json()
    name = data.get('name', '')
    email = data.get('email', '')
    subject = data.get('subject', 'No Subject')
    message_text = data.get('message', '')

    # Validate required fields
    if not name or not email or not message_text:
        return jsonify({'error': 'All fields are required'}), 400

    try:
        send_contact_email(name, email, subject, message_text)
        return jsonify({'message': 'Email sent successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to send email'}), 500
    

    
@user_api.route('/employees', methods=['GET'])
def get_all_employees_route():
    """
    GET /employees
    Retrieve all employees with their first name, last name, and jobs (split into a list).
    """
    try:
        employees = UserModel.get_all_employees()  # Retrieves all employee documents
        # Filter each document to only include first_name, last_name, and split jobs into a list
        result = [
            {
                "first_name": emp.get("first_name", ""),
                "last_name": emp.get("last_name", ""),
                "jobs": [job.strip() for job in emp.get("jobs", "").split(",") if job.strip()]
            }
            for emp in employees
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@user_api.route('/employees-management', methods=['GET'])
def get_all_employees_management():
    """
    GET /employees
    Retrieve all employees with their first name, last name, and jobs (split into a list).
    """
    try:
        employees = UserModel.get_all_employees()  # Retrieves all employee documents
        # Filter each document to only include first_name, last_name, and split jobs into a list
        result = [
            {
                "uid": emp.get("uid", ""),
                "name": emp.get("first_name", "")+" "+emp.get("last_name", ""),
                "roles": [job.strip() for job in emp.get("jobs", "").split(",") if job.strip()]
            }
            for emp in employees
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@user_api.route('/employees-management', methods=['PUT'])
def update_employees():
    try:
        data = request.get_json()
        # Get the list of employees from the payload.
        employees_list = data.get("employees", [])
        for emp in employees_list:
            uid = emp.get("uid")
            roles_list = emp.get("roles", [])
            jobs = ",".join(roles_list)
            data = {
                "jobs": jobs
            }
            if uid is None:
                continue  
            UserModel.update(uid, data)
            
        return jsonify({"message": "Employees updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400