from flask import Blueprint, jsonify, request
import datetime
from bson import ObjectId
from app.middlewares.session_middleware import verify_token
from models.manager_messages_model import ManagerMessagesModel

manager_messages_api = Blueprint('manager_messages_api', __name__, url_prefix='/manager_messages')

@manager_messages_api.route('/', methods=['GET'])
def get_20_manager_messages():
    """
    GET /manager_messages/
    שליפת 20 ההודעות האחרונות (או מספר אחר לפי הפרמטר limit).
    """
    limit = request.args.get('limit', default=20, type=int)
    try:
        messages = ManagerMessagesModel.get_recent(limit=limit)
        return jsonify(messages), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@manager_messages_api.route('/', methods=['POST'])
# @verify_token  # וודא שרק משתמשים מורשים (למשל מנהלים) יכולים ליצור הודעות
def create_manager_message():
    """
    POST /manager_messages/
    יצירת הודעה חדשה.
    אם לא נשלח שדה created_at, מתווסף הזמן הנוכחי.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # if 'created_at' not in data:
    #     data['created_at'] = datetime.datetime.utcnow()
    
    try:
        new_message = ManagerMessagesModel.create(data)
        return jsonify(new_message), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@manager_messages_api.route('/update/<message_id>', methods=['PUT'])
# @verify_token
def update_manager_message(message_id):
    """
    PUT /manager_messages/update/<message_id>
    עדכון הודעה קיימת לפי המזהה (message_id).
    """
    data = request.get_json()
    Message_id = ObjectId(message_id)
    if not data:
        return jsonify({"error": "No update data provided"}), 400

    try:
        updated_message = ManagerMessagesModel.update(Message_id, data)
        return jsonify(updated_message), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@manager_messages_api.route('/delete/<message_id>', methods=['DELETE'])
# @verify_token
def delete_manager_message(message_id):
    """
    DELETE /manager_messages/delete/<message_id>
    מחיקת הודעה לפי המזהה (message_id).
    """
    try:
        Message_id = ObjectId(message_id)
        success = ManagerMessagesModel.delete(Message_id)
        if success:
            return jsonify({"message": "Message deleted successfully"}), 200
        else:
            return jsonify({"error": "Message not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400
