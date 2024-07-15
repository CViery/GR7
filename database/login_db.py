class Login:
    def __init__(self):
        pass
    
    def get_user(self, user):
        try:
            users = [('CRISTIAN', 'viery2312', 'ADMIN'), ('GILBERTO', '1234', 'ADMIN')]
            for person in users:
                if person[0] == user:
                    return person
        except Exception as e:
            print(f"Erro ao buscar usuário: {e}")
            return None

    