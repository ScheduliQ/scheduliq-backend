from models.database import get_collection
from utils.validation import validate_data
from models.schemas import manager_messages_schema

class ManagerMessagesModel:
    collection = get_collection("manager_messages")

    @staticmethod
    def create(message_data):
        """
        Validate and insert a new manager message into the database.

        Args:
            message_data (dict): Data for the new manager message.

        Returns:
            dict: Inserted manager message data.

        Raises:
            ValueError: If validation fails.
        """
        # כאן הפונקציה validate_data בודקת את הנתונים לפי הסכמה ומחזירה dict עם כל השדות
        validated_message = validate_data(message_data, manager_messages_schema)
        result = ManagerMessagesModel.collection.insert_one(validated_message)
        validated_message["_id"] = str(result.inserted_id)
        return validated_message

    @staticmethod
    def get_recent(limit=20):
        """
        Retrieve the most recent manager messages.

        Args:
            limit (int): Number of messages to retrieve (default is 20).

        Returns:
            list: List of messages sorted by created_at descending.
        """
        messages_cursor = ManagerMessagesModel.collection.find().sort("created_at", -1).limit(limit)
        messages = []
        for message in messages_cursor:
            message["_id"] = str(message["_id"])
            messages.append(message)
        return messages

    @staticmethod
    def update(uid, update_data):
        """
        Update an existing manager message.

        Args:
            uid (str): The manager's unique identifier.
            update_data (dict): The data to update.

        Returns:
            dict: The updated manager message document.

        Raises:
            ValueError: If the manager message does not exist.
        """
        result = ManagerMessagesModel.collection.find_one_and_update(
            {"_id": uid},
            {"$set": update_data},
            return_document=True  # במידה ואתה משתמש ב-pymongo>=3.7, אפשר להשתמש ב-return_document
        )
        if result:
            result["_id"] = str(result["_id"])
            return result
        raise ValueError("Manager message not found")

    @staticmethod
    def delete(uid):
        """
        Delete a manager message by the manager's UID.

        Args:
            uid (str): The manager's unique identifier.

        Returns:
            bool: True if the manager message was deleted, False otherwise.
        """
        result = ManagerMessagesModel.collection.delete_one({"_id": uid})
        return result.deleted_count > 0
