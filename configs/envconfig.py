from dotenv import load_dotenv
import os
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
CLOUDINATY_CLOUD_NAME=os.getenv("CLOUDINATY_CLOUD_NAME")
CLOUDINATY_API_KEY=os.getenv("CLOUDINATY_API_KEY")
CLOUDINATY_API_SECRET=os.getenv("CLOUDINATY_API_SECRET")
DEBUG = True

