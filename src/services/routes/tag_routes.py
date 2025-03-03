from flask import Blueprint, jsonify, request
import traceback
from datetime import datetime, timezone
from src.utils.init import db
from src.models.tag_model import TAG_MODEL, TAG_COLLECTION, TAG_CREATOR, TAG_ID_PREFIX
from src.models.bookmark_model import BOOKMARK_COLLECTION
from src.utils.routes_util import authorize_user, validate_required_fields, get_id, remove_tag_from_all_bookmarks
from src.utils.tagGeneration.generate_tags import generate_tags

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
        now = int(datetime.now(timezone.utc).timestamp())

        tag = TAG_MODEL.copy()
        tag.update({
            "tagId": tagId,
            "tagName": data["tagName"],
            "creator": TAG_CREATOR.USER.value,
            "userId": request.user_id,
            "createdAt": now
        })

        # Save to Firestore
        db.collection(TAG_COLLECTION).document(tagId).set(tag)

        return jsonify({
            "message": "Tag created successfully", 
            "data": {
                "tag": tag
            }
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


"""
API to get a tag given tag_id
"""
@tags_blueprint.route("/tag/get/<tag_id>", methods=["GET"])
@authorize_user
def get_tag(tag_id):
    try:
        tag_ref = db.collection(TAG_COLLECTION).document(tag_id)
        tag = tag_ref.get().to_dict()

        if not tag:
            return jsonify({"error": f"Tag not found for tag_id: {tag_id}"}), 404

        if tag["userId"] != request.user_id:
            return jsonify({"error": f"User unauthorized to delete tag with tag_id: {tag_id}"}), 403

        return jsonify({
            "message": "success", 
            "data": {
                "tag": tag
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500
    

"""
API to get all tags for a user
"""
@tags_blueprint.route("/tag/all", methods=["GET"])
@authorize_user
def get_all_tags():
    try:
        tags_query = db.collection(TAG_COLLECTION).where("userId", "==", request.user_id).stream()
        tags = [tag.to_dict() for tag in tags_query]

        # Count bookmarks for each tag dynamically
        for tag in tags:
            tag_id = tag["tagId"]
            bookmarks_query = db.collection(BOOKMARK_COLLECTION)\
                .where("tags", "array_contains", tag_id)\
                .where("isDeleted", "==", False)\
                .stream()
            tag["bookmarksCount"] = sum(1 for _ in bookmarks_query)

        return jsonify({
            "message": "success", 
            "data": {
                "tags": tags
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500
    

"""
API to update a tag
"""
@tags_blueprint.route("/tag/update/<tag_id>", methods=["POST"])
@authorize_user
def update_tag(tag_id):
    try:
        data = request.json
        tag_ref = db.collection(TAG_COLLECTION).document(tag_id)
        tag = tag_ref.get().to_dict()

        if not tag:
            return jsonify({"error": f"Tag not found for tag_id: {tag_id}"}), 404
        if tag["userId"] != request.user_id:
            return jsonify({"error": f"User unauthorized to delete tag with tag_id: {tag_id}"}), 403
        
        required_fields = ["tagName"]
        is_valid, message = validate_required_fields(data, required_fields)
        if not is_valid:
            return jsonify({"error": message}), 400
        
        updated_fields = {}
        if "tagName" in data:
            updated_fields["tagName"] = data["tagName"]
            # Change creator to user if user is updating the generated tag name.
            if tag["creator"] == TAG_CREATOR.SERVICE.value:
                updated_fields["creator"] = TAG_CREATOR.USER.value
        updated_fields["updatedAt"] = int(datetime.now(timezone.utc).timestamp())
        
        # Save to firehose.
        tag_ref.update(updated_fields)
        tag.update(updated_fields)

        return jsonify({
            "message": "Tag updated successfully", 
            "data": {
                "tag_id": tag_id
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


"""
API to delete a tag given bookmark_id
"""
@tags_blueprint.route("/tag/delete/<tag_id>", methods=["DELETE"])
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
        remove_tag_from_all_bookmarks(tag_id)

        # Delete the tag document
        tag_ref.delete()

        return jsonify({
            "message": "Tag successfully deleted", 
            "data": {
                "tag_id": tag_id
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500
    

"""
API to get AI generated tags for user
"""
@tags_blueprint.route("/tag/generate", methods=["POST"])
@authorize_user
def generated_ai_tags():
    try:
        data = request.json
        required_fields = ["bookmarkId"]
        is_valid, message = validate_required_fields(data, required_fields)

        if not is_valid:
            return jsonify({"error": message}), 400
        
        bookmark_id = data["bookmarkId"]
        bookmark_ref = db.collection(BOOKMARK_COLLECTION).document(bookmark_id)
        bookmark = bookmark_ref.get().to_dict()

        # If tag already exists, return it.
        if len(bookmark.get("generatedTags", [])) != 0:
            return jsonify({
                "message": "Tags already exist", 
                "data": {
                    "generatedTags": bookmark["generatedTags"]
                }
            }), 200

        tags_query = db.collection(TAG_COLLECTION).where("userId", "==", request.user_id).stream()
        allUserTags = [tag.to_dict() for tag in tags_query]
        generatedTags = generate_tags(bookmark, allUserTags)

        updated_fields = {}
        updated_fields["generatedTags"] = generatedTags
        bookmark_ref.update(updated_fields)

        return jsonify({
            "message": "Tags successfully generated and saved", 
            "data": {
                "generatedTags": generatedTags
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500