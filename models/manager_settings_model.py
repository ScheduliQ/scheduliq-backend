from datetime import datetime, timedelta, timezone
import random
from models.database import get_collection
from models.schemas import manager_settings_schema
from utils.validation import validate_data
# Get the collection for manager settings
manager_settings_collection = get_collection("manager_settings")

def generate_random_version(length=8) -> str:
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(random.choices(characters, k=length))

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

    if "submissionStart" in data and isinstance(data["submissionStart"], str):
        data["submissionStart"] = datetime.fromisoformat(data["submissionStart"].replace("Z", "+00:00"))
    if "submissionEnd" in data and isinstance(data["submissionEnd"], str):
        data["submissionEnd"] = datetime.fromisoformat(data["submissionEnd"].replace("Z", "+00:00"))

    # Optionally validate the incoming data against the schema.
    validated_data = validate_data(data, manager_settings_schema)
    
    # Add a timestamp for when the document was updated.
    validated_data["last_updated"] = datetime.now(timezone.utc)
    
    # Update (or insert) the unique document.
    manager_settings_collection.update_one({}, {"$set": validated_data}, upsert=True)
    constraints_collection = get_collection("constraints")
    constraints_collection.update_many({}, {"$set": {"is_final": False}})
    # Return the updated document.
    return get_manager_settings()


def transition_cycle():
    try:
        print("Transitioning cycle..........................")
        settings = get_manager_settings()  
        submission_start = settings.get("submissionStart")
        submission_end = settings.get("submissionEnd")
        # Ensure submission_start and submission_end are timezone-aware
        if isinstance(submission_start, str):
            submission_start = datetime.fromisoformat(submission_start.replace("Z", "+00:00"))
        elif submission_start and submission_start.tzinfo is None:
            submission_start = submission_start.replace(tzinfo=timezone.utc)
        if isinstance(submission_end, str):
            submission_end = datetime.fromisoformat(submission_end.replace("Z", "+00:00"))
        elif submission_end and submission_end.tzinfo is None:
            submission_end = submission_end.replace(tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        print(f"now: {now}")
        print(type(now))
        print(f"submission_start: {submission_start}")
        print(type(submission_start))
        print(f"submission_end: {submission_end}")
        print(type(submission_end))

        next_submission_start = submission_start + timedelta(days=7)
        print(f"next_submission_start: {next_submission_start}")
        
        if now >= next_submission_start:
            print("inside if..........................")
            new_active_version = generate_random_version()
            new_submission_start = submission_start + timedelta(days=7)
            new_submission_end = submission_end + timedelta(days=7)
            update_data = {
                "activeVersion": new_active_version,
                "submissionStart": new_submission_start,
                "submissionEnd": new_submission_end,
            }
            manager_settings_collection.update_one({}, {"$set": update_data}, upsert=True)
            constraints_collection = get_collection("constraints")
            constraints_collection.update_many({}, {"$set": {"is_final": False}})
    except Exception as e:
        print("Exception in transition_cycle:", e)