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
    
    def get_all_gastos(self):
        try:
            query = 'SELECT * FROM gastos'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        
        except Exception as e:
            print(e)
    
    def get_gatos_por_tipo(self, tipo, mes, ano):
        try:
            query = 'SELECT valor WHERE despesa = ? AND mes_emissao = ? AND ano_emissao = ? FROM gastos'
            self.cursor.execute(query, (tipo, mes, ano))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)
    
    def get_boletos(self):
        try:
            query = 'SELECT * FROM boletos'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)
    
    def get_boleto_by_day(self, dia, mes, ano):
        try:
            query = 'SELECT * FROM boletos WHERE dia_vencimento = ? AND mes_vencimento = ? AND ano_vencimento = ?'
            self.cursor.execute(query, (dia, mes, ano))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def set_despesas(self, despesa):
        try:
            query = 'INSERT INTO despesas VALUES (?)'
            self.cursor.execute(query, (despesa,))
            self.db.conn.commit()
        except Exception as e:
            print(e)

    def get_despesas(self):
        try:
            query = 'SELECT * FROM despesas' 
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            print(result)
            return result
        except Exception as e:
            print(e)
    
    def get_valor_despesa(self, despesa, mes, ano):
        try:
            query = 'SELECT valor FROM notas WHERE despesa = ? AND mes_emissao = ? AND ano_emissao = ?'
            self.cursor.execute(query, (despesa, mes, ano))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)
    
    def get_all_notas(self):
        try:
            query = 'SELECT * FROM notas'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def obter_notas_filtradas(self,data_inicio=None, data_fim=None, fornecedor=None, despesa=None):
        # Construindo a query SQL
        query = "SELECT * FROM notas WHERE 1=1"
        params = []

        if data_inicio:
            query += " AND data_emissao >= ?"
            params.append(data_inicio)
        if data_fim:
            query += " AND data_emissao <= ?"
            params.append(data_fim)
        if fornecedor:
            query += " AND fornecedor = ?"
            params.append(fornecedor)
        if despesa:
            query += " AND despesa = ?"
            params.append(despesa)

        self.cursor.execute(query, params)
        resultados = self.cursor.fetchall()
        return resultados

    def get_nota_por_numero(self,num_nota):
        try:
            query = 'SELECT * FROM notas WHERE num_nota = ?'
            self.cursor.execute(query, (num_nota,))
            result = self.cursor.fetchone()
            return result
        except Exception as e:
            print(e)

    def atualizar_notas(self, num_nota, numero_duplicata,datas):
        try:
            query1 = 'UPDATE notas SET duplicata = ? WHERE num_nota =?'
            query2 = 'UPDATE notas SET vencimentos = ? WHERE num_nota =?'
            self.cursor.execute(query1, (numero_duplicata, num_nota))
            self.cursor.execute(query2, (datas, num_nota))
            self.db.conn.commit()
            print('foi')
        except Exception as e:
            print(e)
    
    def obter_boletos_filtrados(self, data_inicio=None, data_fim=None, fornecedor=None):
        # Construindo a query SQL
        query = "SELECT * FROM boletos WHERE 1=1"
        params = []

        if data_inicio:
            query += " AND data_vencimento >= ?"
            params.append(data_inicio)
        if data_fim:
            query += " AND data_vencimento <= ?"
            params.append(data_fim)
        if fornecedor:
            query += " AND fornecedor = ?"
            params.append(fornecedor)

        self.cursor.execute(query, params)
        resultados = self.cursor.fetchall()
        return resultados

    def get_valor_notas(self, mes, ano):
        try:
            query = 'SELECT valor FROM notas WHERE mes_emissao = ? AND ano_emissao = ?'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()
            print(result)
            return result
        except Exception as e:
            print(e)