from flask import Blueprint, jsonify, request
from functools import wraps
from datetime import datetime
import uuid
from src.utils.init import db
from src.models.user_model import USER_MODEL, USER_COLLECTION
from src.models.bookmark_model import BOOKMARK_COLLECTION
from src.models.tag_model import TAG_COLLECTION

# Define a blueprint for the User APIs
user_blueprint = Blueprint("user_routes", __name__)

"""
Utility function to validate required fields
"""
def validate_required_fields(data, required_fields):
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    return True, ""

"""
API to create a user.
"""
@user_blueprint.route("/user/create", methods=["POST"])
def create_user():
    try:
        data = request.json
        required_fields = ["firstName", "email"]
        is_valid, message = validate_required_fields(data, required_fields)

        if not is_valid:
            return jsonify({"error": message}), 400

        user_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        user = USER_MODEL.copy()
        user.update({
            "userId": user_id,
            "firstName": data["firstName"],
            "lastName": data.get("lastName", ""),
            "avatarUrl": data.get("avatarUrl", ""),
            "email": data.get("email"),
            "createdAt": now,
            "updatedAt": now
        })

        db.collection(USER_COLLECTION).document(user_id).set(user)

        return jsonify({"message": "User created successfully", "user": user}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

"""
API to get a user by userId
"""
@user_blueprint.route("/user/<user_id>", methods=["GET"])
def get_user(user_id):
    try:
        user_ref = db.collection(USER_COLLECTION).document(user_id)
        user = user_ref.get().to_dict()

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"message": "success", "user": user}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

"""
API to update a user by userId
"""
@user_blueprint.route("/user/<user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        data = request.json
        user_ref = db.collection(USER_COLLECTION).document(user_id)
        user = user_ref.get().to_dict()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # TODO: Validate these data.
        updated_fields = {}
        if "firstName" in data:
            updated_fields["firstName"] = data["firstName"]
        if "lastName" in data:
            updated_fields["lastName"] = data["lastName"]
        if "avatarUrl" in data:
            updated_fields["avatarUrl"] = data["avatarUrl"]
        if "email" in data:
            updated_fields["email"] = data["email"]
        updated_fields["updatedAt"] = datetime.now().isoformat()

        # Save to firehose.
        user_ref.update(updated_fields)

        user.update(updated_fields)
        return jsonify({"message": f"User updated successfully with userId: {user_id}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

"""
API to delete a user by userId and cascade delete associated bookmarks and tags
"""
@user_blueprint.route("/user/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        user_ref = db.collection(USER_COLLECTION).document(user_id)
        user = user_ref.get().to_dict()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Delete all bookmarks associated with the user
        bookmarks_query = db.collection(BOOKMARK_COLLECTION).where("userId", "==", user_id).stream()
        for bookmark in bookmarks_query:
            db.collection(BOOKMARK_COLLECTION).document(bookmark.id).delete()

        # Delete all tags associated with the user
        tags_query = db.collection(TAG_COLLECTION).where("userId", "==", user_id).stream()
        for tag in tags_query:
            db.collection(TAG_COLLECTION).document(tag.id).delete()

        # Delete the user document
        user_ref.delete()

        return jsonify({"message": f"User and associated bookmarks and tags deleted successfully\
            for userId: {user_id}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500