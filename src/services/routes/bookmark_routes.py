from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from src.utils.init import db
from src.models.bookmark_model import BOOKMARK_MODEL, BOOKMARK_COLLECTION, BOOKMARK_ID_PREFIX
from src.models.tag_model import TAG_COLLECTION
from src.utils.routes_util import authorize_user, validate_required_fields, get_id, process_tags, fetch_tag_names

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
        time_now = datetime.now(timezone.utc).isoformat()

        # Handle tags
        tag_ids = process_tags(data.get("tags", []), request.user_id)

        bookmark = BOOKMARK_MODEL.copy()
        bookmark.update({
            "bookmarkId": bookmark_id,
            "userId": request.user_id,
            "url": data["url"],
            "imageUrl": data.get("imageUrl", ""),
            "title": data.get("title", ""),
            "notes": data.get("notes", ""),
            "tags": tag_ids,
            "createdAt": time_now,
            "updatedAt": time_now,
            "isDeleted": False,
            "isFavorite": False
        })

        # Save to Firestore
        db.collection(BOOKMARK_COLLECTION).document(bookmark_id).set(bookmark)

        return jsonify({
            "message": "Bookmark created successfully", 
            "data": {
                "bookmark": bookmark
            }
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


"""
API to get a bookmark given bookmark_id
"""
@bookmark_blueprint.route("/bookmark/get/<bookmark_id>", methods=["GET"])
@authorize_user
def get_bookmark(bookmark_id):
    try:
        bookmark_ref = db.collection(BOOKMARK_COLLECTION).document(bookmark_id)
        bookmark = bookmark_ref.get().to_dict()

        if not bookmark or bookmark.get("isDeleted"):
            return jsonify({"error": f"Bookmark not found for bookmark_id: {bookmark_id}"}), 404

        if bookmark["userId"] != request.user_id:
            return jsonify({"error": f"User unauthorized to get bookmark with bookmark_id: {bookmark_id}"}), 403

        return jsonify({
            "message": "success", 
            "data": {
                "bookmark": bookmark
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



"""
API to update a bookmark given bookmark_id
"""
@bookmark_blueprint.route("/bookmark/update/<bookmark_id>", methods=["POST"])
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
            print(data.get("tags", []))
            if not isinstance(data["tags"], list):
                return jsonify({"error": f"Tags provided in request must be a list"}), 400
            # Handle tags
            tag_ids = process_tags(data.get("tags", []), request.user_id)
            updated_fields["tags"] = tag_ids
        updated_fields["updatedAt"] = datetime.now(timezone.utc).isoformat()

        # Save to Firestore
        bookmark_ref.update(updated_fields)

        # Fetch tag names dynamically
        tag_names = fetch_tag_names(updated_fields.get("tags", []))

        # Update in-memory bookmark for the response
        bookmark.update(updated_fields)
        bookmark["tags"] = tag_names

        return jsonify({
            "message": "Bookmark updated successfully", 
            "data": {
                "bookmark": bookmark
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


"""
API to delete a bookmark given bookmark_id
"""
@bookmark_blueprint.route("/bookmark/delete/<bookmark_id>", methods=["DELETE"])
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
        bookmark["updatedAt"] = datetime.now(timezone.utc).isoformat()
        bookmark_ref.set(bookmark)

        return jsonify({
            "message": "Bookmark deleted successfully", 
            "data": {
                "bookmarkId": bookmark_id
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
"""
API to set a bookmark as favorite (or remove) given bookmark_id
"""
@bookmark_blueprint.route("/bookmark/favorite/<bookmark_id>", methods=["POST"])
@authorize_user
def toggle_favorite(bookmark_id):
    try:
        bookmark_ref = db.collection(BOOKMARK_COLLECTION).document(bookmark_id)
        bookmark = bookmark_ref.get().to_dict()

        if not bookmark or bookmark.get("isDeleted"):
            return jsonify({"error": f"Bookmark not found for bookmark_id: {bookmark_id}"}), 404

        if bookmark["userId"] != request.user_id:
            return jsonify({"error": f"User unauthorized to update bookmark with bookmark_id: {bookmark_id}"}), 403

        # Update Firestore document
        bookmark["isFavorite"] = not bookmark["isFavorite"]
        bookmark["updatedAt"] = datetime.now(timezone.utc).isoformat()
        bookmark_ref.set(bookmark)

        return jsonify({
            "message": "Bookmark favorite set", 
            "data": {
                "bookmarkId": bookmark_id,
                "isFavorite": bookmark['isFavorite']
            }
        }), 200
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

        # Fetch all tags for the user in a single query
        tags_query = db.collection(TAG_COLLECTION).where("userId", "==", request.user_id).stream()
        tag_map = {tag.id: tag.to_dict()["tagName"] for tag in tags_query}  # 🔹 Convert to {tagId: tagName} dict

        if tags_filter:
            if match_type == "AND":
                # Filter bookmarks that contain all tags
                bookmarks = [b for b in bookmarks if all(tag in b.get("tags", []) for tag in tags_filter)]
            elif match_type == "OR":
                # Filter bookmarks that contain at least one tag
                bookmarks = [b for b in bookmarks if any(tag in b.get("tags", []) for tag in tags_filter)]

        # 🔹 Replace tag IDs with tag names
        for bookmark in bookmarks:
            bookmark["tags"] = [tag_map[tag_id] for tag_id in bookmark["tags"] if tag_id in tag_map]

        return jsonify({
            "message": "success", 
            "data": {
                "bookmarks": bookmarks
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500