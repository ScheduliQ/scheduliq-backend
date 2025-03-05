from datetime import datetime, timezone
from models.database import get_collection
from models.schemas import manager_settings_schema
from utils.validation import validate_data

# Get the collection for manager settings
manager_settings_collection = get_collection("manager_settings")

def get_manager_settings():
    """
    Retrieve the single manager settings document.
    """
    settings = manager_settings_collection.find_one({})
    if settings:
        settings["_id"] = str(settings["_id"])
    return settings

def update_manager_settings(data: dict):
    """
    Update (or create) the unique manager settings document.
    The 'uid' is used only to record which manager made the last change.
    This function automatically sets 'shifts_per_day' as the length of 'shift_names'.
    """
    # Automatically set 'shifts_per_day' to the length of 'shift_names'
    if "shift_names" in data:
        data["shifts_per_day"] = len(data["shift_names"])
    
    # Optionally validate the incoming data against the schema.
    validated_data = validate_data(data, manager_settings_schema)
    
    # Add a timestamp for when the document was updated.
    validated_data["last_updated"] = datetime.now(timezone.utc)
    
    # Update (or insert) the unique document.
    manager_settings_collection.update_one({}, {"$set": validated_data}, upsert=True)
    
    # Return the updated document.
    return get_manager_settings()
