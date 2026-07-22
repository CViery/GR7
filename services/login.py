import logging

from flask import session
from database import login_db


class Login:
    def __init__(self):
        self.db = login_db.Login()

    def empresas(self):
        return self.db.get_empresa()

    def login(self, usuario, senha):
        try:
            if not usuario or not senha:
                return {
                    'autenticado': False,
                    'mensagem': 'Usuário e senha são obrigatórios.'
                }

            usuario_encontrado = self.db.get_user(usuario)

            if not usuario_encontrado:
                return {
                    'autenticado': False,
                    'mensagem': 'Usuário não encontrado.'
                }

            dados_usuario = {
                'id': usuario_encontrado[0],
                'usuario': usuario_encontrado[1],
                'senha': usuario_encontrado[2],
                'perfil': usuario_encontrado[3],
                'guia': usuario_encontrado[4]
            }

            if senha != dados_usuario['senha']:
                return {
                    'autenticado': False,
                    'mensagem': 'Senha incorreta.'
                }

            perfil = str(dados_usuario['perfil']).upper().strip()
            guia = int(dados_usuario['guia'])

            if perfil not in ['ADMIN', 'NORMAL']:
                return {
                    'autenticado': False,
                    'mensagem': 'Perfil de usuário inválido.'
                }

            session.clear()

            session['usuario_id'] = dados_usuario['id']
            session['usuario'] = dados_usuario['usuario']
            session['permission'] = perfil
            session['permission_empresa'] = guia

            return {
                'autenticado': True,
                'usuario': dados_usuario['usuario'],
                'perfil': perfil,
                'guia': guia
            }

        except Exception as erro:
            logging.exception(
                "Erro ao autenticar usuário: %s",
                erro
            )

            return {
                'autenticado': False,
                'mensagem': 'Erro interno durante a autenticação.'
            }