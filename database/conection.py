import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()
    
    def ver_faturamento(self, mes, ano):
        try:
            mes = mes
            print(mes)
            query = 'SELECT valor FROM faturamentos WHERE mes = ?'
            self.cursor.execute(query,(mes,))
            result = self.cursor.fetchall()
            print(result)
            valores = []
            for valor in result:
                print(valor[0])
                valores.append(valor[0])
            print(valores)
            output = sum(valores)
            print(output)
            return output
        except Exception as e:
            print(e)

class DatabaseGastos:
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()
    

    def set_boleto(self, boleto):
        pass

    def set_notas(self, nota):
        pass
    def verGastos(self):
        pass

    def gastos_por_tipo(self,tipo, mes, ano):
        try:
            pass
        except Exception as e:
            pass



