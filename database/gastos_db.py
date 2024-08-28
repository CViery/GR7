from database import conection


class GastosDataBase:
    def __init__(self):
        self.db = conection.Database()
        self.cursor = self.db.cursor

    def set_nota(self, nota):
        try:
            query = 'INSERT INTO notas VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
            self.cursor.execute(query, (nota['pago_por'], nota['emitido_para'], nota['status'], nota['boleto'], nota['nota'], nota['duplicata'], nota['fornecedor'],
                                nota['data_emissao'], nota['dia_emissao'], nota['mes_emissao'], nota['ano_emissao'], nota['vencimentos'], nota['valor'], nota['despesa'], ))
            result = 'Nota Cadastrada'
            self.db.conn.commit()
        except Exception as e:
            print(e)

    def set_boleto(self, boleto):
        try:
            query = 'INSERT INTO boletos VALUES (?,?,?,?,?,?,?,?)'
            self.cursor.execute(query, (boleto['num_nota'], boleto['notas'], boleto['fornecedor'], boleto['vencimento'],
                                boleto['dia_vencimento'], boleto['mes_vencimento'], boleto['ano_vencimento'], boleto['valor']))
            result = 'Boleto Cadastrado'
            self.db.conn.commit()

        except Exception as e:
            print(e)

    def get_all_gastos(self):
        try:
            query = 'SELECT * FROM notas ORDER BY data_emissao ASC;'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result

        except Exception as e:
            print(e)

    def get_gastos_por_tipo(self, tipo, mes, ano):
        try:
            query = 'SELECT valor FROM notas WHERE despesa = ? AND mes_emissao = ? AND ano_emissao = ?  '
            self.cursor.execute(query, (tipo, mes, ano))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def get_boletos(self):
        try:
            query = 'SELECT * FROM boletos ORDER BY data_vencimento ASC'
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
            query = 'SELECT * FROM despesa'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
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
            query = 'SELECT * FROM notas ORDER BY data_emissao ASC;'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def obter_notas_filtradas(self, data_inicio=None, data_fim=None, fornecedor=None, despesa=None):
        # Construindo a query SQL
        query = "SELECT * FROM notas"
        params = []
        filters = []

        if data_inicio:
            filters.append( " data_emissao >= ?")
            params.append(data_inicio)
        if data_fim:
            filters.append(" data_emissao <= ?")
            params.append(data_fim)
        if fornecedor:
            filters.append(" fornecedor = ?")
            params.append(fornecedor)
        if despesa:
            filters.append(" num_nota  = ?")
            params.append(despesa)
        
        if filters:
            query += " WHERE " + " AND ".join(filters)

        query += " ORDER BY data_emissao ASC;"


        self.cursor.execute(query, params)
        resultados = self.cursor.fetchall()
        return resultados

    def get_nota_por_numero(self, num_nota):
        try:
            query = 'SELECT * FROM notas WHERE num_nota = ?'
            self.cursor.execute(query, (num_nota,))
            result = self.cursor.fetchone()
            return result
        except Exception as e:
            print(e)

    def atualizar_notas(self, num_nota, numero_duplicata, datas):
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
        filters = []

        if data_inicio:
            filters.append(" data_vencimento >= ?")
            params.append(data_inicio)
        if data_fim:
            filters.append("  data_vencimento <= ?")
            params.append(data_fim)
        if fornecedor:
            filters.append("  fornecedor = ?")
            params.append(fornecedor)
        
        if filters:
            query += " WHERE " + " AND ".join(filters)

        query += " ORDER BY data_vencimento ASC;"

        self.cursor.execute(query, params)
        resultados = self.cursor.fetchall()
        return resultados

    def get_valor_notas(self, mes, ano):
        try:
            query = 'SELECT valor FROM notas WHERE mes_emissao = ? AND ano_emissao = ?'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def get_fornecedores(self):
        try:
            query = 'SELECT * FROM fornecedores '
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def get_recebedor(self):
        try:
            query = 'SELECT * FROM emitido_para'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def set_fornecedor(self, cnpj, nome):
        try:
            query = 'INSERT INTO fornecedores (cnpj, nome) VALUES (?,?)'
            self.cursor.execute(query, (cnpj, nome))
            self.db.conn.commit()
        except Exception as e:
            print(e)

    def set_oleo(self, oleo):
        try:
            query = 'INSERT INTO oleos (nome) VALUES (?)'
            self.cursor.execute(query, (oleo))
            self.db.conn.commit()
        except Exception as e:
            print(e)

    def cadastrar_companhia(self, compahia):
        try:
            query = 'INSERT INTO compahias (cia) VALUES (?)'
            self.cursor.execute(query, (compahia))
            self.db.conn.commit()
        except Exception as e:
            print(e)

    def cadastrar_funcionario(self, id, funcionario):
        try:
            query = 'INSERT INTO funcionarios (id,funcionario) VALUES (?)'
            self.cursor.execute(query, (id, funcionario))
            self.db.conn.commit()
        except Exception as e:
            print(e)

    def cadastrar_baterias(self, modelo):
        try:
            query = 'INSERT INTO baterias (modelo) VALUES (?)'
            self.cursor.execute(query, (modelo))
            self.db.conn.commit()
        except Exception as e:
            print(e)


class GastosDataBasePortal():
    def __init__(self):
        self.db = conection.Database()
        self.cursor = self.db.cursor

    def set_nota(self, nota):
        try:
            query = 'INSERT INTO notas_portal VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
            self.cursor.execute(query, (nota['pago_por'], nota['emitido_para'], nota['status'], nota['boleto'], nota['nota'], nota['duplicata'], nota['fornecedor'],
                                nota['data_emissao'], nota['dia_emissao'], nota['mes_emissao'], nota['ano_emissao'], nota['vencimentos'], nota['valor'], nota['despesa'], ))
            result = 'Nota Cadastrada'
            self.db.conn.commit()
        except Exception as e:
            print(e)

    def set_boleto(self, boleto):
        try:
            query = 'INSERT INTO boletos_portal VALUES (?,?,?,?,?,?,?,?)'
            self.cursor.execute(query, (boleto['num_nota'], boleto['notas'], boleto['fornecedor'], boleto['vencimento'],
                                boleto['dia_vencimento'], boleto['mes_vencimento'], boleto['ano_vencimento'], boleto['valor']))
            result = 'Boleto Cadastrado'
            self.db.conn.commit()

        except Exception as e:
            print(e)

    def get_all_gastos(self):
        try:
            query = 'SELECT * FROM notas_portal ORDER BY data_emissao ASC;'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            
            return result

        except Exception as e:
            print(e)

    def get_gatos_por_tipo(self, tipo, mes, ano):
        try:
            query = 'SELECT valor FROM notas_portal WHERE despesa = ? AND mes_emissao = ? AND ano_emissao = ? '
            self.cursor.execute(query, (tipo, mes, ano))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def get_boletos(self):
        try:
            query = 'SELECT * FROM boletos_portal ORDER BY data_vencimento ASC'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def get_boleto_by_day(self, dia, mes, ano):
        try:
            query = 'SELECT * FROM boletos_portal WHERE dia_vencimento = ? AND mes_vencimento = ? AND ano_vencimento = ?'
            self.cursor.execute(query, (dia, mes, ano))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def set_despesas(self, despesa):
        try:
            query = 'INSERT INTO despesa_portal VALUES (?)'
            self.cursor.execute(query, (despesa,))
            self.db.conn.commit()
        except Exception as e:
            print(e)

    def get_despesas(self):
        try:
            query = 'SELECT * FROM despesa_portal'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
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
            query = 'SELECT * FROM notas_portal ORDER BY data_emissao ASC;'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def obter_notas_filtradas(self, data_inicio=None, data_fim=None, fornecedor=None, despesa=None):
        # Construindo a query SQL
        query = "SELECT * FROM notas_portal"
        params = []
        filters = []

        if data_inicio:
            filters.append( " data_emissao >= ?")
            params.append(data_inicio)
        if data_fim:
            filters.append(" data_emissao <= ?")
            params.append(data_fim)
        if fornecedor:
            filters.append(" fornecedor = ?")
            params.append(fornecedor)
        if despesa:
            filters.append(" num_nota  = ?")
            params.append(despesa)
        
        if filters:
            query += " WHERE " + " AND ".join(filters)

        query += " ORDER BY data_emissao ASC;"


        self.cursor.execute(query, params)
        resultados = self.cursor.fetchall()
        return resultados
    
    def get_nota_por_numero(self, num_nota):
        try:
            query = 'SELECT * FROM notas_portal WHERE num_nota = ?'
            self.cursor.execute(query, (num_nota,))
            result = self.cursor.fetchone()
            return result
        except Exception as e:
            print(e)

    def atualizar_notas(self, num_nota, numero_duplicata, datas):
        try:
            query1 = 'UPDATE notas_portal SET duplicata = ? WHERE num_nota =?'
            query2 = 'UPDATE notas_portal SET vencimentos = ? WHERE num_nota =?'
            self.cursor.execute(query1, (numero_duplicata, num_nota))
            self.cursor.execute(query2, (datas, num_nota))
            self.db.conn.commit()
           
        except Exception as e:
            print(e)

    def obter_boletos_filtrados(self, data_inicio=None, data_fim=None, fornecedor=None):
        # Construindo a query SQL
        query = "SELECT * FROM boletos WHERE 1=1"
        params = []
        filters = []

        if data_inicio:
            filters.append("  data_vencimento >= ?")
            params.append(data_inicio)
        if data_fim:
            filters.append("  data_vencimento <= ?")
            params.append(data_fim)
        if fornecedor:
            filters.append("  fornecedor = ?")
            params.append(fornecedor)
        
        if filters:
            query += " WHERE " + " AND ".join(filters)

        query += " ORDER BY data_vencimento ASC;"

        self.cursor.execute(query, params)
        resultados = self.cursor.fetchall()
        return resultados

    def get_valor_notas(self, mes, ano):
        try:
            query = 'SELECT valor FROM notas_portal WHERE mes_emissao = ? AND ano_emissao = ?'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def get_fornecedores(self):
        try:
            query = 'SELECT * FROM fornecedores_portal'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def get_recebedor(self):
        try:
            query = 'SELECT * FROM emitido_para_portal'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def set_fornecedor(self, cnpj, nome):
        try:
            query = 'INSERT INTO fornecedores_portal (cnpj, nome) VALUES (?,?)'
            self.cursor.execute(query, (cnpj, nome))
            self.db.conn.commit()
        except Exception as e:
            print(e)

    def set_oleo(self, oleo):
        try:
            query = 'INSERT INTO oleos (nome) VALUES (?)'
            self.cursor.execute(query, (oleo))
            self.db.conn.commit()
        except Exception as e:
            print(e)

    def cadastrar_companhia(self, compahia):
        try:
            query = 'INSERT INTO companhias_portal (cia) VALUES (?)'
            self.cursor.execute(query, (compahia))
            self.db.conn.commit()
        except Exception as e:
            print(e)

    def cadastrar_funcionario(self, id, funcionario):
        try:
            query = 'INSERT INTO funcionarios_portal (id,nome) VALUES (?,?)'
            self.cursor.execute(query, (id, funcionario))
            self.db.conn.commit()
        except Exception as e:
            print(e)

    def cadastrar_baterias(self, modelo):
        try:
            query = 'INSERT INTO baterias (modelo) VALUES (?)'
            self.cursor.execute(query, (modelo))
            self.db.conn.commit()
        except Exception as e:
            print(e)

    def set_fornecedor(self, cnpj, nome):
        try:
            query = 'INSERT INTO fornecedores_portal (cnpj, nome) VALUES (?,?)'
            self.cursor.execute(query, (cnpj, nome))
            self.db.conn.commit()
        except Exception as e:
            print(e)
