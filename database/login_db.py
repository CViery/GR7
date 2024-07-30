class Login:
    def __init__(self):
        pass
    
    def get_user(self, user):
        try:
            users = [('CRISTIAN', 'viery2312', 'ADMIN'), ('GILBERTO', 'Giba130364@2024', 'ADMIN'), ('FERNANDO', '1234', 'NORMAL')]
            for person in users:
                if person[0] == user:
                    return person
        except Exception as e:
            print(f"Erro ao buscar usuário: {e}")
            return None