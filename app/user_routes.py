from flask import Blueprint, jsonify, request
from models.database import get_collection
from app.middlewares.session_middleware import verify_token

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