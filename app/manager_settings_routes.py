from flask import Blueprint, request, jsonify
from models.manager_settings_model import get_manager_settings, update_manager_settings

manager_settings_api = Blueprint("manager_settings_api", __name__)

@manager_settings_api.route("/", methods=["GET"])
def get_settings():
    settings = get_manager_settings()
    if settings:
        return jsonify(settings), 200
    return jsonify({"error": "Manager settings not found"}), 404

@manager_settings_api.route("/", methods=["POST", "PUT"])
def update_settings():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    try:
        updated_settings = update_manager_settings(data)
        return jsonify(updated_settings), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
