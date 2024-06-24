from database import login_db


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
                    'permission': users[2]
                    }
                print(dados)
                if user == dados['user'] and password == dados['password']:
                    return True
            else:
                print('usuario não encontrado')
                return False
        except Exception as e:
            print(f"Erro ao autenticar usuário: {e}")
            return False