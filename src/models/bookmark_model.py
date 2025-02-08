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
    "directoryId": "uncategorized",  # Default directory
    "createdAt": "",
    "updatedAt": "",
    "isDeleted": False,  # for now, implementing soft delete, "isDeleted": True, means it will not show up.
    "isFavorite": False
}