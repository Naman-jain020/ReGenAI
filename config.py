import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', 'serviceAccountKey.json')
    FIREBASE_PROJECT_ID=os.getenv('FIREBASE_PROJECT_ID', 'medicalrecoverysystem')
    FIREBASE_STORAGE_BUCKET=os.getenv('FIREBASE_STORAGE_BUCKET', 'medicalrecoverysystem.appspot.com')
    FIREBASE_CONFIG = {
        "apiKey": os.getenv('FIREBASE_API_KEY'),
        "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN'),
        "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        "appId": os.getenv('FIREBASE_APP_ID')
    }
    SECRET_KEY = os.getenv('SECRET_KEY') or 'dev-key-123'