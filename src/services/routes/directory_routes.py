from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from src.utils.init import db
from src.models.bookmark_model import BOOKMARK_COLLECTION
from src.models.directory_model import DIRECTORY_COLLECTION, DIRECTORY_MODEL, DIRECTORY_ID_PREFIX, DEFAULT_DIRECTORY_NAME_AND_ID
from src.utils.routes_util import authorize_user, validate_required_fields, get_id

# Define a blueprint for the User APIs
directory_blueprint = Blueprint("directory_routes", __name__)

@directory_blueprint.route("/directory/create", methods=["POST"])
@authorize_user
def create_directory():
    try:
        data = request.json

        required_fields = ["name"]
        is_valid, message = validate_required_fields(data, required_fields)
        if not is_valid:
            return jsonify({"error": message}), 400

        directory_id = get_id(DIRECTORY_ID_PREFIX)
        time_now = int(datetime.now(timezone.utc).timestamp())

        directory = DIRECTORY_MODEL.copy()
        directory.update({
            "directoryId": directory_id,
            "userId": request.user_id,
            "name": data["name"],
            "createdAt": time_now,
            "updatedAt": time_now,
            "isDeleted": False
        })

        db.collection(DIRECTORY_COLLECTION).document(directory_id).set(directory)

        return jsonify({
            "message": "Directory created successfully",
            "data": {"directory": directory}
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@directory_blueprint.route("/directory/rename/<directory_id>", methods=["POST"])
@authorize_user
def rename_directory(directory_id):
    try:
        data = request.json
        directory_ref = db.collection(DIRECTORY_COLLECTION).document(directory_id)
        directory = directory_ref.get().to_dict()

        if not directory or directory.get("isDeleted"):
            return jsonify({"error": f"Directory not found for id: {directory_id}"}), 404

        if directory["userId"] != request.user_id:
            return jsonify({"error": "Unauthorized"}), 403

        updated_fields = {"name": data["name"], "updatedAt": int(datetime.now(timezone.utc).timestamp())}
        directory_ref.update(updated_fields)

        return jsonify({
            "message": "Directory renamed successfully",
            "data": {
                "directory" : directory
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@directory_blueprint.route("/directory/all", methods=["GET"])
@authorize_user
def get_all_directories():
    try:
        directories_query = db.collection(DIRECTORY_COLLECTION)\
            .where("userId", "==", request.user_id)\
            .where("isDeleted", "==", False)\
            .stream()

        directories = [directory.to_dict() for directory in directories_query]

                # Count bookmarks for each tag dynamically
        for directory in directories:
            directory_id = directory["directoryId"]
            bookmarks_query = db.collection(BOOKMARK_COLLECTION)\
                .where("directoryId", "==", directory_id)\
                .where("isDeleted", "==", False)\
                .stream()
            directory["bookmarksCount"] = sum(1 for _ in bookmarks_query)

        return jsonify({
            "message": "success",
            "data": {"directories": directories}
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@directory_blueprint.route("/directory/delete/<directory_id>", methods=["DELETE"])
@authorize_user
def delete_directory(directory_id):
    """
    Deletes a directory.
    - If `moveBookmarks=True`, move all bookmarks to "Uncategorized".
    - If `moveBookmarks=False`, permanently delete all bookmarks in the directory.
    """
    try:
        data = request.json
        move_bookmarks = data.get("moveBookmarks", True)  # Default is to move bookmarks

        directory_ref = db.collection(DIRECTORY_COLLECTION).document(directory_id)
        directory = directory_ref.get().to_dict()

        if not directory or directory.get("isDeleted"):
            return jsonify({"error": f"Directory not found for id: {directory_id}"}), 404

        if directory["userId"] != request.user_id:
            return jsonify({"error": "Unauthorized"}), 403

        # Mark directory as deleted
        directory_ref.update({"isDeleted": True, "updatedAt": int(datetime.now(timezone.utc).timestamp())})

        bookmarks_query = db.collection(BOOKMARK_COLLECTION).where("directoryId", "==", directory_id).stream()

        if move_bookmarks:
            # Move all bookmarks to "Uncategorized"
            for bookmark in bookmarks_query:
                bookmark.reference.update({
                    "directoryId": DEFAULT_DIRECTORY_NAME_AND_ID,
                    "updatedAt": int(datetime.now(timezone.utc).timestamp())
                })
            return jsonify({
                "message": "Directory deleted, bookmarks moved to Uncategorized",
                "data": {
                    "directory_id": directory_id,
                    "move_bookmarks": move_bookmarks,

                }
            }), 200
        else:
            # Permanently delete all bookmarks in the directory
            for bookmark in bookmarks_query:
                bookmark.reference.update({"isDeleted": True, "updatedAt": int(datetime.now(timezone.utc).timestamp())})
            return jsonify({
                "message": "Directory and all bookmarks deleted",
                "data": {
                    "directory_id": directory_id,
                    "move_bookmarks": move_bookmarks,
                    
                }
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500





