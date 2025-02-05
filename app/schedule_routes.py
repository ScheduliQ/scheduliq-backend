from flask import Blueprint, request, jsonify
from models.weekly_schedule_model import WeeklyScheduleModel

schedule_api = Blueprint("schedule_api", __name__)

@schedule_api.route("/add", methods=["POST"])
def add_schedule():
    """
    Route to add a new weekly schedule.
    """
    try:
        data = request.get_json()
        response = WeeklyScheduleModel.add_schedule(data)
        return jsonify(response), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@schedule_api.route("/remove/<schedule_id>", methods=["DELETE"])
def remove_schedule(schedule_id):
    """
    Route to remove a schedule by ID.
    """
    try:
        response = WeeklyScheduleModel.remove_schedule(schedule_id)
        return jsonify(response), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@schedule_api.route("/all", methods=["GET"])
def get_all_schedules():
    """
    Route to get all schedules sorted from latest to earliest.
    """
    try:
        schedules = WeeklyScheduleModel.get_all_schedules()
        return jsonify(schedules), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@schedule_api.route("/latest", methods=["GET"])
def get_latest_schedule():
    """
    Route to get the latest schedule.
    """
    try:
        latest_schedule = WeeklyScheduleModel.get_latest_schedule()
        if latest_schedule:
            return jsonify(latest_schedule), 200
        return jsonify({"message": "No schedules found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500