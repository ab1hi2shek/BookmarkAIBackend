from src.utils.init import create_app
from src.services.routes import api_blueprint

app = create_app()

# Register API blueprints
app.register_blueprint(api_blueprint, url_prefix="/api")

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)