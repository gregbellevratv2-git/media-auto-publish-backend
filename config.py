import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    
    # Webhook URLs (can be overridden by env vars, otherwise defaults or empty)
    LINKEDIN_WEBHOOK_URL = os.getenv("LINKEDIN_WEBHOOK_URL", "https://hook.eu2.make.com/y72rxhdivuoq9bfcwd69ztkpeifgn30p")
    INSTAGRAM_WEBHOOK_URL = os.getenv("INSTAGRAM_WEBHOOK_URL", "https://hook.eu1.make.com/0edx1p5aj72cfj61amhu1comfwu9kv9x")
    FACEBOOK_WEBHOOK_URL = os.getenv("FACEBOOK_WEBHOOK_URL", "https://hook.eu1.make.com/rj34gfj4cl9elg45jla4h9oz15lrdrpx")

settings = Settings()
