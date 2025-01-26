from flask import Blueprint, jsonify, request
from src.utils.init import db
from src.models.user_model import USER_MODEL, USER_COLLECTION
from datetime import datetime
import uuid

user_blueprint = Blueprint("user_routes", __name__)

# Helper function to check for a required field in user api request
def check_for_required_fields(user_data, field_name):
    if not user_data.get("userId", "").strip():
        return jsonify({"error": "userId is required"}), 400
    if not user_data.get("firstName", "").strip():
        return jsonify({"error": "firstName is required"}), 400

"""
API to create user.
"""
@user_blueprint.route("/user", methods=["POST"])
def create_user():
    try:
        user_data = request.get_json()
        if not user_data:
            return jsonify({"error": "No data provided"}), 400
        
        # Check for required fields.
        check_for_required_fields(user_data)

        # Create user_data_as_per_model dict by taking missing values from model definition.
        create_user_data = {key: user_data.get(key, USER_MODEL[key]) for key in USER_MODEL}
        
        # Save to Firestore
        user_ref = db.collection(USER_COLLECTION).document(create_user_data["userId"])
        user_ref.set(create_user_data)

        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


"""
API to get user.
"""
@user_blueprint.route("/user/<user_id>", methods=["GET"])
def get_user(user_id):
    try:
        user_ref = db.collection(USER_COLLECTION).document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return jsonify({"error": "User not found with user_id " + user_id}), 404

        return jsonify(user_doc.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


"""
API to update user.
"""
@user_blueprint.route("/user/<user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        user_data = request.get_json()
        if not user_data:
            return jsonify({"error": "No data provided"}), 400

        user_ref = db.collection(USER_COLLECTION).document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists():
            return jsonify({"error": "User not found with user_id " + user_id}), 404
        
        # Check for required fields.
        check_for_required_fields(user_data)

        # Create user_data_as_per_model dict by taking missing values from model definition.
        update_user_data = {key: user_data.get(key, USER_MODEL[key]) for key in USER_MODEL}

        # Update Firestore document
        user_ref.update(update_user_data)

        return jsonify({"message": "User updated successfully with user_id " + user_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


"""
API to delete user.
"""
@user_blueprint.route("/user/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        user_ref = db.collection(USER_COLLECTION).document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists():
            return jsonify({"error": "User not found with user_id " + user_id}), 404

        # Delete the user document
        user_ref.delete()

        return jsonify({"message": "User deleted successfully with user_id " + user_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
