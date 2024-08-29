import sqlite3
import pyodbc
import traceback


class Database:
    def __init__(self):
        conn_str = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:gr7server.database.windows.net,1433;Database=admingr7;Uid=cristian;Pwd=viery2312@;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
        self.conn = pyodbc.connect(conn_str)
        self.cursor = self.conn.cursor()

    def cadastrar_faturamento(self, dados):
        try:
            query = 'INSERT INTO faturamento VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
            self.cursor.execute(query, (dados['placa'], dados['modelo_veiculo'], dados['data_orcamento'], dados['data_faturamento'], dados['mes_faturamento'], dados['ano_faturamento'], dados['dias_servico'], dados['numero_os'], dados['companhia'], dados['conversao_ps'], dados['valor_pecas'], dados['valor_servicos'], dados['total_os'], dados['valor_revitalizacao'], dados['valor_aditivo'], dados['quantidade_litros'], dados['valor_fluido_sangria'], dados['valor_palheta'], dados['valor_limpeza_freios'], dados['valor_pastilha_parabrisa'],
                                dados['valor_filtro'], dados['valor_pneu'], dados['valor_bateria'], dados['modelo_bateria'], dados['lts_oleo_motor'], dados['valor_lt_oleo'], dados['marca_e_tipo_oleo'], dados['valor_p_meta'], dados['mecanico_servico'], dados['servico_filtro'],  dados['valor_em_dinheiro'], dados['valor_servico_freios'], dados['valor_servico_suspensao'], dados['valor_servico_injecao_ignicao'], dados['valor_servico_cabecote_motor_arr'], dados['valor_outros_servicos'], dados['valor_servicos_oleos'], dados['valor_servico_transmissao']))
            self.conn.commit()
        except Exception as e:
            print(e)

    def faturamento_mes(self, mes, ano):
        try:
            query = 'SELECT valor_os FROM faturamento WHERE mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()

            return result
        except Exception as e:
            print(e)

    def faturamento_mes_meta(self, mes, ano):
        try:
            query = 'SELECT valor_meta FROM faturamento WHERE mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def get_qntd_filtros_mec(self, mecanico, mes, ano):
        try:
            # Garantir que os parâmetros são strings
            mecanico = str(mecanico)
            mes = str(mes)
            ano = str(ano)

            # Debugging

            query = 'SELECT filtro_mecanico FROM faturamento WHERE filtro_mecanico = ? AND mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mecanico, mes, ano))
            result = self.cursor.fetchall()

            # Verificação dos resultados
            if not result:
                print("Nenhum resultado encontrado.")

            return result
        except Exception as e:
            print(f"Erro ao executar a consulta: {e}")
            traceback.print_exc()  # Imprime a pilha de chamadas para depuração
            raise e

    def faturamento_por_mecanico(self, mecanico, mes, ano):
        try:
            # Convertendo para strings se não estiverem
            mecanico = str(mecanico)
            mes = str(mes)
            ano = str(ano)

            # Montando a query SQL
            query = '''
            SELECT servicos 
            FROM faturamento 
            WHERE mecanico = ? AND mes_faturamento = ? AND ano_faturamento = ?
            '''

            # Imprimindo a query para debug

            # Executando a query
            self.cursor.execute(query, (mecanico, mes, ano))
            result = self.cursor.fetchall()

            return result

        except Exception as e:
            # Imprimindo o erro para debug
            print(f'Erro ao buscar faturamento por mecânico: {str(e)}')
            raise e

    def get_mecanicos(self):
        try:
            query = 'SELECT nome FROM funcionarios ORDER BY nome ASC; '
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(f'Erro ao buscar mecânico: {str(e)}')
            raise

    def get_revitalizacao_mecanico(self, mecanico, mes, ano):
        try:
            query = 'SELECT revitalizacao FROM faturamento WHERE mecanico = ? AND mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mecanico, mes, ano))
            result = self.cursor.fetchall()

            return result
        except Exception as e:
            print(e)

    def get_cias(self):
        try:
            query = 'SELECT * FROM companhias ORDER BY CAST(cia AS NVARCHAR(MAX)) ASC;'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            raise e

    def faturamento_cia(self, cia, mes, ano):
        try:
            query = 'SELECT valor_os FROM faturamento WHERE cia = ? AND mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (cia, mes, ano))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            raise e

    def faturamento_serv(self, serv, mes, ano):
        try:
            query = f'SELECT {
                serv} FROM faturamento WHERE mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()

            return result
        except Exception as e:
            print(e)

    def buscar_serv(self):
        try:
            query = 'SELECT * FROM servicos'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            raise e

    def faturamento_geral(self):
        try:
            query = 'SELECT * FROM faturamento ORDER BY data_faturamento ASC;'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def faturamento_pecas(self, mes, ano):
        try:
            query = 'SELECT pecas FROM faturamento WHERE mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def faturamento_servicos(self, mes, ano):
        try:
            query = 'SELECT servicos FROM faturamento WHERE mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def faturamento_dinheiro(self, mes, ano):
        try:
            query = 'SELECT valor_dinheiro FROM faturamento WHERE mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, mes, ano)
            result = self.cursor.fetchall()
            
            return result
        except Exception as e:
            print(e)

    def obter_ordens_filtradas(self, data_inicio=None, data_fim=None, placa=None, mecanico=None, num_os=None, cia=None):
        # Construindo a query SQL
        query = "SELECT * FROM faturamento"
        params = []
        filters = []

        if data_inicio:
            filters.append("data_faturamento >= ?")
            params.append(data_inicio)
        if data_fim:
            filters.append("data_faturamento <= ?")
            params.append(data_fim)
        if mecanico:
            filters.append("mecanico = ?")
            params.append(str(mecanico))
        if placa:
            filters.append("placa = ?")
            params.append(placa)
        if num_os:
            filters.append("num_os = ?")
            params.append(num_os)
        if cia:
            filters.append("cia = ?")
            params.append(cia)

        if filters:
            query += " WHERE " + " AND ".join(filters)

        query += " ORDER BY data_faturamento ASC;"

        self.cursor.execute(query, params)
        resultados = self.cursor.fetchall()
        return resultados

class DatabasePortal:
    def __init__(self):
        conn_str = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:gr7server.database.windows.net,1433;Database=admingr7;Uid=cristian;Pwd=viery2312@;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
        self.conn = pyodbc.connect(conn_str)
        self.cursor = self.conn.cursor()

    def cadastrar_faturamento(self, dados):
        try:
            query = 'INSERT INTO faturamento_portal VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
            self.cursor.execute(query, (dados['placa'], dados['modelo_veiculo'], dados['data_orcamento'], dados['data_faturamento'], dados['mes_faturamento'], dados['ano_faturamento'], dados['dias_servico'], dados['numero_os'], dados['companhia'], dados['conversao_ps'], dados['valor_pecas'], dados['valor_servicos'], dados['total_os'], dados['valor_revitalizacao'], dados['valor_aditivo'], dados['quantidade_litros'], dados['valor_fluido_sangria'], dados['valor_palheta'], dados['valor_limpeza_freios'], dados['valor_pastilha_parabrisa'],
                                dados['valor_filtro'], dados['valor_pneu'], dados['valor_bateria'], dados['modelo_bateria'], dados['lts_oleo_motor'], dados['valor_lt_oleo'], dados['marca_e_tipo_oleo'], dados['valor_p_meta'], dados['mecanico_servico'], dados['servico_filtro'],  dados['valor_em_dinheiro'], dados['valor_servico_freios'], dados['valor_servico_suspensao'], dados['valor_servico_injecao_ignicao'], dados['valor_servico_cabecote_motor_arr'], dados['valor_outros_servicos'], dados['valor_servicos_oleos'], dados['valor_servico_transmissao']))
            self.conn.commit()
        except Exception as e:
            print(e)

    def faturamento_mes(self, mes, ano):
        try:
            query = 'SELECT valor_os FROM faturamento_portal WHERE mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()

            return result
        except Exception as e:
            print(e)

    def faturamento_mes_meta(self, mes, ano):
        try:
            query = 'SELECT valor_meta FROM faturamento_portal WHERE mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def get_qntd_filtros_mec(self, mecanico, mes, ano):
        try:
            # Garantir que os parâmetros são strings
            mecanico = str(mecanico)
            mes = str(mes)
            ano = str(ano)

            # Debugging

            query = 'SELECT filtro_mecanico FROM faturamento_portal WHERE filtro_mecanico = ? AND mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mecanico, mes, ano))
            result = self.cursor.fetchall()

            # Verificação dos resultados
            if not result:
                print("Nenhum resultado encontrado.")

            return result
        except Exception as e:
            print(f"Erro ao executar a consulta: {e}")
            traceback.print_exc()  # Imprime a pilha de chamadas para depuração
            raise e

    def faturamento_por_mecanico(self, mecanico, mes, ano):
        try:
            # Convertendo para strings se não estiverem
            mecanico = str(mecanico)
            mes = str(mes)
            ano = str(ano)

            # Montando a query SQL
            query = '''
            SELECT servicos 
            FROM faturamento_portal
            WHERE mecanico = ? AND mes_faturamento = ? AND ano_faturamento = ?
            '''

            # Imprimindo a query para debug

            # Executando a query
            self.cursor.execute(query, (mecanico, mes, ano))
            result = self.cursor.fetchall()

            return result

        except Exception as e:
            # Imprimindo o erro para debug
            print(f'Erro ao buscar faturamento por mecânico: {str(e)}')
            raise e

    def get_mecanicos(self):
        try:
            query = 'SELECT nome FROM funcionarios_portal ORDER BY nome ASC;'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(f'Erro ao buscar mecânico: {str(e)}')
            raise

    def get_revitalizacao_mecanico(self, mecanico, mes, ano):
        try:
            query = 'SELECT revitalizacao FROM faturamento_portal WHERE mecanico = ? AND mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mecanico, mes, ano))
            result = self.cursor.fetchall()

            return result
        except Exception as e:
            print(e)

    def get_cias(self):
        try:
            query = 'SELECT * FROM companhias ORDER BY CAST(cia AS NVARCHAR(MAX)) ASC;'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            raise e

    def faturamento_cia(self, cia, mes, ano):
        try:
            query = 'SELECT valor_os FROM faturamento_portal WHERE cia = ? AND mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (cia, mes, ano))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            raise e

    def faturamento_serv(self, serv, mes, ano):
        try:
            query = f'SELECT {
                serv} FROM faturamento_portal WHERE mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()

            return result
        except Exception as e:
            print(e)

    def buscar_serv(self):
        try:
            query = 'SELECT * FROM servicos_portal'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            raise e

    def faturamento_geral(self):
        try:
            query = 'SELECT * FROM faturamento_portal ORDER BY data_faturamento ASC;'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def faturamento_pecas(self, mes, ano):
        try:
            query = 'SELECT pecas FROM faturamento_portal WHERE mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def faturamento_servicos(self, mes, ano):
        try:
            query = 'SELECT servicos FROM faturamento_portal WHERE mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def faturamento_dinheiro(self, mes, ano):
        try:
            query = 'SELECT valor_dinheiro FROM faturamento_portal WHERE mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, mes, ano)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def obter_ordens_filtradas(self, data_inicio=None, data_fim=None, placa=None, mecanico=None, num_os=None, cia=None):
        # Construindo a query SQL
        query = "SELECT * FROM faturamento_portal"
        params = []
        filters = []

        if data_inicio:
            filters.append("data_faturamento >= ?")
            params.append(data_inicio)
        if data_fim:
            filters.append("data_faturamento <= ?")
            params.append(data_fim)
        if mecanico:
            filters.append("mecanico = ?")
            params.append(str(mecanico))
        if placa:
            filters.append("placa = ?")
            params.append(placa)
        if num_os:
            filters.append("num_os = ?")
            params.append(num_os)
        if cia:
            filters.append("cia = ?")
            params.append(cia)

        if filters:
            query += " WHERE " + " AND ".join(filters)

        query += " ORDER BY data_faturamento ASC;"

        self.cursor.execute(query, params)
        resultados = self.cursor.fetchall()
        return resultados