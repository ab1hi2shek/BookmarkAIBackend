from flask import jsonify, request
from functools import wraps
from src.utils.init import db
import uuid
from datetime import datetime, timezone
from src.models.user_model import USER_COLLECTION
from src.models.bookmark_model import BOOKMARK_COLLECTION
from src.models.tag_model import TAG_CREATOR, TAG_COLLECTION, TAG_ID_PREFIX
from src.utils.tagGeneration.fetch_page_content import fetch_page_content
from src.utils.tagGeneration.generate_tags import generate_tags
import traceback

"""
Decorator that ensures only authorized users can access the wrapped API routes.
"""
def authorize_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = request.headers.get("userId")
        if not user_id:
            return jsonify({"error": "Unauthorized Access: Missing userId in header"}), 401
        
        """
        Check if user exists in Firestore
        Querying the Firestore database on every request is inefficient, especially for high-traffic APIs 
        or cases where the same user sends multiple requests in a short time span.

        Here are some optimized approaches to handle user authorization more efficiently:
        1. Use a Cached Authorization System: Like Redis, Memcached, or a local Python dictionary.
        2. Use a JWT-Based System (Stateless Authentication)
        """
        user_ref = db.collection(USER_COLLECTION).document(user_id).get()
        if not user_ref.exists:
            return jsonify({"error": "Unauthorized Access: Invalid userId provided"}), 401
        request.user_id = user_id  # Attach userId to the request context
        return func(*args, **kwargs)
    return wrapper


"""
Utility function to validate_required_fields
"""
def validate_required_fields(data, required_fields):
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    return True, ""


"""
Get unique UUID4 with given prefix.
"""
def get_id(prefix):
    return prefix + "-" + str(uuid.uuid4())


"""
    Process tag names to get or create tag IDs.

    Args:
        tags (list): List of tag names.
        user_id (str): The ID of the user creating/updating the bookmark.

    Returns:
        list: List of tag IDs corresponding to the tag names.

    Raises:
        ValueError: If `tag_names` is not a list or is missing.
    """
def process_tags(tags, user_id):
    if not isinstance(tags, list):
        raise ValueError("Tags must be a list.")

    time_now = int(datetime.now(timezone.utc).timestamp())
    tag_ids = []

    for tag_name in tags:
        # Check if tag exists for the user
        tag_query = db.collection(TAG_COLLECTION)\
            .where("tagName", "==", tag_name)\
            .where("userId", "==", user_id)\
            .get()
        if tag_query:
            # Tag exists
            tag_id = tag_query[0].id
        else:
            # Create new tag
            tag_id = get_id(TAG_ID_PREFIX)
            tag_data = {
                "tagId": tag_id,
                "tagName": tag_name,
                "creator": TAG_CREATOR.USER.value, # TODO - Different types of tag handling
                "userId": user_id,
                "createdAt": time_now
            }
            # Add a new tag to the db
            db.collection(TAG_COLLECTION).document(tag_id).set(tag_data)
        
        tag_ids.append(tag_id)

    return tag_ids


"""
Remove tag from bookmark. If a bookmark have only input tag, delete the bookmark.
"""
def remove_tag_from_all_bookmarks(tag_id):
    bookmarks_query = db.collection(BOOKMARK_COLLECTION)\
        .where("userId", "==", request.user_id)\
        .where("tags", "array_contains", tag_id)
    
    for bookmark_doc in bookmarks_query.stream():
        bookmark = bookmark_doc.to_dict()
        updated_tags = [tid for tid in bookmark["tags"] if tid != tag_id]

        if not updated_tags:
            # If no tags left, delete the bookmark
            bookmark_doc.reference.update({"isDeleted": True})
        else:
            # Update tags
            bookmark_doc.reference.update({"tags": updated_tags})


def fetch_tag_names(tag_ids):
    """Fetch tag names from Firestore based on tag IDs"""
    if not tag_ids:
        return []

    tag_docs = db.collection(TAG_COLLECTION).where("tagId", "in", tag_ids).stream()
    return [tag_doc.to_dict().get("tagName", "") for tag_doc in tag_docs if tag_doc.exists]


def async_process_bookmark_creation(bookmark_id, url, user_id):
    """Background task to fetch page content, generate tags, and update bookmark."""
    try:
        print("🔄 Background processing started...")

        # Fetch page content
        page_content = fetch_page_content(url)

        # Get user tags
        tags_query = db.collection(TAG_COLLECTION).where("userId", "==", user_id).stream()
        allUserTags = [tag.to_dict() for tag in tags_query]

        # Generate AI tags
        generatedTags = generate_tags(
            5, # generate 5 number of tags when bookmark is created
            url, 
            page_content["title"],
            page_content["content"], 
            allUserTags
        )

        # Process tags and get tag IDs
        tag_ids = process_tags(generatedTags, user_id)

        # Update Firestore with generated tags & fetched content
        db.collection(BOOKMARK_COLLECTION).document(bookmark_id).update({
            "imageUrl": page_content["image"],
            "title": page_content["title"],
            "generatedTags": generatedTags,
            "tags": tag_ids,
            "updatedAt": int(datetime.now(timezone.utc).timestamp()),
        })
        
        print(f"✅ Background processing completed for {bookmark_id}")

    except Exception as e:
        print(f"❌ Error in async process: {str(e)}")
        print(traceback.format_exc())