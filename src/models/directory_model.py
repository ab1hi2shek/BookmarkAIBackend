DIRECTORY_COLLECTION = "directories"
DIRECTORY_ID_PREFIX = "directory"

DEFAULT_DIRECTORY_NAME_AND_ID = "uncategorized"

DIRECTORY_MODEL = {
    "directoryId": "",  # Required
    "userId": "",  # Required
    "name": "",  # Required (e.g., "Work", "Personal")
    "createdAt": "",
    "updatedAt": "",
    "isDeleted": False,  # Soft delete support,
    "isModifiable": True # Uncategorized should not be deleted/edited
}
