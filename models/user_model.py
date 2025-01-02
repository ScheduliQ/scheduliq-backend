from models.database import get_collection
from utils.validation import validate_data
from models.schemas import user_schema


class UserModel:
    collection = get_collection("users")

    @staticmethod
    def create(user_data):
        """
        Validate and insert a new user into the database.

        Args:
            user_data (dict): Data for the new user.

        Returns:
            dict: Inserted user data.

        Raises:
            ValueError: If validation fails.
        """
        print("User data before validation:", user_data)

        # Validate user data
        validated_user = validate_data(user_data, user_schema)
        print("Validated user data:", validated_user)
        print("Attempting to insert user into database:", validated_user)

        # Insert into the database
        result = UserModel.collection.insert_one(validated_user)

        # Return the inserted user with the MongoDB-generated ID
        validated_user["_id"] = str(result.inserted_id)
        return validated_user

    @staticmethod
    def find_by_uid(uid):
        """
        Find a user by their UID.

        Args:
            uid (str): The user's unique identifier.

        Returns:
            dict: The user document, or None if not found.
        """
        user = UserModel.collection.find_one({"uid": uid})
        if user:
            user["_id"] = str(user["_id"])  # Convert ObjectId to string
        return user

    @staticmethod
    def update(uid, update_data):
        """
        Update an existing user's data.

        Args:
            uid (str): The user's unique identifier.
            update_data (dict): The data to update.

        Returns:
            dict: The updated user document.

        Raises:
            ValueError: If the user does not exist.
        """
        # Find and update the user
        result = UserModel.collection.find_one_and_update(
            {"uid": uid}, {"$set": update_data}, return_document=True
        )
        if result:
            result["_id"] = str(result["_id"])  # Convert ObjectId to string
            return result
        raise ValueError("User not found")

    @staticmethod
    def delete(uid):
        """
        Delete a user by their UID.

        Args:
            uid (str): The user's unique identifier.

        Returns:
            bool: True if the user was deleted, False otherwise.
        """
        result = UserModel.collection.delete_one({"uid": uid})
        return result.deleted_count > 0