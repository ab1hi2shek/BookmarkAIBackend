from flask import Blueprint, jsonify, request
from datetime import datetime
from src.utils.init import db
from src.models.tag_model import TAG_MODEL, TAG_COLLECTION, TAG_CREATOR, TAG_ID_PREFIX
from src.utils.routes_util import authorize_user, validate_required_fields, get_id, remove_tag_from_bookmarks

# Define a blueprint for the User APIs
tags_blueprint = Blueprint("tags_routes", __name__)

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

        tagId = get_id(TAG_ID_PREFIX)
        now = datetime.now(datetime.timezone.utc).isoformat()

        tag = TAG_MODEL.copy()
        tag.update({
            "tagId": tagId,
            "tagName": request.user_id,
            "creator": TAG_CREATOR.USER.value,
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
            return jsonify({"error": f"Tag not found for tag_id: {tag_id}"}), 404

        if tag["userId"] != request.user_id:
            return jsonify({"error": f"User unauthorized to delete tag with tag_id: {tag_id}"}), 403

        return jsonify({"message": "success", "tag": tag}), 200
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
            return jsonify({"error": f"Tag not found for tag_id: {tag_id}"}), 404

        if tag["userId"] != request.user_id:
            return jsonify({"error": f"User unauthorized to delete tag with tag_id: {tag_id}"}), 403
        
        # Remove tag from all bookmarks
        remove_tag_from_bookmarks(tag_id)

        # Delete the tag document
        tag_ref.delete()

        return jsonify({"message": f"Tag successfully deleted with tag_id: {tag_id}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500