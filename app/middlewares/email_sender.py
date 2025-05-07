from flask_mail import Message
from flask import current_app
from configs.envconfig import MAIL_USERNAME
def send_email_html(recipients, subject, html_body):
    """
    Sends an email to the specified recipients with the given subject and HTML content.
    """
    msg = Message(subject, recipients=recipients, body=html_body)
    msg.html = html_body  # Set the HTML content for the email.
    current_app.extensions['mail'].send(msg)

def send_contact_email(name, email, subject, body):
    """
    Sends an email to the specified recipients with the given subject, email and HTML content.
    """
    # Create HTML version with better formatting
    html_body = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; max-width: 600px;">
        <h2 style="color: #333;">New Contact Form Message</h2>
        <p><strong>From:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>
        <p><strong>Subject:</strong> {subject}</p>
        <h3 style="margin-top: 20px; border-top: 1px solid #eee; padding-top: 15px;">Message:</h3>
        <p style="white-space: pre-line;">{body}</p>
    </div>
    """
    
    # Plain text version as fallback
    plain_body = (
        "A new contact form message has been received.\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Subject: {subject}\n\n"
        "Message:\n"
        f"{body}\n"
    )
    
    msg = Message(
        subject=f"Contact Form message from: {name}",
        sender=email,
        recipients=[MAIL_USERNAME],
        body=plain_body,
        html=html_body
    )
    current_app.extensions['mail'].send(msg)

    