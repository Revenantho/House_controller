import os

from dotenv import load_dotenv

load_dotenv()

SESSION_SECRET_KEY = os.environ.get("SESSION_SECRET_KEY", "dev-only-insecure-secret")
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./domotique.db")
