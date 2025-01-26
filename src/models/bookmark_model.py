BOOKMARK_COLLECTION = "bookmarks"

BOOKMARK_ID_PREFIX = "bookmark"

BOOKMARK_MODEL = {
    "bookmarkId": "", # Required
    "userId": "", # Required
    "url": "", # Required
    "title": "",
    "notes": "",
    "tags": [],
    "createdAt": "", # Set by service code.
    "updatedAt": "", # Set by service code.
    "isDeleted": False  # for now, implementing soft delete, "isDeleted": True, means it will not show up.
}