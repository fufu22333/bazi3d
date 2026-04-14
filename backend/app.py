import os
from uuid import uuid4

from flask import Flask, g, jsonify, request, send_from_directory
from flask_cors import CORS

from backend.config import get_config
from backend.models import Base, SessionLocal, configure_session
from backend.routes.auth import auth_bp
from backend.routes.assets import assets_bp
from backend.routes.chat import chat_bp
from backend.routes.evaluations import evaluations_bp
from backend.routes.proxy import proxy_bp
from backend.routes.tasks import tasks_bp
from backend.routes.works import works_bp



def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")

    def serve_frontend_file(filename: str):
        return send_from_directory(frontend_dir, filename)

    CORS(
        app,
        # resources={r"/api/*": {"origins": "http://127.0.0.1:8000"}},
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=False,
    )
    app.config.update(get_config())
    if test_config:
        app.config.update(test_config)

    engine = configure_session(app.config["SQLALCHEMY_DATABASE_URI"])
    if app.config.get("TESTING"):
        Base.metadata.create_all(engine)

    app.register_blueprint(auth_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(evaluations_bp)
    app.register_blueprint(proxy_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(works_bp)

    @app.before_request
    def assign_request_id() -> None:
        g.request_id = request.headers.get("X-Request-Id") or uuid4().hex

    @app.after_request
    def attach_request_id_header(response):
        response.headers["X-Request-Id"] = getattr(g, "request_id", "")
        return response

    @app.get("/")
    def home() -> tuple:
        return jsonify({
            "message": "bazi3d backend is running",
            "health": "/health"
        }), 200

    @app.get("/health")
    def health() -> tuple:
        return jsonify({"status": "ok"}), 200

    @app.route("/frontend/<path:filename>")
    def serve_frontend(filename: str):
        return serve_frontend_file(filename)

    @app.route("/<path:filename>")
    def serve_frontend_root_asset(filename: str):
        return serve_frontend_file(filename)

    @app.route("/app")
    def serve_index():
        return serve_frontend_file("index.html")

    @app.teardown_appcontext
    def remove_session(exception=None) -> None:
        SessionLocal.remove()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5001, debug=True)
