from database import login_db
from flask import session


class Login:
    def __init__(self):
        self.db = login_db.Login()

    def login(self, user, password):
        try:
            # Verifica se os dados fornecidos não estão vazios
            if not user or not password:
                print("Usuário e senha não podem ser vazios.")
                return False

            # Obtém os dados do usuário do banco de dados
            users = self.db.get_user(user)

            if users:
                dados = {
                    'user': users[0],
                    'password': users[1],
                    'permission': users[2],
                    'empresa': users[3]
                }
                print(session)
                # Verifica se a senha fornecida corresponde à senha armazenada
                if password == dados['password']:
                    # Define as permissões e a empresa na sessão
                    session['permission'] = dados['permission']
                    session['permission_empresa'] = dados['empresa']

                    if dados['permission'] == 'ADMIN':
                        return 'ADMIN'
                    elif dados['permission'] == 'NORMAL':
                        return 'NORMAL'
                else:
                    print('Senha incorreta')
                    return False
            else:
                print('Usuário não encontrado')
                return False

        except Exception as e:
            # Trata erros específicos de autenticação
            print(f"Erro ao autenticar usuário: {e}")
            return False
