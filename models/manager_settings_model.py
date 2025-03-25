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
    
    # Return the updated document.
    return get_manager_settings()


# דוגמה לפונקציה שמחשבת מעבר למחזור חדש
def transition_cycle():
    # שליפת ההגדרות הנוכחיות ממסד הנתונים
    settings = get_manager_settings()  # פונקציה קיימת שמשיגה את מסמך ההגדרות
    submission_start = settings.get("submissionStart")
    submission_end = settings.get("submissionEnd")
    
    # המרה לאובייקט datetime אם השדות הגיעו כמחרוזת
    if isinstance(submission_start, str):
        submission_start = datetime.fromisoformat(submission_start.replace("Z", "+00:00"))
    if isinstance(submission_end, str):
        submission_end = datetime.fromisoformat(submission_end.replace("Z", "+00:00"))
    
    now = datetime.now(timezone.utc)
    
    # חישוב תחילת המחזור הבא - נניח שהמחזור משתנה בדיוק ביום ראשון הבא,
    # כלומר, נוסיף 7 ימים לערך הקיים של submissionStart
    next_submission_start = submission_start + timedelta(days=7)
    
    if now >= next_submission_start:
        # יצירת activeVersion חדש
        new_active_version = generate_random_version()
        # עדכון טווח ההגשה למחזור הבא - נוסיף 7 ימים גם ל-submissionStart וגם ל-submissionEnd
        new_submission_start = submission_start + timedelta(days=7)
        new_submission_end = submission_end + timedelta(days=7)
        update_data = {
            "activeVersion": new_active_version,
            "submissionStart": new_submission_start,
            "submissionEnd": new_submission_end,
            "last_updated": datetime.now(timezone.utc)
        }
        manager_settings_collection.update_one({}, {"$set": update_data}, upsert=True)
        # print(f"Cycle transitioned: New activeVersion: {new_active_version}")
        # print(f"New submission window: {new_submission_start} to {new_submission_end}")
    # else:
    #     print("Cycle transition not required yet.")