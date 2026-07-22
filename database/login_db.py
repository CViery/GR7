import logging
from database import conection


class Login:
    def __init__(self):
        self.db = conection.Database()

    def get_user(self, usuario):
        try:
            query = """
                SELECT
                    id,
                    usuario,
                    senha,
                    perfil,
                    guia
                FROM usuarios
                WHERE UPPER(usuario) = UPPER(?);
            """

            self.db.cursor.execute(query, (usuario,))
            return self.db.cursor.fetchone()

        except Exception as erro:
            logging.exception(
                "Erro ao buscar usuário no banco: %s",
                erro
            )
            return None

    def get_empresa(self):
        try:
            return self.db.get_empresa()

        except Exception as erro:
            logging.exception(
                "Erro ao buscar empresas: %s",
                erro
            )
            return []