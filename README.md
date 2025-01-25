# Bookmark and Tag Management App

## Description
A Flask application integrated with Firebase Firestore to manage users, bookmarks, and tags. The app supports CRUD operations, searching, and filtering.

## Features
1. User management (create, update, delete users).
2. Bookmark management (create, search, filter, update, delete bookmarks).
3. Tag management (create, delete tags and count bookmarks associated with them).

## Installation

1. Clone the repository.
2. Set up a Firebase Firestore project.
3. Download the Firebase Admin SDK private key and save it as `firebase-key.json`.
4. Install dependencies:

```bash
pip install flask firebase-admin
```

5. Run the application:

```bash
python app.py
```

## API Endpoints

### User Endpoints
- `POST /users` - Create a user.
- `GET /users/<user_id>` - Get user details.
- `PUT /users/<user_id>` - Update user details.
- `DELETE /users/<user_id>` - Delete a user.

### Bookmark Endpoints
- `POST /bookmarks` - Create a bookmark.
- `GET /bookmarks/<user_id>` - Get all bookmarks for a user with optional search and tag filters.

## Example Usage

```bash
# Create a new user
curl -X POST -H "Content-Type: application/json" -d '{"firstName": "John", "lastName": "Doe", "avatarUrl": "example.com/avatar"}' http://127.0.0.1:5000/users