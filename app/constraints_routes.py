# app/routes/constraints_routes.py
from flask import Blueprint, request, jsonify
from models.constraints_model import load_draft,save_draft,create_or_update_constraint, get_constraints_by_uid, delete_constraints
from models.schemas import constraints_schema
from models.database import get_collection

constraints_collection = get_collection("constraints")
constraints_api = Blueprint("constraints_api", __name__)
#route for adding or updating constarints for certain user by uid
@constraints_api.route("/", methods=["POST"])
def create_constraint():
    data = request.get_json()
    uid = data.get("uid")
    response = create_or_update_constraint(uid, data)
    return jsonify(response), 200


#route for getting constraints by uid
@constraints_api.route("/<uid>", methods=["GET"])
def get_constraint(uid):
    constraints = get_constraints_by_uid(uid)
    if not constraints:
        return jsonify({"error": "Constraints not found"}), 404
    else:
        constraints["_id"] = str(constraints["_id"])  # המרת ObjectId למחרוזת
    return jsonify(constraints), 200


#route for deleting constraints by uid
@constraints_api.route("/remove/<uid>", methods=["DELETE"])
def delete_constraint(uid):
    response = delete_constraints(uid)
    return jsonify(response), 200


@constraints_api.route("/save-draft", methods=["POST"])
def save_draft_route():
    try:
        data = request.get_json()
        uid = data.get("uid")
        draft_data = {
            "availability": data.get("availability", []),
            "constraints": data.get("constraints", "")
        }
        response = save_draft(uid, draft_data)
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@constraints_api.route("/draft/<uid>", methods=["GET"])
def load_draft_route(uid):
    try:
        response = load_draft(uid)
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
