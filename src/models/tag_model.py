from enum import Enum

"""
Enum to define the creator of the tag. A tag can be created either by a user or by service using LLM.
"""
class TAG_CREATOR(Enum):
    USER = "USER"
    SERVICE = "SERVICE"

TAG_COLLECTION = "tags"

TAG_MODEL = {
    "tagId": "", # Required.
    "tagName": "", # Required.
    "creator": TAG_CREATOR.USER, # Setting the default creator as user.
    "userId": "" # Required.
}