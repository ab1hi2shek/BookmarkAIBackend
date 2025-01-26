from flask import Blueprint, jsonify, request
from src.utils.init import db  # Use the globally initialized Firestore client
from src.models.model import BOOKMARK_MODEL

# Define a blueprint for the User APIs
bookmark_blueprint = Blueprint("bookmark_routes", __name__)