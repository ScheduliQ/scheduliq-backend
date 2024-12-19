from flask import Blueprint, jsonify, request
from models.database import get_collection
from firebase_admin import auth
from configs.firebaseConfig import firebaseApp  # לאתחול חד-פעמי

auth_api = Blueprint('auth_api', __name__)
users_collection=get_collection('users')

#Register User
@auth_api.route("/register-user", methods=["POST"])  # יצירת נתיב API עם HTTP POST
def register_user():
    try:
        id_token = request.headers.get("Authorization").split(" ")[1]
        decoded = auth.verify_id_token(id_token)
        email = request.json["email"]
        # בדיקה האם המשתמש כבר קיים במסד הנתונים (לפי ה-uid מ-Firebase)
        if users_collection.find_one({"uid": decoded["uid"]}):
            return jsonify({"message": "User already exists"}), 201  # תגובה במידה והמשתמש קיים
        # שמירת המשתמש החדש ב-MongoDB עם מידע רלוונטי
        new_user = {
            "uid": decoded["uid"],  # מזהה ייחודי מה-Firebase
            "email": email,  # כתובת המייל שנשלחה
            "created_at": decoded["auth_time"],  # זמן ההרשמה שנשלף מה-Token
            "role":"worker",
        }
        users_collection.insert_one(new_user)  # הוספת המשתמש למסד הנתונים
        print(new_user)
        # תגובה חזרה ל-Frontend עם הודעת הצלחה
        return jsonify({"message": "User registered successfully"}), 201
    
    except Exception as e:
        print("Error:", str(e))
        # טיפול בשגיאות במקרה של כישלון באימות או בעיות אחרות
        return jsonify({"error": str(e)}), 401

