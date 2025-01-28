class Login:
    def __init__(self):
        pass

    def get_user(self, user):
        try:
            # Guia 0=Acesso total, 1=GR7, 2=Portal
            users = [
                ('CRISTIAN', 'viery2312', 'ADMIN', 0),
                ('GILBERTO', 'Giba130364@2024', 'ADMIN', 0),
                ('THIAGO', 'Qazplm82*', 'ADMIN', 2),
                ('DANIEL', '415263', 'ADMIN', 0),
                ('FERNANDO', '1234', 'NORMAL', 2),
                ('ANA MARIA', '1234', 'NORMAL', 2),
                ('SERGIO', '1234', 'ADMIN', 2),
            ]
            for person in users:
                if person[0] == user:
                    return person
        except Exception as e:
            print(f"Erro ao buscar usuário: {e}")
            return None
