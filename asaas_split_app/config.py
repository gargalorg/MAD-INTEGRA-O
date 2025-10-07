# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///db.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ASAAS_API_KEY = os.getenv("ASAAS_API_KEY")
    ASAAS_BASE_URL = os.getenv("ASAAS_BASE_URL", "https://www.asaas.com/api/v3")
    # wallet environment keys (strings) are read dinamicamente no asaas_client
