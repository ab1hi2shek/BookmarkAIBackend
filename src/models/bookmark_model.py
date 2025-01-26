BOOKMARK_COLLECTION = "bookmarks"

BOOKMARK_MODEL = {
    "bookmarkId": "",
    "userId": "", # required
    "url": "", # required
    "title": "",
    "notes": "",
    "tags": [],
    "createdAt": "",
    "updatedAt": "",
    "isDeleted": False  # for now, implementing soft delete, "isDeleted": True, means it will not show up.
}