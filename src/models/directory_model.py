DIRECTORY_COLLECTION = "directories"
DIRECTORY_ID_PREFIX = "directory"

DIRECTORY_MODEL = {
    "directoryId": "",  # Required
    "userId": "",  # Required
    "name": "",  # Required (e.g., "Work", "Personal")
    "createdAt": "",
    "updatedAt": "",
    "isDeleted": False  # Soft delete support
}
