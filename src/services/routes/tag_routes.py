from flask import Blueprint, jsonify, request
from src.utils.init import db  # Use the globally initialized Firestore client
from src.models.model import TAG_MODEL

# Define a blueprint for the User APIs
tags_blueprint = Blueprint("tags_routes", __name__)