from flask_cors import CORS
from src.utils.init import create_app
from src.services.routes import api_blueprint
from waitress import serve
import os

# Check if running on Vercel
ON_VERCEL = os.getenv("VERCEL") == "1"

app = create_app()

# Enable CORS for all origins
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

PORT = 5002

# Register API blueprints
app.register_blueprint(api_blueprint, url_prefix="/api")

if __name__ == "__main__":
    if ON_VERCEL:
        print(f"🚀 Running Flask app with Waitress at port: {PORT}...")
        serve(app, host="0.0.0.0", port=PORT)
    else:
        print(f"🚀 Running Flask app on local...")
        app.run(debug=True)