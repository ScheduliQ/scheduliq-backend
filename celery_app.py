import os
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery = Celery(
    "tasks",
    broker=redis_url,
    backend=redis_url,
)
