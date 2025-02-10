DIRECTORY_COLLECTION = "directories"
DIRECTORY_ID_PREFIX = "directory"

DEFAULT_DIRECTORY_ID = "directory-83167e18-7d55-4758-b00d-a8724e9feff5"
DEFAULT_DIRECTORY_NAME = "Uncategorized"

DIRECTORY_MODEL = {
    "directoryId": "",  # Required
    "userId": "",  # Required
    "name": "",  # Required (e.g., "Work", "Personal")
    "createdAt": "",
    "updatedAt": "",
    "isDeleted": False,  # Soft delete support,
    "isModifiable": True # Uncategorized should not be deleted/edited
}
