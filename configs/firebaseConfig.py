import firebase_admin 
from firebase_admin import credentials
import os
from firebase_admin import auth


# קביעת הנתיב של הקובץ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "serviceAccountKey.json")

# אתחול Firebase Admin SDK
cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
firebaseApp=firebase_admin.initialize_app(cred)
