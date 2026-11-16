import ast
import inspect
import logging
import os
from pathlib import Path
from urllib.parse import quote_plus

from .extensions import db


logger = logging.getLogger(__name__)


def _resolver_connection_string():
    conn_str = (os.getenv("DB_CONNECTION_STRING") or "").strip()
    if conn_str:
        return conn_str

    try:
        from database import conection as db_conn

        # Caso _connection_string() funcione via variável de ambiente
        if hasattr(db_conn, "_connection_string"):
            try:
                val = db_conn._connection_string()
                if isinstance(val, str) and val.strip():
                    return val.strip()
            except RuntimeError:
                pass

        # Extrai a string conn_str definida dentro de Database.__init__ em database/conection.py
        if hasattr(db_conn, "Database"):
            source = inspect.getsource(db_conn.Database.__init__)
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "conn_str":
                            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                return node.value.value.strip()
    except Exception as exc:
        logger.warning("Não foi possível ler database.conection: %s", exc)

    return ""


def register_modulos(app):
    """Acopla o GR7 Módulos ao mesmo SQL Server do sistema gerencial."""
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    database_uri = os.getenv("MODULOS_DATABASE_URI", "").strip()
    if database_uri.lower().startswith("sqlite:"):
        logger.warning(
            "MODULOS_DATABASE_URI ainda aponta para SQLite; usando o SQL "
            "Server configurado em database.conection / DB_CONNECTION_STRING."
        )
        database_uri = ""

    if not database_uri:
        connection_string = _resolver_connection_string()
        if not connection_string:
            raise RuntimeError(
                "DB_CONNECTION_STRING não configurada e não encontrada em database.conection."
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

    if os.getenv("CI", "").lower() == "true" or app.config.get("TESTING"):
        return

    with app.app_context():
        try:
            db.create_all()
            if os.getenv("MODULOS_AUTO_SEED", "0") == "1":
                ensure_seeded()
        except Exception as exc:
            logger.warning("Aviso ao executar db.create_all() nos módulos: %s", exc)