from flask import Blueprint, jsonify, request
from datetime import datetime
from src.utils.init import db
from src.models.bookmark_model import BOOKMARK_MODEL, BOOKMARK_COLLECTION, BOOKMARK_ID_PREFIX
from src.models.tag_model import TAG_COLLECTION, TAG_CREATOR, TAG_ID_PREFIX
from src.utils.routes_util import authorize_user, validate_required_fields, get_id

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

        bookmark_id = get_id(BOOKMARK_ID_PREFIX)
        time_now = datetime.now(datetime.timezone.utc).isoformat()

        # Handle tags
        tag_names = data.get("tags", []),
        tag_ids = []
        for tag_name in tag_names:
            # Check if tag exists for the user
            tag_query = db.collection(TAG_COLLECTION).where("tagName", "==", tag_name).where("userId", "==", request.user_id).get()
            if tag_query:
                # Tag exists
                tag_id = tag_query[0].id
            else:
                # Create new tag
                tag_id = get_id(TAG_ID_PREFIX)
                tag_data = {
                    "tagId": tag_id,
                    "tagName": tag_name,
                    "creator": TAG_CREATOR.USER.value,
                    "userId": request.user_id,
                    "createdAt": time_now
                }
                db.collection(TAG_COLLECTION).document(tag_id).set(tag_data)
            tag_ids.append(tag_id)


        bookmark = BOOKMARK_MODEL.copy()
        bookmark.update({
            "bookmarkId": bookmark_id,
            "userId": request.user_id,
            "url": data["url"],
            "title": data.get("title", ""),
            "notes": data.get("notes", ""),
            "tags": tag_ids,
            "createdAt": time_now,
            "updatedAt": time_now,
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
            return jsonify({"error": f"Bookmark not found for bookmark_id: {bookmark_id}"}), 404

        if bookmark["userId"] != request.user_id:
            return jsonify({"error": f"User unauthorized to get bookmark with bookmark_id: {bookmark_id}"}), 403

        return jsonify({"message": "success", "bookmark": bookmark}), 200
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
            return jsonify({"error": f"Bookmark not found for bookmark_id: {bookmark_id}"}), 404

        if bookmark["userId"] != request.user_id:
            return jsonify({"error": f"User unauthorized to update bookmark with bookmark_id: {bookmark_id}"}), 403

        # Collect only fields that need to be updated
        updated_fields = {}
        if "title" in data:
            updated_fields["title"] = data["title"]
        if "notes" in data:
            updated_fields["notes"] = data["notes"]
        if "tags" in data:
            if not isinstance(data["tags"], list):
                return jsonify({"error": f"Tags provided in request must be a list"}), 400
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
            return jsonify({"error": f"Bookmark not found for bookmark_id: {bookmark_id}"}), 404

        if bookmark["userId"] != request.user_id:
            return jsonify({"error": f"User unauthorized to update bookmark with bookmark_id: {bookmark_id}"}), 403

        # Update Firestore document
        bookmark["isDeleted"] = True
        bookmark["updatedAt"] = datetime.now(datetime.timezone.utc).isoformat()
        bookmark_ref.set(bookmark)

        return jsonify({"message": f"Bookmark deleted successfully with bookmark_id: {bookmark_id}"}), 200
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

        return jsonify({"message": "success", "bookmarks": bookmarks}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500