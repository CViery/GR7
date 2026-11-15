import os
import logging
from pathlib import Path
from urllib.parse import quote_plus

from .extensions import db


logger = logging.getLogger(__name__)


def register_modulos(app):
    """Acopla o GR7 Módulos ao mesmo SQL Server do sistema gerencial."""
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    database_uri = os.getenv("MODULOS_DATABASE_URI", "").strip()
    if database_uri.lower().startswith("sqlite:"):
        logger.warning(
            "MODULOS_DATABASE_URI ainda aponta para SQLite; usando o SQL "
            "Server configurado em DB_CONNECTION_STRING."
        )
        database_uri = ""
    if not database_uri:
        connection_string = os.getenv("DB_CONNECTION_STRING")
        if not connection_string:
            raise RuntimeError(
                "DB_CONNECTION_STRING não configurada. A área de Módulos "
                "usa o mesmo SQL Server do sistema gerencial."
            )
        database_uri = (
            "mssql+pyodbc:///?odbc_connect="
            + quote_plus(connection_string)
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    app.config.setdefault(
        "SQLALCHEMY_ENGINE_OPTIONS",
        {"pool_pre_ping": True, "pool_recycle": 1800},
    )

    db.init_app(app)

    from .cli import ensure_seeded, register_cli
    from .routes import bp

    app.register_blueprint(bp)
    register_cli(app)

    with app.app_context():
        db.create_all()
        if os.getenv("MODULOS_AUTO_SEED", "0") == "1":
            ensure_seeded()
