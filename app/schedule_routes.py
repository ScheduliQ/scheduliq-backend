from flask import Blueprint, app, request, jsonify
from app.middlewares.gemini_service import chat_with_manager
from models.weekly_schedule_model import WeeklyScheduleModel
import traceback


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
    
@schedule_api.route('/update/<schedule_id>', methods=['PUT'])
def update_schedule_route(schedule_id):
    data = request.get_json()
    if not data or 'days' not in data:
        return jsonify({"error": "Missing 'days' field in request body"}), 400

    new_days = data['days']
    result = WeeklyScheduleModel.update_schedule(schedule_id, new_days)
    
    if 'error' in result:
        return jsonify(result),400
    return jsonify(result),200

import traceback
from flask import request, jsonify

@schedule_api.route("/chatbot", methods=["POST"])
def chat():
    # ▶️ Log raw payload
    data = request.get_json()
    print(f"[chatbot] Received payload: {data}")

    if not data or "message" not in data or "first_message" not in data:
        print("[chatbot] Bad request – missing 'message' or 'first_message'")
        return jsonify({"error": "Missing 'message' or 'first_message'"}), 400

    manager_message = data["message"]
    first_message = data["first_message"]
    print(f"[chatbot] manager_message='{manager_message}', first_message={first_message}")

    try:
        reply = chat_with_manager(manager_message, first_message)
        print("[chatbot] Reply generated successfully")
        return jsonify({"response": reply}), 200

    except Exception as e:
        # ▶️ קבלת ה-traceback המלא
        tb = traceback.format_exc()
        print(f"[chatbot] Exception occurred:\n{tb}")
        # ▶️ החזרת השגיאה + traceback בתגובה
        return jsonify({
            "error": str(e),
            "traceback": tb
        }), 500