user_schema = {
    "uid": {"type": "string", "required": True},  # Removed 'unique'
    "email": {"type": "string", "required": True},
    "first_name": {"type": "string", "required": True},
    "last_name": {"type": "string", "required": True},
    "phone": {"type": "string", "required": True},
    "profile_picture": {"type": "string", "required": True},
    "gender": {"type": "string", "required": True},
    "jobs": {"type": "string", "required": True},  # Ensure this matches input type
    "business_id": {"type": "string", "required": True},
    "role": {"type": "string", "required": True, "default": "worker"},
    "created_at": {"type": "string", "required": True},  # Keep as string
}


# app/schemas/constraints_schema.py

constraints_schema = {
    "uid": {"type": "string", "required": True},  # מזהה ייחודי של העובד
    "first_name": {"type": "string", "required": True},  # שם העובד
    "last_name": {"type": "string", "required": True},  # שם משפחה
    "availability": {
        "type": "list", "required": True,         # רשימת משמרות
        "schema": {
            "type": "dict",                       # כל משמרת בפורמט אובייקט
            "schema": {
                "shift": {"type": "integer", "min": 0},   # מזהה המשמרת
                "day": {"type": "integer", "min": 0, "max": 6},  # יום בשבוע (0-6)
                "priority": {"type": "integer", "min": 1, "max": 10}  # עדיפות המשמרת
            }
        }
    },
    "roles": {
        "type": "list", "required": True,  # רשימת תפקידים מהדאטהבייס
        "schema": {"type": "string"}
    },
    "status": {
        "type": "string", "required": True,       # סטטוס האילוץ
        "allowed": ["active", "inactive", "not_submitted"]
    },
    "constraints": {
        "type": "string",  # שדה מחרוזת פשוט
        "required": False  # אופציונלי
    },
    "draft": {
        "type": "dict",  # טיוטה היא אובייקט
        "required": False,  # אופציונלי
        "schema": {
            "availability": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": {
                        "shift": {"type": "integer", "min": 0},
                        "day": {"type": "integer", "min": 0, "max": 6},
                        "priority": {"type": "integer", "min": 1, "max": 10}
                        }
                    }
                },
        "constraints": {"type": "string"}
        }
    },
    "last_updated": {"type": "datetime", "required": True}  # תאריך עדכון אחרון
}


manager_settings_schema = {
    "uid": {"type": "string", "required": True},
    "shifts_per_day": {"type": "integer", "required": True},
    "shift_names": {
        "type": "list",
        "schema": {"type": "string"},
        "required": True
    },
    "shift_colors": {  # שדה אופציונלי לשמירת הצבעים לכל משמרת, לדוגמה { "Morning": "#AEDFF7", ... }
        "type": "dict",
        "required": False,
        "valuesrules": {"type": "string"}
    },
    "roles_per_shift": {
        "type": "dict",
        "required": True,
        # לכל מפתח (שם משמרת) הערך הוא מסמך שממפה שם תפקיד למספר עובדים נדרש.
        "valuesrules": {
            "type": "dict",
            "valuesrules": {"type": "integer"}
        }
    },
    "max_consecutive_shifts": {"type": "integer", "required": True},
    "role_importance": {
        "type": "dict",
        "required": True,
        # לכל תפקיד מפתחים את החשיבות שלו כמספר.
        "valuesrules": {"type": "integer"}
    },
    "work_days": {
        "type": "list",
        "schema": {"type": "string"},
        "required": True
    },
    "min_max_employees_per_shift": {
        "type": "dict",
        "required": True,
        "schema": {
            "min": {"type": "integer"},
            "max": {"type": "integer"}
        }
    },
    "last_updated": {"type": "datetime", "required": False}
}


manager_messages_schema = {
    "uid": {"type": "string","required": True},
    "business_id": {"type": "string","required": True},
    "text": {"type": "string","required": True},
    "created_at": {"type": "string","required": True},
    "last_updated": {"type": "string","required": False}
}
