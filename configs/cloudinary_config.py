import cloudinary
from configs.envconfig import CLOUDINATY_CLOUD_NAME,CLOUDINATY_API_KEY,CLOUDINATY_API_SECRET

# Configure Cloudinary
cloudinary.config(
    cloud_name=CLOUDINATY_CLOUD_NAME, 
    api_key=CLOUDINATY_API_KEY,        
    api_secret=CLOUDINATY_API_SECRET 
)
