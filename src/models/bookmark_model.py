from src.models.directory_model import DEFAULT_DIRECTORY_ID, DEFAULT_DIRECTORY_NAME

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
    "directoryId": DEFAULT_DIRECTORY_ID,  # Default directory
    "directoryName": DEFAULT_DIRECTORY_NAME,
    "createdAt": "",
    "updatedAt": "",
    "isDeleted": False,  # for now, implementing soft delete, "isDeleted": True, means it will not show up.
    "isFavorite": False
}