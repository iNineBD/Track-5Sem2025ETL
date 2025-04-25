# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis do .env

TAIGA_HOST = os.getenv("TAIGA_HOST", "http://localhost:9000/")
TAIGA_USER = os.getenv("TAIGA_USER", "admin")
TAIGA_PASSWORD = os.getenv("TAIGA_PASSWORD", "admin")
DATABASE_URL = os.getenv("DATABASE_URL")
