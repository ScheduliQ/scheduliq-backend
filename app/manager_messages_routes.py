from flask import Blueprint, jsonify, request, current_app
import datetime
from bson import ObjectId
from app.middlewares.session_middleware import verify_token
from models.manager_messages_model import ManagerMessagesModel

manager_messages_api = Blueprint('manager_messages_api', __name__, url_prefix='/manager-messages')

@manager_messages_api.route('/', methods=['GET'])
def get_20_manager_messages():
    """
    GET /manager-messages/
    Retrieve the 20 most recent manager messages (or another number via the 'limit' parameter).
    """
    limit = request.args.get('limit', default=20, type=int)
    try:
        messages = ManagerMessagesModel.get_recent(limit=limit)
        return jsonify(messages), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@manager_messages_api.route('/', methods=['POST'])
# @verify_token  # Ensure only authorized users (e.g., managers) can create messages
def create_manager_message():
    """
    POST /manager-messages/
    Create a new manager message.
    If 'created_at' is not provided, the current time is added.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        new_message = ManagerMessagesModel.create(data)
        # Emit the new message to all connected clients, excluding the sender.
        
        current_app.socketio.emit(
            'new_manager_message', 
            new_message,  
            skip_sid=data.get("sid"),
        )
        return jsonify(new_message), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@manager_messages_api.route('/update/<message_id>', methods=['PUT'])
# @verify_token
def update_manager_message(message_id):
    """
    PUT /manager-messages/update/<message_id>
    Update an existing manager message by its ID.
    """
    data = request.get_json()
    Message_id = ObjectId(message_id)
    if not data:
        return jsonify({"error": "No update data provided"}), 400

    try:
        updated_message = ManagerMessagesModel.update(Message_id, data)
        # Broadcast the updated message (excluding the sender)
        current_app.socketio.emit(
            'update_manager_message', 
            updated_message, 
            skip_sid=data.get("sid"),
        )
        return jsonify(updated_message), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@manager_messages_api.route('/delete/<message_id>', methods=['DELETE'])
# @verify_token
def delete_manager_message(message_id):
    """
    DELETE /manager-messages/delete/<message_id>
    Delete a manager message by its ID.
    """
    try:
        Message_id = ObjectId(message_id)
        success = ManagerMessagesModel.delete(Message_id)
        # Broadcast the deletion event (excluding the sender)
        current_app.socketio.emit(
            'delete_manager_message', 
            {'_id': message_id}, 
        )
        if success:
            return jsonify({"message": "Message deleted successfully"}), 200
        else:
            return jsonify({"error": "Message not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400
