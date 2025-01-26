from flask import jsonify, request
from functools import wraps
from src.utils.init import db
from src.models.user_model import USER_COLLECTION

"""
Decorator that ensures only authorized users can access the wrapped API routes.
"""
def authorize_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = request.headers.get("userId")
        if not user_id:
            return jsonify({"error": "Unauthorized: Missing key userId in header"}), 401
        
        """
        Check if user exists in Firestore
        Querying the Firestore database on every request is inefficient, especially for high-traffic APIs 
        or cases where the same user sends multiple requests in a short time span.

        Here are some optimized approaches to handle user authorization more efficiently:
        1. Use a Cached Authorization System: Like Redis, Memcached, or a local Python dictionary.
        2. Use a JWT-Based System (Stateless Authentication)
        """
        user_ref = db.collection(USER_COLLECTION).document(user_id).get()
        if not user_ref.exists:
            return jsonify({"error": "Unauthorized: Invalid userId passed"}), 401
        request.user_id = user_id  # Attach userId to the request context
        return func(*args, **kwargs)
    return wrapper