import mysql.connector


class Database:
    def __init__(self):
        try:
            cnx = mysql.connector.connect(user="edvkcjfxrx", password="{your_password}", host="admingr7-servidor.mysql.database.azure.com", port=3306, database="{your_database}", ssl_ca="{ca-cert filename}", ssl_disabled=False)
            self.cursor = self.conn.cursor()
            print('Conexão estabelecida com sucesso.')
        except pyodbc.Error as e:
            print(f'Erro ao conectar ao banco de dados: {e}')

    def close(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
            print('Conexão fechada.')


# Inicialização da classe Database
app = Database()

# Fechamento da conexão (exemplo de uso)
app.close()