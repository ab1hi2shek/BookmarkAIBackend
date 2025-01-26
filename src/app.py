from src.utils.init import app
from src.services.routes import api_blueprint

# Register API blueprints
app.register_blueprint(api_blueprint, url_prefix="/api")

if __name__ == "__main__":
    app.run(debug=True)