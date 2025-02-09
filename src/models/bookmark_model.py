BOOKMARK_COLLECTION = "bookmarks"

BOOKMARK_ID_PREFIX = "bookmark"

BOOKMARK_MODEL = {
    "bookmarkId": "", # Required
    "userId": "", # Required
    "url": "", # Required
    "imageUrl": "",
    "title": "",
    "notes": "",
    "tags": [],
    "directoryId": "directory-165ee178-7c68-4134-a2f6-9455be8ec55e",  # Default directory
    "createdAt": "",
    "updatedAt": "",
    "isDeleted": False,  # for now, implementing soft delete, "isDeleted": True, means it will not show up.
    "isFavorite": False
}