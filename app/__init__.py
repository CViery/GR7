from flask import Flask
app = Flask(__name__)
app.config['SECRET_ KEY'] = 'CVGS'
app.secret_key = 'sua_chave_secreta'
if __name__ == '__main__':
    app.run(debug=True)
from app import routes