from models.database import get_collection
from datetime import datetime, timezone
from bson.objectid import ObjectId

class WeeklyScheduleModel:
    collection = get_collection("weekly_schedule")
    MAX_DOCUMENTS = 16

    @staticmethod
    def add_schedule(data):
        """
        Add a new weekly schedule. If more than MAX_DOCUMENTS exist, remove the earliest one.
        """
        # Add a timestamp for sorting purposes
        data["created_at"] = datetime.now(timezone.utc)
        
        # Insert the new schedule
        result = WeeklyScheduleModel.collection.insert_one(data)
        
        # Ensure we do not exceed MAX_DOCUMENTS
        if WeeklyScheduleModel.collection.count_documents({}) > WeeklyScheduleModel.MAX_DOCUMENTS:
            oldest = WeeklyScheduleModel.collection.find().sort("created_at", 1).limit(1)
            WeeklyScheduleModel.collection.delete_one({"_id": oldest["_id"]})
        
        return {"message": "Schedule added successfully", "id": str(result.inserted_id)}

    @staticmethod
    def remove_schedule(schedule_id):
        """
        Remove a schedule by ID.
        """
        print("remove_schedule")
        result = WeeklyScheduleModel.collection.delete_one({"_id": ObjectId(schedule_id)})
        
        if result.deleted_count == 0:
            return {"error": "Schedule not found"}, 404
        
        return {"message": "Schedule removed successfully"}

    @staticmethod
    def get_all_schedules():
        """
        Get all schedules sorted from latest to earliest.
        """
        schedules = list(WeeklyScheduleModel.collection.find().sort("created_at", -1).limit(16))

        for schedule in schedules:
            schedule["_id"] = str(schedule["_id"])  # Convert ObjectId to string
            schedule["created_at"] = schedule["created_at"].isoformat()  # Convert datetime to string
        
        return schedules

    @staticmethod
    def get_latest_schedule():
        """
        Get the latest schedule based on created_at timestamp.
        """
        latest_schedule = WeeklyScheduleModel.collection.find_one(sort=[("created_at", -1)])
        
        if latest_schedule:
            latest_schedule["_id"] = str(latest_schedule["_id"])  # Convert ObjectId to string
            latest_schedule["created_at"] = latest_schedule["created_at"].isoformat()  # Convert datetime to string
        
        return latest_schedule
    
    @staticmethod
    def update_schedule(schedule_id, new_days):
        """
        Update the 'days' field of a schedule identified by schedule_id.
        """
        result = WeeklyScheduleModel.collection.update_one(
            {"_id": ObjectId(schedule_id)},
            {"$set": {"days": new_days}}
        )
        if result.modified_count == 0:
            return {"error": "Schedule not found or no changes made"}
        return {"message": "Schedule updated successfully"}