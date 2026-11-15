import os
from datetime import timedelta
from pathlib import Path

from flask import Flask
from dotenv import load_dotenv


# Carrega as configurações locais antes de qualquer conexão com o banco.
load_dotenv(Path(__file__).resolve().parent.parent / '.env')


app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'gr7-altere-esta-chave-em-producao'),
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,
    SEND_FILE_MAX_AGE_DEFAULT=timedelta(days=1),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=os.getenv('SESSION_COOKIE_SECURE', '0') == '1',
    JSON_AS_ASCII=False,
)


from database.conection import close_connection

app.teardown_appcontext(close_connection)

# Gerencial e Módulos compartilham o mesmo SQL Server, Flask, login e sessão.
from modulos import register_modulos

register_modulos(app)

# Importações no final evitam dependência circular durante a criação do app.
from app import routes
from app import gastos
from app import aprovacoes
