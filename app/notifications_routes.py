import datetime
from flask import Blueprint, current_app, request, jsonify
from models.notifications_model import (
    create_global_notification,
    get_last_notifications,
    get_unread_count_for_user,
    mark_all_as_read_for_user
)

notifications_api = Blueprint("notifications_api", __name__)

# def serialize_notification(notification):
#     """ ממיר את תאריך ה־datetime למחרוזת """
#     serialized = notification.copy()
#     if isinstance(serialized.get("createdAt"), datetime):
#         serialized["createdAt"] = serialized["createdAt"].isoformat()
#     return serialized

@notifications_api.route("/create", methods=["POST"])
def create_notification_route():
    """
    This route creates a new notification in the system.
    The data should include:
      - message: The text of the notification
      - data: (optional) Additional data
    After creating the notification, it will be saved in the database and sent in real-time to all employees via Socket.IO.
    """
    data = request.get_json()
    message = data.get("message")
    extra_data = data.get("data", "")

    if not message:
        return jsonify({"error": "Missing required fields: 'message' are required"}), 400

    notification = create_global_notification(message, extra_data)
    tosend= {
        "notification": {
                "_id": str(notification["_id"]),
                "message": notification["message"],
                "data": notification["data"]
            },
    }
    print("Sending notification to all employees:", tosend)

    current_app.socketio.emit("notification", tosend,skip_sid=data.get("uid"), )

    return jsonify(notification), 201

@notifications_api.route("/get_all/<user_id>", methods=["GET"])
def get_global_notifications(user_id):
    """
    This route returns the last 5 notifications along with the count of unread notifications for the user.
    The user provides their UID in the URL, and the system performs the following:
      - Retrieves the last notifications (sorted by createdAt in descending order)
      - Counts the unread notifications (where the user is not present in the read_by array)
    The response returns a JSON object with two fields: notifications and unread_count.
    """
    notifications = get_last_notifications()
    unread_count = get_unread_count_for_user(user_id)
    return jsonify({
        "notifications": notifications,
        "unread_count": unread_count
    }), 200

@notifications_api.route("/mark_read/<user_id>", methods=["PUT"])
def mark_notifications_read(user_id):
    """
    This route marks all notifications as read for the user.
    The operation is performed by updating all documents (where the user is not present in the read_by array) and adding the user's UID.
    After the update, the response returns the number of documents that were updated.
    """
    modified_count = mark_all_as_read_for_user(user_id)
    return jsonify({
        "message": "Notifications marked as read",
        "modified_count": modified_count
        }), 200
