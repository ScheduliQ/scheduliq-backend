# import os
# from celery import Celery

# redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

# celery = Celery(
#     "tasks",
#     broker=redis_url,
#     backend=redis_url,
#     include=["tasks"]
# )


# back/celery_app.py
import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks"],    # נתיב מלא ל־tasks.py
)

# ב-DEV נפעיל eager mode (ריצה בסנכרון, בלי צורך ב-worker)
if os.getenv("FLASK_ENV") != "production":
    celery.conf.task_always_eager = True
