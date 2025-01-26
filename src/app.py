from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app

# Firebase initialization
cred = credentials.Certificate('credentials/firebase-adminsdk.json')
initialize_app(cred)
db = firestore.client()

app = Flask(__name__)

# Models
# User Model
USER_COLLECTION = "users"
BOOKMARK_COLLECTION = "bookmarks"
TAG_COLLECTION = "tags"

# Create Bookmark
@app.route("/bookmarks", methods=["POST"])
def create_bookmark():
    bookmark_data = request.json
    bookmark_ref = db.collection(BOOKMARK_COLLECTION).document()
    bookmark_data["bookmarkId"] = bookmark_ref.id
    db.collection(BOOKMARK_COLLECTION).document(bookmark_ref.id).set(bookmark_data)
    return jsonify({"message": "Bookmark created", "bookmarkId": bookmark_ref.id}), 201

# Get All Bookmarks of a User
@app.route("/bookmarks/<user_id>", methods=["GET"])
def get_bookmarks(user_id):
    tag_filter = request.args.get("tag")
    search_value = request.args.get("search")
    bookmarks = search_bookmarks(user_id, search_value=search_value, tag_filter=tag_filter)
    return jsonify(bookmarks), 200

# Search Bookmarks
@app.route("/bookmarks/<user_id>/search", methods=["GET"])
def search_bookmarks_endpoint(user_id):
    search_value = request.args.get("search")
    tag_filter = request.args.get("tag")
    bookmarks = search_bookmarks(user_id, search_value=search_value, tag_filter=tag_filter)
    return jsonify(bookmarks), 200

# Helper Functions

def search_bookmarks(user_id, search_value=None, tag_filter=None):
    bookmarks = db.collection(BOOKMARK_COLLECTION).where("userId", "==", user_id).where("isDeleted", "==", False).stream()
    results = []

    search_terms = search_value.lower().split() if search_value else []

    for b in bookmarks:
        bookmark = b.to_dict()

        if tag_filter and not any(tag["tagName"] == tag_filter for tag in bookmark["tags"]):
            continue

        if search_terms:
            searchable_fields = [
                bookmark["title"].lower(),
                bookmark["url"].lower(),
                bookmark["notes"].lower()
            ] + [tag["tagName"].lower() for tag in bookmark["tags"]]

            if not any(term in field for term in search_terms for field in searchable_fields):
                continue

        results.append(bookmark)

    return results

if __name__ == "__main__":
    app.run(debug=True)