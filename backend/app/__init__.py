import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from backend.app.config import Config
from backend.app.db import db
from backend.app.cli import register_cli_commands

migrate = Migrate()

def create_app(config_class=Config):
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dist_path = os.path.join(repo_root, "dist")
    if not os.path.exists(dist_path):
        dist_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dist")

    app = Flask(
        __name__,
        static_folder=dist_path,
        static_url_path="/static"
    )
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, supports_credentials=True)

    # Ensure upload directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Register CLI commands
    register_cli_commands(app)

    # Register blueprints (will be populated in subsequent milestones)
    from backend.app.auth.routes import auth_bp
    from backend.app.api.catalog import catalog_bp
    from backend.app.payments.routes import payments_bp
    from backend.app.api.orders import orders_bp
    from backend.app.admin.routes import admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)

    # Serve built React SPA & hash routing fallback
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        # Do not hijack API routes
        if path.startswith("api/"):
            return jsonify({"error": "Resource not found"}), 404

        if app.static_folder and os.path.exists(app.static_folder):
            if path and os.path.exists(os.path.join(app.static_folder, path)) and os.path.isfile(os.path.join(app.static_folder, path)):
                return send_from_directory(app.static_folder, path)
            return send_from_directory(app.static_folder, "index.html")
        return jsonify({"message": "BoostX API is running."}), 200

    return app
