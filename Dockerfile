# # שלב בנייה
# FROM python:3.11-slim

# # הגדרת תיקיית עבודה
# WORKDIR /app

# # העתקת קובץ התלויות והתקנה
# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

# # העתקת שאר הקוד
# COPY . .

# # חשיפת פורט
# EXPOSE 5000

# # פקודת הרצה - מפעילה את run.py שמשתמש ב-socketio.run()
# CMD ["python", "run.py"]

# Dockerfile for backend with Gunicorn & Eventlet
FROM python:3.11-slim

WORKDIR /app

# Copy dependencies file and install packages including Gunicorn and Eventlet
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn eventlet

# Copy application code
COPY . .

# Expose port used by Gunicorn
EXPOSE 5000

# Run the app with Gunicorn and Eventlet
CMD ["gunicorn","-k","eventlet","-w","4","--timeout","120","--bind","0.0.0.0:5000","run:app"]
