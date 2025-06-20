# app/routes/constraints_routes.py
from app.middlewares.gemini_service import priorityByAI
from flask import Blueprint, json, request, jsonify, Response
from models.constraints_model import load_draft,save_draft,create_or_update_constraint, get_constraints_by_uid, delete_constraints, get_all_constraints
from models.schemas import constraints_schema
from models.database import get_collection
from models.manager_settings_model import get_manager_settings
# from app.middlewares.gemini_api import generate


constraints_collection = get_collection("constraints")
constraints_api = Blueprint("constraints_api", __name__)
#route for adding or updating constarints for certain user by uid
@constraints_api.route("/", methods=["POST"])
def create_constraint():
    data = request.get_json()
    uid = data.get("uid")
    
    # אם קיימים אילוצים וזמינות, ננסה לעדכן את השדה availability
    if "constraints" in data and "availability" in data:
        try:
            data["availability"] = priorityByAI(data.get("constraints"), data.get("availability"))
            status_code = 200
        except Exception as e:
            print(f"Warning: GEMINI operation failed: {str(e)}. Proceeding with original data.")
            status_code = 201
    
    response = create_or_update_constraint(uid, data)
    return jsonify(response), status_code

# @constraints_api.route("/", methods=["POST"])
# def create_constraint():
#     data = request.get_json()
#     uid = data.get("uid")
    
#     # אם קיימים אילוצים וזמינות, נעדכן את השדה availability
#     if "constraints" in data and "availability" in data:
#         try:
#             # קריאה לפונקציה שמעדכנת את הזמינות
#             generated_list = priorityByAI(data.get("constraints"), data.get("availability"))
#             # עדכון השדה availability בנתונים
#             data["availability"] = generated_list
#         except Exception as e:
#             return jsonify({"error": f"Error during availability update: {str(e)}"}), 500
    
#     # קריאה לפונקציה create_or_update_constraint עם הנתונים המעודכנים
#     response = create_or_update_constraint(uid, data)
#     return jsonify(response), 200

#route for getting constraints by uid
@constraints_api.route("/<uid>", methods=["GET"])
def get_constraint(uid):
    constraints = get_constraints_by_uid(uid)
    if not constraints:
        return jsonify({"error": "Constraints not found"}), 404
    else:
        constraints["_id"] = str(constraints["_id"]) 
    return jsonify(constraints), 200


#route for deleting constraints by uid
@constraints_api.route("/remove/<uid>", methods=["DELETE"])
def delete_constraint(uid):
    response = delete_constraints(uid)
    return jsonify(response), 200


@constraints_api.route("/save-draft", methods=["POST"])
def save_draft_route():
    manager_settings=get_manager_settings()
    try:
        data = request.get_json()
        uid = data.get("uid")
        draft_data = {
            "availability": data.get("availability", []),
            "constraints": data.get("constraints", ""),
            "draftVersion": manager_settings.get("activeVersion", "")
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
        error_message = str(e)
        if "Draft version is outdated." in error_message:
            return jsonify({"error": error_message, "errorType": "OUTDATED"}), 403
        elif "No draft found" in error_message:
            return jsonify({"error": error_message, "errorType": "NOT_FOUND"}), 404
        else:
            return jsonify({"error": error_message, "errorType": "VALIDATION_ERROR"}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e), "errorType": "UNEXPECTED"}), 500


@constraints_api.route("/employees-constraints", methods=["GET"])
def get_employees_constraints():
    try:
        # קבלת כל האילוצים מהמסד נתונים
        all_constraints = get_all_constraints()
        
        # יצירת רשימה עם המידע הנדרש בלבד
        filtered_constraints = []
        for constraint in all_constraints:
            employee_data = {
                "first_name": constraint.get("first_name", ""),
                "last_name": constraint.get("last_name", ""),
                "constraints": constraint.get("constraints", "")
            }
            filtered_constraints.append(employee_data)
        
        return jsonify(filtered_constraints), 200
    except Exception as e:
        return jsonify({"error": "Failed to retrieve employee constraints", "details": str(e)}), 500

# @constraints_api.route("/gemini", methods=["POST"])
# def generate_priority():
#     # Parse JSON data from the request body.
#     data = request.get_json()
#     if not data or "constraints" not in data or "availability" not in data:
#         return jsonify({"error": "No 'prompt' provided"}), 400
    
#     try:
#         # Call the function to generate the Gemini response.
#         generated_text = priorityByAI(data.get("constraints"),data.get("availability"))
#     except Exception as e:
#         return jsonify({"error": f"Error during generation: {str(e)}"}), 500
    
#     # Return the generated text as JSON.
#     return jsonify({"response": generated_text}), 200