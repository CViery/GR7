from flask import Flask
from flask_session import Session
import redis


app = Flask(__name__)
app.config['SECRET_ KEY'] = 'CVGS'
# Configurações para Flask-Session
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'session:'
app.config['SESSION_REDIS'] = redis.StrictRedis(host='localhost', port=6379, db=0)
app.secret_key = 'sua_chave_secreta'
if __name__ == '__main__':
    app.run(debug=True)
from app import routes