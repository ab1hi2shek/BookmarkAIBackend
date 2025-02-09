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

### Local APIs

```bash

# Create a new user in local
curl -X POST -H "Content-Type: application/json" -d '{"firstName": "John", "lastName": "Doe", "avatarUrl": "example.com/avatar", "email": "abc3@gmail.com"}' http://127.0.0.1:5002/api/user/create

# create bookmark in local
curl -X POST http://127.0.0.1:5000/api/bookmark/create \
     -H "Content-Type: application/json" \
     -H "userId: omUeLo2YN6N2LUVePtiKvCT9odD2" \
     -d '{
          "url": "https://www.reddit.com/r/vancouver/",
          "tags": ["reddit", "vancouver"]
         }'

# Fetch all bookmarks in local
curl -X GET http://127.0.0.1:5000/api/bookmark/all \
     -H "Content-Type: application/json" \
     -H "userId: omUeLo2YN6N2LUVePtiKvCT9odD2"

# To update a bookmark tags in local
curl -X POST http://127.0.0.1:5000/api/bookmark/update/bookmark-a8ceaf44-891b-403c-8e35-df363dfb9b2f \
     -H "Content-Type: application/json" \
     -H "userId: omUeLo2YN6N2LUVePtiKvCT9odD2" \
     -d '{
          "tags": ["reddit", "vancouver"]
         }'

# to fetch all tags in local
curl -X GET http://127.0.0.1:5000/api/tag/all \
     -H "Content-Type: application/json" \
     -H "userId: omUeLo2YN6N2LUVePtiKvCT9odD2"


# to fetch bookmarks with tagId in local
curl -X GET "http://127.0.0.1:5000/api/bookmark/tag/tag-e2c6cd22-6371-49a9-9cb8-928b5bbe287b" \
     -H "Content-Type: application/json" \
     -H "userId: omUeLo2YN6N2LUVePtiKvCT9odD2"

# to fetch all directories of a user in local
curl -X GET "http://127.0.0.1:5000/api/directory/all" \
     -H "Content-Type: application/json" \
     -H "userId: omUeLo2YN6N2LUVePtiKvCT9odD2"

# to fetch bookmarks with directoryId in local
curl -X GET "http://127.0.0.1:5000/api/bookmark/directory/directory-56a207d2-edd3-46fb-b935-90095d4263e1" \
     -H "Content-Type: application/json" \
     -H "userId: omUeLo2YN6N2LUVePtiKvCT9odD2"

```

### Vercel APIs

```bash

# Create a new user in vercel
curl -X POST -H "Content-Type: application/json" -d '{"firstName": "John", "lastName": "Doe", "avatarUrl": "example.com/avatar", "email": "abc3@gmail.com"}' https://bookmark-ai-backend.vercel.app/api/user/create

# create bookmark in vercel
curl -X POST https://bookmark-ai-backend.vercel.app/api/bookmark/create \
     -H "Content-Type: application/json" \
     -H "userId: omUeLo2YN6N2LUVePtiKvCT9odD2" \
     -d '{
          "url": "https://www.reddit.com/r/vancouver/",
          "tags": ["reddit", "vancouver"]
         }'

# Fetch all bookmarks in vercel
curl -X GET https://bookmark-ai-backend.vercel.app/api/bookmark/all \
     -H "Content-Type: application/json" \
     -H "userId: omUeLo2YN6N2LUVePtiKvCT9odD2"

# to fetch all tags in vercel
curl -X GET https://bookmark-ai-backend.vercel.app/api/tag/all \
     -H "Content-Type: application/json" \
     -H "userId: omUeLo2YN6N2LUVePtiKvCT9odD2" \
     -d '{}'

```