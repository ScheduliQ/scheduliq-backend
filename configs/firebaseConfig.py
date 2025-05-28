# import firebase_admin 
# from firebase_admin import credentials
# import os
# from firebase_admin import auth


# # קביעת הנתיב של הקובץ
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "serviceAccountKey.json")

# # אתחול Firebase Admin SDK
# cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
# firebaseApp=firebase_admin.initialize_app(cred)


import os
import firebase_admin
from firebase_admin import credentials, auth

# 1. Read and normalize the RENDER flag from env vars
render_env = os.getenv("RENDER", "false").lower() in ("true", "1")  

# 2. Choose the correct service account path
if render_env:
    # Use Render’s Secret File mount point
    SERVICE_ACCOUNT_PATH = "/etc/secrets/serviceAccountKey.json"
else:
    # Use local file for development
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "serviceAccountKey.json")

# 3. Initialize Firebase Admin SDK
cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
firebaseApp = firebase_admin.initialize_app(cred)
