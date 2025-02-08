from flask import Blueprint
from src.services.routes.user_routes import user_blueprint
from src.services.routes.bookmark_routes import bookmark_blueprint
from src.services.routes.tag_routes import tags_blueprint
from src.services.routes.directory_routes import directory_blueprint

# Combine all blueprints into one
api_blueprint = Blueprint("api", __name__)
api_blueprint.register_blueprint(user_blueprint)
api_blueprint.register_blueprint(bookmark_blueprint)
api_blueprint.register_blueprint(tags_blueprint)
api_blueprint.register_blueprint(directory_blueprint)