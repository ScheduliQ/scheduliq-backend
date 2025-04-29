# שלב בנייה
FROM python:3.11-slim

# הגדרת תיקיית עבודה
WORKDIR /app

# העתקת קובץ התלויות והתקנה
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# העתקת שאר הקוד
COPY . .

# חשיפת פורט
EXPOSE 5000

# פקודת הרצה - מפעילה את run.py שמשתמש ב-socketio.run()
CMD ["python", "run.py"]
