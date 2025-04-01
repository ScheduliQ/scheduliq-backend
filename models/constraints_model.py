# models/constraints_model.py
from datetime import datetime, timezone
from models.database import get_collection
from models.manager_settings_model import get_manager_settings
from utils.validation import validate_data
from models.schemas import constraints_schema


constraints_collection = get_collection("constraints")
users_collection = get_collection("users")
def create_or_update_constraint(uid, data):
    data["last_updated"] = datetime.now(timezone.utc)
    data["status"] = "active"
    user = users_collection.find_one({"uid": uid},{"jobs": 1, "first_name": 1, "last_name": 1})
    data["first_name"]=user["first_name"] 
    data["last_name"]=user["last_name"] 
    data["roles"] = user["jobs"].split(",") if user and "jobs" in user else []
    settings = get_manager_settings()
    data["version"] = settings.get("activeVersion")
    data["is_final"] = True
    validate_data(data, constraints_schema)

    constraints_collection.update_one(
        {"uid": uid},
        {"$set": data},
        upsert=True
    )
    return {"message": "Constraint created/updated successfully"}

def get_constraints_by_uid(uid):
    return constraints_collection.find_one({"uid": uid})

def delete_constraints(uid):
    constraints_collection.delete_one({"uid": uid})
    return {"message": "Constraint deleted successfully"}


def save_draft(uid, draft_data):
    try:
        constraints_collection.update_one(
            {"uid": uid},
            {"$set": {"draft": draft_data}},
            upsert=True
        )
        return {"message": "Draft saved successfully"}
    except Exception as e:
        raise ValueError(f"Failed to save draft: {str(e)}")


def load_draft(uid):
    settings = get_manager_settings()
    current_version = settings.get("activeVersion")
    try:
        constraint = constraints_collection.find_one({"uid": uid}, {"draft": 1,"draftVersion": 1})  
        if constraint and "draft" in constraint:

            if constraint.get("draft").get("draftVersion") != current_version:
                raise ValueError("Draft version is outdated. Please update the draft.")
            return {"draft": constraint["draft"]}
        raise ValueError("No draft found")

    except Exception as e:
        raise ValueError(str(e))
    

def get_all_constraints():
    return constraints_collection.find()

