from models.database import get_collection
from datetime import datetime, timezone
from models.schemas import notifications_schema

from utils.validation import validate_data

# גישה לאוסף ההתראות במונגו
notifications_collection = get_collection("notifications")

def create_global_notification( message, data=None):
    """
    Creates a global notification in the system.
    Each notification is stored in a document with the following fields:
      - type: The type of notification (e.g., "new_shift", "deadline_alert", "manager_settings_update")
      - message: The text of the notification
      - data: Additional data (if any)
      - createdAt: The creation date of the notification (UTC)
      - read_by: An array of user IDs who marked the notification as read (default is empty)
    """
    count = notifications_collection.count_documents({})
    if count >= 5:
        # Find the oldest document by createdAt (sort in ascending order and take the first one)
        oldest = list(notifications_collection.find({}).sort("createdAt", 1).limit(1))
        if oldest:
            notifications_collection.delete_one({"_id": oldest[0]["_id"]})
    
    # Creating the notification
    notification = {
        "message": message,
        "data": data or "",
        "createdAt": datetime.now(timezone.utc),
        "read_by": []  # בתחילה אף משתמש לא סימן את ההתראה כנקראה
    }
    
    # Validation (assuming you have a validate_data function and a notifications_schema)
    validated_message = validate_data(notification, notifications_schema)
    result = notifications_collection.insert_one(validated_message)
    notification["_id"] = str(result.inserted_id)
    return notification

def get_last_notifications():
    """
    Returns the last `limit` (default is 5) notifications, sorted from newest to oldest.
    """
    notifications = list(notifications_collection.find({}).sort("createdAt", -1))
    for notif in notifications:
        notif["_id"] = str(notif["_id"])
    return notifications

def get_unread_count_for_user(user_id):
    """
    Counts the number of unread notifications for a given user.
    The condition is that the user does not appear in the "read_by" array of the notification.
    """
    count = notifications_collection.count_documents({"read_by": {"$ne": user_id}})
    return count

def mark_all_as_read_for_user(user_id):
    """
    מסמן את כל ההתראות כנקראות עבור המשתמש על ידי הוספת מזהה המשתמש למערך "read_by" בכל מסמך בו הוא אינו קיים.
    """
    result = notifications_collection.update_many(
        {"read_by": {"$ne": user_id}},
        {"$push": {"read_by": user_id}}
    )
    return result.modified_count
