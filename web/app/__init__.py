from flask import Flask
from flask_cors import CORS


def create_app():
    """Create the Flask app
    
    This function creates the ready-to-use Flask app and returns it.

    Returns:
        Flask: The app created.
    """    
    app = Flask(__name__)
    CORS(app)

    from .api import api as api_bp
    app.register_blueprint(api_bp)

    return app
