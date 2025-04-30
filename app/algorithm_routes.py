
from flask import Blueprint, request, jsonify
# from app.algorithm.csp_algoritm import solve_schedule
from tasks import generate_schedule

alg_api = Blueprint("alg_api", __name__)


@alg_api.route("/generate-schedule", methods=["POST"])
def enqueue_schedule():
    # grab the socket ID from the incoming JSON
    data = request.get_json() or {}
    socket_id = data.get("socket_id")
    if not socket_id:
        return jsonify({"error": "socket_id is required"}), 400

    # enqueue the background job
    task = generate_schedule.delay(socket_id)

    # immediately return a 202 so the browser stays responsive
    return jsonify({
        "status": "queued",
        "task_id": task.id
    }), 202