# BookmarkAI Backend

## Description
A Flask application integrated with Firebase Firestore to manage users, bookmarks, and tags. The app supports CRUD operations, searching, and filtering.

## Features
1. User management (create, update, delete users).
2. Bookmark management (create, search, filter, update, delete bookmarks).
3. Tag management (create, delete tags and count bookmarks associated with them).

## Installation

1. Clone the repository.
3. Download the Firebase Admin SDK private key and save it as `credentials/credentials/firebase-adminsdk.json`. If downloaded file have different name, either rename to `firebase-adminsdk.json` or change path of credentials in `app.py` file.
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
# Create a new user in local
curl -X POST -H "Content-Type: application/json" -d '{"firstName": "John", "lastName": "Doe", "avatarUrl": "example.com/avatar", "email": "abc3@gmail.com"}' http://127.0.0.1:5002/api/user/create

# Create a new user in vercel
curl -X POST -H "Content-Type: application/json" -d '{"firstName": "John", "lastName": "Doe", "avatarUrl": "example.com/avatar", "email": "abc3@gmail.com"}' https://bookmark-ai-backend.vercel.app/api/user/create

# create bookmark in local
curl -X POST http://127.0.0.1:5002/api/bookmark/create \
     -H "Content-Type: application/json" \
     -H "userId: user-7601dd26-64ac-4327-84e2-e2d758701934" \
     -d '{
          "url": "https://www.reddit.com/r/vancouver/",
          "tags": ["reddit", "vancouver"]
         }'

# create bookmark in versel
curl -X POST https://bookmark-ai-backend.vercel.app/api/bookmark/create \
     -H "Content-Type: application/json" \
     -H "userId: user-7601dd26-64ac-4327-84e2-e2d758701934" \
     -d '{
          "url": "https://www.reddit.com/r/vancouver/",
          "tags": ["reddit", "vancouver"]
         }'

# to fetch all bookmarks
curl -X POST https://bookmark-ai-backend.vercel.app/api/bookmark/filter \
     -H "Content-Type: application/json" \
     -H "userId: user-7601dd26-64ac-4327-84e2-e2d758701934" \
     -d '{}'


# to fetch all tags
curl -X GET http://127.0.0.1:5002/api/tag/all \
     -H "Content-Type: application/json" \
     -H "userId: user-7601dd26-64ac-4327-84e2-e2d758701934" \
     -d '{}'

```