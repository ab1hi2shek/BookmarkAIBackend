from flask import Blueprint, jsonify, request
from functools import wraps
from datetime import datetime
import uuid
from src.utils.init import db
from src.models.tag_model import TAG_MODEL, TAG_COLLECTION, TAG_CREATOR

# Define a blueprint for the User APIs
tags_blueprint = Blueprint("tags_routes", __name__)

"""
Utility function to validate_required_fields
"""
def validate_required_fields(data, required_fields):
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    return True, ""


"""
Decorator that ensures only authorized users can access the wrapped API routes.
"""
def authorize_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = request.headers.get("userId")
        if not user_id:
            return jsonify({"error": "Unauthorized: Missing userId"}), 401
        
        """
        Check if user exists in Firestore
        Querying the Firestore database on every request is inefficient, especially for high-traffic APIs 
        or cases where the same user sends multiple requests in a short time span.

        Here are some optimized approaches to handle user authorization more efficiently:
        1. Use a Cached Authorization System: Like Redis, Memcached, or a local Python dictionary.
        2. Use a JWT-Based System (Stateless Authentication)
        """
        user_ref = db.collection("users").document(user_id).get()
        if not user_ref.exists:
            return jsonify({"error": "Unauthorized: Invalid userId"}), 401
        request.user_id = user_id  # Attach userId to the request context
        return func(*args, **kwargs)
    return wrapper

"""
API to create a tag.
"""
@tags_blueprint.route("/tag/create", methods=["POST"])
@authorize_user
def create_tag():
    try:
        data = request.json
        required_fields = ["tagName"]
        is_valid, message = validate_required_fields(data, required_fields)

        if not is_valid:
            return jsonify({"error": message}), 400

        tagId = str(uuid.uuid4())
        now = datetime.now(datetime.timezone.utc).isoformat()

        tag = TAG_MODEL.copy()
        tag.update({
            "tagId": tagId,
            "tagName": request.user_id,
            "creator": TAG_CREATOR.USER,
            "userId": data.get("title", ""),
            "createdAt": now
        })

        # Save to Firestore
        db.collection(TAG_COLLECTION).document(tagId).set(tag)

        return jsonify({"message": "Tag created successfully", "tag": tag}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


"""
API to get a tag given tag_id
"""
@tags_blueprint.route("/tag/<tag_id>", methods=["GET"])
@authorize_user
def get_tag(tag_id):
    try:
        tag_ref = db.collection(TAG_COLLECTION).document(tag_id)
        tag = tag_ref.get().to_dict()

        if not tag:
            return jsonify({"error": "Tag not found"}), 404

        if tag["userId"] != request.user_id:
            return jsonify({"error": "Unauthorized user"}), 403

        return jsonify({"tag": tag}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


"""
API to delete a tag given bookmark_id
"""
@tags_blueprint.route("/tag/<tag_id>", methods=["DELETE"])
@authorize_user
def delete_tag(tag_id):
    try:
        tag_ref = db.collection(TAG_COLLECTION).document(tag_id)
        tag = tag_ref.get().to_dict()

        if not tag:
            return jsonify({"error": "Tag not found"}), 404

        if tag["userId"] != request.user_id:
            return jsonify({"error": "Unauthorized user"}), 403

        # Delete the user document
        tag_ref.delete()

        return jsonify({"message": "Tag deleted successfully with tag_id: " + tag_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500