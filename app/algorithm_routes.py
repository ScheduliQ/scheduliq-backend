
from flask import Blueprint, request, jsonify
from app.algorithm.csp_algoritm import solve_schedule


alg_api = Blueprint("alg_api", __name__)


@alg_api.route("/generate-schedule", methods=["GET"])
def get_schedule():
    result = solve_schedule()  # returns a tuple: (formatted_json, text_output_split)
    if result:
        formatted_json, text_output = result
        return jsonify({
            "solution": formatted_json,
            "text": text_output
        }), 200
    return jsonify({"error": "No feasible solution found"}), 400


