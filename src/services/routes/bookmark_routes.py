from flask import Blueprint, jsonify, request
from functools import wraps
from datetime import datetime
from src.utils.init import db
import uuid
from src.models.bookmark_model import BOOKMARK_MODEL, BOOKMARK_COLLECTION
from src.utils.routes_util import authorize_user, validate_required_fields

# Define a blueprint for the User APIs
bookmark_blueprint = Blueprint("bookmark_routes", __name__)

"""
API to create a bookmark.
"""
@bookmark_blueprint.route("/bookmark/create", methods=["POST"])
@authorize_user
def create_bookmark():
    try:
        data = request.json
        required_fields = ["url"]
        is_valid, message = validate_required_fields(data, required_fields)

        if not is_valid:
            return jsonify({"error": message}), 400

        bookmark_id = str(uuid.uuid4())
        now = datetime.now(datetime.timezone.utc).isoformat()

        bookmark = BOOKMARK_MODEL.copy()
        bookmark.update({
            "bookmarkId": bookmark_id,
            "userId": request.user_id,
            "url": data["url"],
            "title": data.get("title", ""),
            "notes": data.get("notes", ""),
            "tags": data.get("tags", []),
            "createdAt": now,
            "updatedAt": now,
            "isDeleted": False
        })

        # Save to Firestore
        db.collection(BOOKMARK_COLLECTION).document(bookmark_id).set(bookmark)

        return jsonify({"message": "Bookmark created successfully", "bookmark": bookmark}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


"""
API to get a bookmark given bookmark_id
"""
@bookmark_blueprint.route("/bookmark/<bookmark_id>", methods=["GET"])
@authorize_user
def get_bookmark(bookmark_id):
    try:
        bookmark_ref = db.collection(BOOKMARK_COLLECTION).document(bookmark_id)
        bookmark = bookmark_ref.get().to_dict()

        if not bookmark or bookmark.get("isDeleted"):
            return jsonify({"error": "Bookmark not found"}), 404

        if bookmark["userId"] != request.user_id:
            return jsonify({"error": "Unauthorized user"}), 403

        return jsonify({"bookmark": bookmark}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



"""
API to update a bookmark given bookmark_id
"""
@bookmark_blueprint.route("/bookmark/<bookmark_id>", methods=["POST"])
@authorize_user
def update_bookmark(bookmark_id):
    try:
        data = request.json
        bookmark_ref = db.collection(BOOKMARK_COLLECTION).document(bookmark_id)
        bookmark = bookmark_ref.get().to_dict()

        if not bookmark or bookmark.get("isDeleted"):
            return jsonify({"error": "Bookmark not found"}), 404

        if bookmark["userId"] != request.user_id:
            return jsonify({"error": "Unauthorized"}), 403

        # Collect only fields that need to be updated
        updated_fields = {}
        if "title" in data:
            updated_fields["title"] = data["title"]
        if "notes" in data:
            updated_fields["notes"] = data["notes"]
        if "tags" in data:
            if not isinstance(data["tags"], list):
                return jsonify({"error": "Tags must be a list"}), 400
            updated_fields["tags"] = data["tags"]
        updated_fields["updatedAt"] = datetime.now(datetime.timezone.utc).isoformat()

        # Save to Firestore
        bookmark_ref.update(updated_fields)

        # Update in-memory bookmark for the response
        bookmark.update(updated_fields)

        return jsonify({"message": "Bookmark updated successfully", "bookmark": bookmark}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


"""
API to delete a bookmark given bookmark_id
"""
@bookmark_blueprint.route("/bookmark/<bookmark_id>", methods=["DELETE"])
@authorize_user
def delete_bookmark(bookmark_id):
    try:
        bookmark_ref = db.collection(BOOKMARK_COLLECTION).document(bookmark_id)
        bookmark = bookmark_ref.get().to_dict()

        if not bookmark or bookmark.get("isDeleted"):
            return jsonify({"error": "Bookmark not found"}), 404

        if bookmark["userId"] != request.user_id:
            return jsonify({"error": "Unauthorized user"}), 403

        # Update Firestore document
        bookmark["isDeleted"] = True
        bookmark["updatedAt"] = datetime.now(datetime.timezone.utc).isoformat()
        bookmark_ref.set(bookmark)

        return jsonify({"message": "Bookmark deleted successfully with bookmark_id: " + bookmark_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

"""
API to get bookmarks given tag. This API matches for AND operator of all tags.
"""
@bookmark_blueprint.route("/bookmark/filter", methods=["POST"])
@authorize_user
def filter_bookmarks():
    try:
        data = request.json
        tags_filter = data.get("tags", [])
        match_type = data.get("match", "AND").upper()  # "AND" or "OR", with default as "AND"

        bookmarks_query = db.collection(BOOKMARK_COLLECTION)\
            .where("userId", "==", request.user_id)\
            .where("isDeleted", "==", False)
        bookmarks = [doc.to_dict() for doc in bookmarks_query.stream()]

        if tags_filter:
            if match_type == "AND":
                # Filter bookmarks that contain all tags
                bookmarks = [b for b in bookmarks if all(tag in b.get("tags", []) for tag in tags_filter)]
            elif match_type == "OR":
                # Filter bookmarks that contain at least one tag
                bookmarks = [b for b in bookmarks if any(tag in b.get("tags", []) for tag in tags_filter)]

        return jsonify({"bookmarks": bookmarks}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500