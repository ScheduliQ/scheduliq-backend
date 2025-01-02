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
