from flask import Blueprint, jsonify, request
from models.database import get_collection

api = Blueprint('api', __name__)


@api.route('/users', methods=['GET'])
def get_users():
    users_collection = get_collection('users')
    users = list(users_collection.find())  # שליפת כל המסמכים מהקולקשן
    for user in users:
        user['_id'] = str(user['_id'])  # המרה של ObjectId למחרוזת
    return jsonify(users), 200


