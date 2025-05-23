# from flask import Flask
# from flask_cors import CORS
# from flask_socketio import SocketIO
# from app.user_routes import user_api
# from app.auth_routes import auth_api
# from app.constraints_routes import constraints_api
# from app.algorithm_routes import alg_api
# from app.schedule_routes import schedule_api
# from app.manager_settings_routes import manager_settings_api
# from app.manager_messages_routes import manager_messages_api
# from app.reports_routes import reports_api
# from flask_mail import Mail
# from configs.envconfig import MAIL_USERNAME,MAIL_PASSWORD
# from app.notifications_routes import notifications_api
# from utils.scheduler import start_scheduler
# from configs.envconfig import PORT
# from socketio_server import socketio
# import os
# if os.getenv("FLASK_ENV") == "production":
#     import eventlet
#     eventlet.monkey_patch()

# app = Flask(__name__)
# CORS(app)
# # Mail configuration
# app.config.update(
#     MAIL_SERVER='smtp.gmail.com',          # SMTP server (Gmail's server)
#     MAIL_PORT=587,                         # Port for TLS
#     MAIL_USE_TLS=True,                     # Use TLS for security
#     MAIL_USE_SSL=False,                    # Not needed if using TLS
#     MAIL_USERNAME=MAIL_USERNAME,  # Your email address
#     MAIL_PASSWORD=MAIL_PASSWORD,   # Your email password or app-specific password
#     MAIL_DEFAULT_SENDER=('ScheduliQ', MAIL_USERNAME)  # Default sender details
# )

# mail = Mail(app)  # Initialize Flask-Mail

# # redis_url=os.getenv("REDIS_URL", "redis://redis:6379/0")
# # if os.getenv("FLASK_ENV")=="production":
# #     socketio.init_app(app, message_queue=redis_url)
# # else:
# #     socketio.init_app(app)
# socketio.init_app(app)

# app.socketio = socketio  # Attach to the app for later access in routes
# scheduler = start_scheduler()


# app.register_blueprint(user_api, url_prefix='/user')
# app.register_blueprint(auth_api,url_prefix='/auth')
# app.register_blueprint(constraints_api, url_prefix="/constraints")
# app.register_blueprint(alg_api,url_prefix='/csp')
# app.register_blueprint(schedule_api, url_prefix="/schedule")
# app.register_blueprint(manager_settings_api, url_prefix='/manager-settings')
# app.register_blueprint(manager_messages_api, url_prefix='/manager-messages')
# app.register_blueprint(notifications_api, url_prefix='/notifications')
# app.register_blueprint(reports_api, url_prefix="/reports")

# if __name__ == '__main__':
#     port = int(PORT) if PORT else 5000  # Default to 5000 if PORT is not set
    

#     # app.run(debug=True)
#     # socketio.run(app, debug=True)
#     socketio.run(app, host="0.0.0.0", port=port, debug=True, use_reloader=False)


# back/run.py
import os
if os.getenv("FLASK_ENV") == "production":
    import eventlet
    eventlet.monkey_patch()    

from flask import Flask
from flask_cors import CORS
from flask_mail import Mail
from configs.envconfig import MAIL_USERNAME, MAIL_PASSWORD, PORT
from socketio_server import socketio
from utils.scheduler import start_scheduler

# ייבוא ה-blueprints
from app.user_routes import user_api
from app.auth_routes import auth_api
from app.constraints_routes import constraints_api
from app.algorithm_routes import alg_api
from app.schedule_routes import schedule_api
from app.manager_settings_routes import manager_settings_api
from app.manager_messages_routes import manager_messages_api
from app.notifications_routes import notifications_api
from app.reports_routes import reports_api

app = Flask(__name__)
CORS(app)

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_DEFAULT_SENDER=('ScheduliQ', MAIL_USERNAME),
)

Mail(app)
start_scheduler()

socketio.init_app(app)

app.register_blueprint(user_api, url_prefix='/user')
app.register_blueprint(auth_api, url_prefix='/auth')
app.register_blueprint(constraints_api, url_prefix='/constraints')
app.register_blueprint(alg_api, url_prefix='/csp')
app.register_blueprint(schedule_api, url_prefix='/schedule')
app.register_blueprint(manager_settings_api, url_prefix='/manager-settings')
app.register_blueprint(manager_messages_api, url_prefix='/manager-messages')
app.register_blueprint(notifications_api, url_prefix='/notifications')
app.register_blueprint(reports_api, url_prefix='/reports')

if __name__ == '__main__':
    port = int(os.getenv("PORT", PORT or 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=True, use_reloader=False)
#hello its deploy test