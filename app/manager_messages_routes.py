from flask import Blueprint, jsonify, request, current_app
import datetime
from bson import ObjectId
from app.middlewares.email_sender import send_urgent_email
from app.middlewares.session_middleware import verify_token
from models.manager_messages_model import ManagerMessagesModel
from models.user_model import UserModel 

manager_messages_api = Blueprint('manager_messages_api', __name__, url_prefix='/manager-messages')

@manager_messages_api.route('/', methods=['GET'])
def get_20_manager_messages():
    """
    GET /manager-messages/
    Retrieve the 20 most recent manager messages (or another number via the 'limit' parameter).
    """
    limit = request.args.get('limit', default=20, type=int)
    try:
        messages = ManagerMessagesModel.get_recent(limit=limit)
        return jsonify(messages), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@manager_messages_api.route('/', methods=['POST'])
# @verify_token  # Ensure only authorized users (e.g., managers) can create messages
def create_manager_message():
    """
    POST /manager-messages/
    Create a new manager message.
    If 'created_at' is not provided, the current time is added.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        new_message = ManagerMessagesModel.create(data)
        # Emit the new message to all connected clients, excluding the sender.
        if new_message.get("priority") == "urgent":
            employee_emails = UserModel.get_all_employee_emails()
            subject = "URGENT: System Alert Notification"
            html_body = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Urgent System Notification</title>
                    <style>
                        body, html {{
                            margin: 0;
                            padding: 0;
                            font-family: Arial, Helvetica, sans-serif;
                            line-height: 1.6;
                        }}
                        
                        .email-container {{
                            max-width: 600px;
                            margin: 0 auto;
                            background-color: #ffffff;
                            border-radius: 8px;
                            border: 1px solid #e2e8f0;
                        }}
                        
                        .email-header {{
                            background-color: #1a3d7c;  /* Deep blue */
                            color: #ffffff;
                            padding: 25px 20px;
                            text-align: center;
                            border-radius: 8px 8px 0 0;
                        }}
                        
                        .logo {{
                            display: inline-block;
                            margin-bottom: 10px;
                        }}
                        
                        .logo-text {{
                            font-size: 28px;
                            font-weight: bold;
                            color: #ffffff;
                        }}
                        
                        .email-body {{
                            padding: 30px 20px;
                        }}
                        
                        .email-title {{
                            font-size: 24px;
                            font-weight: bold;
                            color: #1e293b;
                            margin-bottom: 20px;
                            padding-bottom: 15px;
                            border-bottom: 1px solid #e2e8f0;
                        }}
                        
                        .email-content {{
                            font-size: 16px;
                            color: #1e293b;
                            margin-bottom: 25px;
                        }}
                        
                        .message-box {{
                            background-color: #f1f5f9;
                            border-left: 4px solid #1a3d7c;  /* Deep blue border */
                            padding: 20px;
                            margin: 20px 0;
                        }}
                        
                        .message-header {{
                            font-weight: bold;
                            font-size: 18px;
                            color: #15315e;  /* A deeper accent blue */
                            margin-bottom: 10px;
                        }}
                        
                        .notification-badge {{
                            display: inline-block;
                            background-color: #ef4444;
                            color: #ffffff;
                            border-radius: 50px;
                            padding: 4px 12px;
                            font-size: 14px;
                            font-weight: bold;
                            margin-left: 8px;
                        }}
                        
                        .message-content {{
                            font-size: 16px;
                            color: #1e293b;
                        }}
                        
                        .action-button {{
                            display: inline-block;
                            background-color: #1a3d7c;  /* Deep blue */
                            color: #ffffff;
                            padding: 12px 24px;
                            border-radius: 6px;
                            text-decoration: none;
                            font-weight: bold;
                            margin: 20px 0;
                        }}
                        
                        .email-footer {{
                            background-color: #f1f5f9;
                            padding: 20px;
                            text-align: center;
                            color: #64748b;
                            font-size: 14px;
                            border-top: 1px solid #e2e8f0;
                            border-radius: 0 0 8px 8px;
                        }}
                        
                        .company-info {{
                            margin-bottom: 10px;
                        }}
                        
                        table {{
                            border-collapse: collapse;
                            width: 100%;
                        }}
                        
                        td {{
                            vertical-align: top;
                        }}
                        
                        p {{
                            margin: 0 0 15px 0;
                        }}
                    </style>
                </head>
                <body>
                    <table cellpadding="0" cellspacing="0" border="0" width="100%" bgcolor="#f8fafc">
                        <tr>
                            <td align="center" style="padding: 40px 0;">
                                <table cellpadding="0" cellspacing="0" border="0" width="600" class="email-container">
                                    <!-- Header -->
                                    <tr>
                                        <td align="center" bgcolor="#1a3d7c" style="padding: 25px 20px; border-radius: 8px 8px 0 0;">
                                            <div class="logo-text" style="font-size: 28px; font-weight: bold; color: #ffffff;">
                                                ScheduliQ
                                            </div>
                                        </td>
                                    </tr>
                                    
                                    <!-- Body -->
                                    <tr>
                                        <td style="padding: 30px 20px;">
                                            <div style="text-align: left;">
                                                <h1 style="font-size: 24px; font-weight: bold; color: #1e293b; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #e2e8f0;">
                                                    Urgent System Notification
                                                </h1>
                                                
                                                <p style="font-size: 16px; color: #1e293b; margin-bottom: 15px;">Dear Employee,</p>
                                                <p style="font-size: 16px; color: #1e293b; margin-bottom: 15px;">We would like to inform you that a new urgent system message has been posted:</p>
                                                
                                                <div style="background-color: #f1f5f9; border-left: 4px solid #1a3d7c; padding: 20px; margin: 20px 0;">
                                                    <div style="font-weight: bold; font-size: 18px; color: #15315e; margin-bottom: 10px;">
                                                        System Update
                                                        <span style="display: inline-block; background-color: #ef4444; color: #ffffff; border-radius: 50px; padding: 4px 12px; font-size: 14px; font-weight: bold; margin-left: 8px;">Urgent</span>
                                                    </div>
                                                    <div style="font-size: 16px; color: #1e293b;">
                                                        <p>{new_message.get('text')}</p>
                                                    </div>
                                                </div>
                                                
                                                <p style="font-size: 16px; color: #1e293b; margin-bottom: 15px;">Please check the system dashboard for further details.</p>
                                                
                                                <a href="#" style="display: inline-block; background-color: #1a3d7c; color: #ffffff; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: bold; margin: 20px 0;">Access System</a>
                                            </div>
                                        </td>
                                    </tr>
                                    
                                    <!-- Footer -->
                                    <tr>
                                        <td align="center" bgcolor="#f1f5f9" style="padding: 20px; border-top: 1px solid #e2e8f0; border-radius: 0 0 8px 8px;">
                                            <div style="margin-bottom: 10px; color: #64748b; font-size: 14px;">
                                                <strong>ScheduliQ</strong>
                                            </div>
                                            <div style="color: #64748b; font-size: 14px;">
                                                © 2025 ScheduliQ, All Rights Reserved
                                            </div>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                </body>
                </html>
                """


            send_urgent_email(employee_emails, subject, html_body)
            
        current_app.socketio.emit(
            'new_manager_message', 
            new_message,  
            skip_sid=data.get("sid"),
        )
        return jsonify(new_message), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@manager_messages_api.route('/update/<message_id>', methods=['PUT'])
# @verify_token
def update_manager_message(message_id):
    """
    PUT /manager-messages/update/<message_id>
    Update an existing manager message by its ID.
    """
    data = request.get_json()
    Message_id = ObjectId(message_id)
    if not data:
        return jsonify({"error": "No update data provided"}), 400

    try:
        updated_message = ManagerMessagesModel.update(Message_id, data)
        # Broadcast the updated message (excluding the sender)
        current_app.socketio.emit(
            'update_manager_message', 
            updated_message, 
            skip_sid=data.get("sid"),
        )
        return jsonify(updated_message), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@manager_messages_api.route('/delete/<message_id>', methods=['DELETE'])
# @verify_token
def delete_manager_message(message_id):
    """
    DELETE /manager-messages/delete/<message_id>
    Delete a manager message by its ID.
    """
    try:
        Message_id = ObjectId(message_id)
        success = ManagerMessagesModel.delete(Message_id)
        # Broadcast the deletion event (excluding the sender)
        current_app.socketio.emit(
            'delete_manager_message', 
            {'_id': message_id}, 
        )
        if success:
            return jsonify({"message": "Message deleted successfully"}), 200
        else:
            return jsonify({"error": "Message not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400
