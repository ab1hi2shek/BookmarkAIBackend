# User Model
USER_MODEL = {
    "userId": "",
    "firstName": "",
    "lastName": "",
    "avatarUrl": "",
    "createdAt": "",
    "updatedAt": ""
}

# Bookmark Model
BOOKMARK_MODEL = {
    "bookmarkId": "",
    "userId": "",
    "url": "",
    "title": "",
    "notes": "",
    "tags": [],  # List of {"tagName": "", "creator": "user/ai"}
    "createdAt": "",
    "updatedAt": "",
    "isDeleted": False
}

# Tag Model
TAG_MODEL = {
    "tagId": "",
    "tagName": "",
    "creator": "",
    "userId": ""
}