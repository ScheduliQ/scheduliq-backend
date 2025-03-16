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

        # Validate user data
        validated_user = validate_data(user_data, user_schema)

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
    
    @staticmethod
    def get_all_employee_emails():
        """
        Retrieve email addresses for all employees (users with role 'worker').
        Returns:
            list: A list of email strings.
        """
        # Query the users collection for documents where role equals "worker"
        employees = UserModel.collection.find({"role": "worker"}, {"email": 1})
        emails = [user["email"] for user in employees if "email" in user]
        return emails
    @staticmethod
    def get_all_employees():
        """
        Retrieve all employees (users with role 'worker').
        
        Returns:
            list: A list of employee dictionaries.
        """
        # Query the users collection for documents where role equals "worker"
        employees_cursor = UserModel.collection.find({"role": "worker"})
        employees = []
        for employee in employees_cursor:
            employee["_id"] = str(employee["_id"])  # Convert ObjectId to string
            employees.append(employee)
        return employees