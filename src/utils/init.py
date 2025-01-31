import os
import json
from flask import Flask
from firebase_admin import credentials, initialize_app, firestore

# Check if running on Vercel
ON_VERCEL = os.getenv("VERCEL") == "1"

def create_app():
    app = Flask(__name__)
    # Additional Flask app configurations can go here
    return app

# Initialize Firebase and Firestore
def init_firestore():
    if ON_VERCEL:
        # Running on Vercel: Load credentials from environment variable
        firebase_creds = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
        cred = credentials.Certificate(firebase_creds)
    else:
     # Running Locally: Load from file
        cred = credentials.Certificate("credentials_firebase/firebase-adminsdk.json")
    initialize_app(cred)
    return firestore.client()

# Create a global Firestore client
db = init_firestore()
