from flask import Flask
from firebase_admin import credentials, initialize_app, firestore

def create_app():
    app = Flask(__name__)
    # Additional Flask app configurations can go here
    return app

# Initialize Firebase and Firestore
def init_firestore():
    cred = credentials.Certificate("../credentials/firebase-adminsdk.json")
    initialize_app(cred)
    return firestore.client()

# Create a global Firestore client
db = init_firestore()
