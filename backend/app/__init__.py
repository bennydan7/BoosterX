import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from backend.app.config import Config
from backend.app.db import db
from backend.app.cli import register_cli_commands

def create_app(config_class=Config):
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "dist"),
        static_url_path="/"
    )
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    CORS(app, supports_credentials=True)

    # Ensure upload directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Register CLI commands
    register_cli_commands(app)

    # Register blueprints (will be populated in subsequent milestones)
    from backend.app.auth.routes import auth_bp
    from backend.app.api.catalog import catalog_bp
    from backend.app.payments.routes import payments_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(payments_bp)

    # Serve built React SPA & hash routing fallback
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        # Do not hijack API routes
        if path.startswith("api/"):
            return jsonify({"error": "Resource not found"}), 404
            
        dist_dir = app.static_folder
        if dist_dir and os.path.exists(dist_dir):
            file_path = os.path.join(dist_dir, path)
            if path and os.path.exists(file_path) and os.path.isfile(file_path):
                return send_from_directory(dist_dir, path)
            return send_from_directory(dist_dir, "index.html")
        return jsonify({"message": "BoostX API is running. Frontend dist not built yet."}), 200

    return app
