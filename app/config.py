import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///store_monitoring.db")
