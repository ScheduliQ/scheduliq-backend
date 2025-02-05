
from flask import Blueprint, request, jsonify
from app.algorithm.csp_algoritm import solve_schedule


alg_api = Blueprint("alg_api", __name__)


@alg_api.route("/generate-schedule", methods=["GET"])
def get_schedule():
    schedule_json = solve_schedule()
    if schedule_json:
        return jsonify(schedule_json), 200
    return jsonify({"error": "No feasible solution found"}), 400



