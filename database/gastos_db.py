from database import conection


class GastosDataBase:
    def __init__(self):
        self.db = conection.Database()
        self.cursor = self.db.cursor

    def set_nota(self, nota):
        try:
            query = 'INSERT INTO notas VALUES (?,?,?,?,?,?,?,?,?,?,?,?)'
            self.cursor.execute(query, (nota['emitido_para'], nota['status'], nota['boleto'], nota['nota'], nota['duplicata'], nota['fornecedor'], nota['data_emissao'], nota['dia_emissao'], nota['mes_emissao'], nota['ano_emissao'], nota['despesa'], nota['valor']))
            result = 'Nota Cadastrada'
            print(result)
            self.db.conn.commit()
        except Exception as e:
            print(e)
    
    def set_boleto(self, boleto):
        try:
            query = 'INSERT INTO boletos VALUES (?,?,?,?,?,?,?,?)'
            self.cursor.execute(query, (boleto['num_nota'], boleto['notas'], boleto['fornecedor'], boleto['vencimento'], boleto['dia_vencimento'], boleto['mes_vencimento'], boleto['ano_vencimento'], boleto['valor']))
            result = 'Boleto Cadastrado'
            self.db.conn.commit()
            print(result)
        except Exception as e:
            print(e)
