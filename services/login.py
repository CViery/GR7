from database import login_db
from flask import session


class Login:
    def __init__(self):
        self.db = login_db.Login()

    def login(self, user, password):
        try:
            users = self.db.get_user(user)
            if users:
                dados = {
                    'user': users[0],
                    'password': users[1],
                    'permission': users[2],
                    'empresa': users[3]
                }
                if user == dados['user'] and password == dados['password']:
                    if dados['permission'] == 'ADMIN':
                        session['permission'] = dados['permission']
                        session['permission_empresa'] = dados['empresa']
                        return 'ADMIN'
                    elif dados['permission'] == 'NORMAL':
                        session['permission'] = dados['permission']
                        session['permission_empresa'] = dados['empresa']
                        return 'NORMAL'
            else:
                print('usuario não encontrado')
                return False
        except Exception as e:
            print(f"Erro ao autenticar usuário: {e}")
            return False
