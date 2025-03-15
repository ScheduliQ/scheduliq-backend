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

def send_contact_email(name, email, body):
    """
    Sends an email to the specified recipients with the given subject and HTML content.
    """
    custom_body = (
        "A new contact form message has been received.\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n\n"
        "Message:\n"
        f"{body}\n"
    )
    msg = Message(
        subject=f"Contact Form Message from {name}",
        sender=email,  # You can also use app.config['MAIL_DEFAULT_SENDER'] here
        recipients=[MAIL_USERNAME],
        body=custom_body
    )
    current_app.extensions['mail'].send(msg)

    