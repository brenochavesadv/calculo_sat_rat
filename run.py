# flask --app run:create_app --debug run

from datetime import timedelta

from flask import Flask, jsonify, redirect, render_template, url_for
from flask_jwt_extended import JWTManager, get_jwt_identity, verify_jwt_in_request
from werkzeug.exceptions import RequestEntityTooLarge

from app import db
from config import Config


jwt = JWTManager()


def _import_models():
    """Import models before Flask-Migrate inspects the metadata."""
    from app.models import ajuste  # noqa: F401
    from app.models import base_apurada  # noqa: F401
    from app.models import calcula_cs  # noqa: F401
    from app.models import contribuicao  # noqa: F401
    from app.models import esocial_s1005_evtTabEstab  # noqa: F401
    from app.models import esocial_s1010_evtTabRubrica  # noqa: F401
    from app.models import esocial_s1200_evtRemun  # noqa: F401
    from app.models import esocial_s1202_evtRmnRPPS  # noqa: F401
    from app.models import esocial_s1210_evtPgtos  # noqa: F401
    from app.models import esocial_s1298_evtReabreEvPer  # noqa: F401
    from app.models import esocial_s1299_evtFechaEvPer  # noqa: F401
    from app.models import esocial_s5001_evtBasesTrab  # noqa: F401
    from app.models import esocial_s5002_evtIrrfBenef  # noqa: F401
    from app.models import esocial_s5011_evtCs  # noqa: F401
    from app.models import esocial_s5011_evtCs_bases_remun  # noqa: F401
    from app.models import esocial_s5011_evtCs_info_cr_contrib  # noqa: F401
    from app.models import import_skip  # noqa: F401
    from app.models import job  # noqa: F401
    from app.models import municipio  # noqa: F401
    from app.models import remuneracao  # noqa: F401
    from app.models import rubrica  # noqa: F401
    from app.models import selic  # noqa: F401
    from app.models import user  # noqa: F401


def create_app(config_class=Config, **config_overrides):
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder="app/templates",
        static_folder="app/static",
    )
    app.config.from_object(config_class)
    app.config.update(config_overrides)

    @app.context_processor
    def inject_max_upload():
        return {"max_upload_bytes": app.config.get("MAX_CONTENT_LENGTH")}

    db.init_app(app)
    jwt.init_app(app)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
        minutes=app.config.get("JWT_ACCESS_TOKEN_EXPIRES_MIN", 60)
    )
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(
        minutes=app.config.get("JWT_REFRESH_TOKEN_EXPIRES_MIN", 43200)
    )

    _import_models()

    from flask_migrate import Migrate

    Migrate(app, db)

    from app.blueprints.routes.apuracao_routes import bp as apuracao_bp
    from app.blueprints.routes.auth_routes import bp as auth_bp
    from app.blueprints.routes.municipio_routes import bp as municipio_bp
    from app.blueprints.routes.selic_routes import bp as selic_bp
    from app.blueprints.routes.upload_routes import bp as upload_bp
    from app.blueprints.reports import bp as reports_bp

    app.register_blueprint(upload_bp, url_prefix="/upload")
    app.register_blueprint(selic_bp, url_prefix="/selic")
    app.register_blueprint(municipio_bp, url_prefix="/municipios")
    app.register_blueprint(apuracao_bp, url_prefix="/apuracao")
    app.register_blueprint(auth_bp)
    app.register_blueprint(reports_bp, url_prefix="/reports")

    @app.get("/")
    def index():
        try:
            verify_jwt_in_request(optional=True)
            if not get_jwt_identity():
                return redirect(url_for("auth.page_login"))
        except Exception:
            return redirect(url_for("auth.page_login"))
        return render_template("dashboard.html")

    @app.errorhandler(RequestEntityTooLarge)
    def handle_large_file(error):
        from flask import request

        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(
                error="Request entity too large",
                max_bytes=app.config.get("MAX_CONTENT_LENGTH"),
            ), 413
        return render_template(
            "413.html", max_bytes=app.config.get("MAX_CONTENT_LENGTH")
        ), 413

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=True)