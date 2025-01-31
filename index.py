from src.utils.init import create_app
from src.services.routes import api_blueprint
from waitress import serve

app = create_app()

PORT = 5002

# Register API blueprints
app.register_blueprint(api_blueprint, url_prefix="/api")

if __name__ == "__main__":
    print(f"🚀 Running Flask app with Waitress at port: {PORT}...")
    serve(app, host="0.0.0.0", port=PORT)