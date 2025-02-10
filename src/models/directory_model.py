DIRECTORY_COLLECTION = "directories"
DIRECTORY_ID_PREFIX = "directory"

DEFAULT_DIRECTORY_ID = "directory-165ee178-7c68-4134-a2f6-9455be8ec55e"
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
