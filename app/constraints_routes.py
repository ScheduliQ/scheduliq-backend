# app/routes/constraints_routes.py
from flask import Blueprint, request, jsonify, Response
from models.constraints_model import load_draft,save_draft,create_or_update_constraint, get_constraints_by_uid, delete_constraints
from models.schemas import constraints_schema
from models.database import get_collection
# from app.middlewares.gemini_api import generate
from configs.envconfig import GEMINI_API_KEY
import google.generativeai as genai

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


@constraints_api.route("/gemini", methods=["POST"])
def chat():
    genai.configure(api_key=GEMINI_API_KEY)

    # Set the model to "gemini-1.5-flash"
    MODEL = "gemini-1.5-flash"
    # Read the free text from the request body.
    input_text = request.get_data(as_text=True)
    if not input_text:

        return Response("No input text provided", status=400)
    
    try:
        # Call the Gemini model using the google-generativeai library.
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(input_text)
    except Exception as e:
        return Response(f"Error during generation: {str(e)}", status=500)
    
    # Verify that a response was generated.
    if not response or not response.text:
        return Response("No response generated", status=500)
    
    # Return the generated text as plain text.
    return Response(response.text, mimetype='text/plain')