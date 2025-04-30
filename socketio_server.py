# import os, eventlet;
# from flask_socketio import SocketIO

# socketio = SocketIO(
#   cors_allowed_origins="*",
#   message_queue=os.getenv("REDIS_URL", "redis://redis:6379/0"),
#   async_mode="eventlet",
# )


import os
import eventlet
eventlet.monkey_patch()

from flask_socketio import SocketIO

# רק ב-PROD יש message_queue, ב-DEV = לא מוגדר
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
mq = REDIS_URL if os.getenv("FLASK_ENV") == "production" else None

socketio = SocketIO(
    cors_allowed_origins="*",
    message_queue=mq,
    async_mode="eventlet",
)