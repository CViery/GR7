import sqlite3
import pyodbc
import traceback
import logging

logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
class Database:
    def __init__(self):
        conn_str = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:gr7server.database.windows.net,1433;Database=admingr7;Uid=cristian;Pwd=viery2312@;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
        self.conn = pyodbc.connect(conn_str)
        self.cursor = self.conn.cursor()
        

    def cadastrar_faturamento(self, dados):
        """
        Método para cadastrar dados de faturamento no banco de dados.

        Parâmetros:
            dados (dict): Dicionário contendo os dados necessários para o cadastro.

        Retorno:
            dict: Resultado da operação, com status e mensagem.
        """
        try:
            # Query com os nomes das colunas explicitamente definidos
            print(dados)
            query = '''
                INSERT INTO faturamento (
                    placa, modelo_veiculo, data_orcamento, data_faturamento, mes_faturamento, ano_faturamento, 
                    dias, num_os, cia, conversao_pneustore, pecas, servicos, valor_os, 
                    revitalizacao, aditivo, quantidade_aditivo, fluido_sangria, palheta, 
                    limpeza_freios, detergente_parabrisa, filtro, pneus, bateria, 
                    modelo_bateria, quantidade_oleo, valor_oleo, tipo_marca_oleo, valor_meta, mecanico, 
                    filtro_mecanico, valor_dinheiro, freios, suspensao, 
                    injecao_ignicao,cabecote_motor_arrefecimento, outros, 
                    oleos, transmissao, usuario, observacoes, terceiros
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            '''

            # Executa a query com os dados fornecidos
            self.cursor.execute(query, (
                dados['placa'], dados['modelo_veiculo'], dados['data_orcamento'], dados['data_faturamento'], 
                dados['mes_faturamento'], dados['ano_faturamento'], dados['dias_servico'], dados['numero_os'], 
                dados['companhia'], dados['conversao_ps'], dados['valor_pecas'], dados['valor_servicos'], 
                dados['total_os'], dados['valor_revitalizacao'], dados['valor_aditivo'], dados['quantidade_litros'], 
                dados['valor_fluido_sangria'], dados['valor_palheta'], dados['valor_limpeza_freios'], 
                dados['valor_pastilha_parabrisa'], dados['valor_filtro'], dados['valor_pneu'], dados['valor_bateria'], 
                dados['modelo_bateria'], dados['lts_oleo_motor'], dados['valor_lt_oleo'], dados['marca_e_tipo_oleo'], 
                dados['valor_p_meta'], dados['mecanico_servico'], dados['servico_filtro'], dados['valor_em_dinheiro'], 
                dados['valor_servico_freios'], dados['valor_servico_suspensao'], dados['valor_servico_injecao_ignicao'], 
                dados['valor_servico_cabecote_motor_arr'], dados['valor_outros_servicos'], dados['valor_servicos_oleos'], 
                dados['valor_servico_transmissao'], dados['usuario'], dados['obs'], dados['valor_terceiros']
            ))

            # Confirma a transação
            self.conn.commit()

            return {"status": "success", "message": "Faturamento cadastrado com sucesso."}

        except Exception as e:
            # Reverte a transação em caso de erro
            self.conn.rollback()

            # Loga o erro detalhado
            logging.error("Erro ao cadastrar faturamento: %s", e)

            # Retorna uma mensagem de erro
            return {"status": "error", "message": str(e)}


    def faturamento_mes(self, mes, ano):
        try:
            logging.info(f"Consulta de faturamento iniciada para o mês {mes}/{ano}.")
            
            query = 'SELECT valor_os FROM faturamento WHERE mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()
            
            if result:
                logging.info(f"Foram encontrados {len(result)} registros para o mês {mes}/{ano}.")
            else:
                logging.warning(f"Nenhum registro encontrado para o mês {mes}/{ano}.")
            
            return result
        except Exception as e:
            logging.error(f"Erro ao consultar faturamento para o mês {mes}/{ano}: {e}")
            return []

    def faturamento_mes_meta(self, mes, ano):
        try:
            logging.info(f"Iniciando consulta de valor meta para o mês {mes}/{ano}.")
            
            query = 'SELECT valor_meta FROM faturamento WHERE mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()
            
            if result:
                logging.info(f"Consulta concluída com sucesso. {len(result)} registro(s) encontrado(s) para o mês {mes}/{ano}.")
            else:
                logging.warning(f"Nenhum registro encontrado para o mês {mes}/{ano}.")
            
            return result
        except Exception as e:
            logging.error(f"Erro ao consultar valor meta para o mês {mes}/{ano}: {e}")
            return []

    def get_qntd_filtros_mec(self, mecanico, mes, ano):
        try:
            # Garantir que os parâmetros são strings
            mecanico = str(mecanico)
            mes = str(mes)
            ano = str(ano)
            
            logging.info(f"Iniciando consulta de filtros do mecânico '{mecanico}' para {mes}/{ano}.")
            
            query = '''
                SELECT filtro_mecanico 
                FROM faturamento 
                WHERE filtro_mecanico = ? AND mes_faturamento = ? AND ano_faturamento = ?
            '''
            self.cursor.execute(query, (mecanico, mes, ano))
            result = self.cursor.fetchall()
            
            if not result:
                logging.warning(f"Nenhum registro encontrado para o mecânico '{mecanico}' no mês {mes}/{ano}.")
            else:
                logging.info(f"Consulta concluída com {len(result)} registro(s) encontrado(s) para o mecânico '{mecanico}' no mês {mes}/{ano}.")
            
            return result
        except Exception as e:
            logging.error(f"Erro ao executar a consulta para o mecânico '{mecanico}' no mês {mes}/{ano}: {e}")
            raise

    def faturamento_por_mecanico(self, mecanico, mes, ano):
        """
        Consulta o faturamento de serviços realizados por um mecânico em um determinado mês e ano.

        Args:
            mecanico (str): Nome do mecânico.
            mes (str): Mês do faturamento.
            ano (str): Ano do faturamento.

        Returns:
            list: Lista de resultados da consulta, contendo os serviços faturados.
        """
        try:
            # Garantindo que os parâmetros são strings
            mecanico = str(mecanico)
            mes = str(mes)
            ano = str(ano)
            
            logging.info(f"Iniciando consulta de faturamento para o mecânico '{mecanico}' em {mes}/{ano}.")
            
            # Montando a query SQL
            query = '''
                SELECT servicos 
                FROM faturamento 
                WHERE mecanico = ? AND mes_faturamento = ? AND ano_faturamento = ?
            '''
            
            # Executando a query
            self.cursor.execute(query, (mecanico, mes, ano))
            result = self.cursor.fetchall()
            
            if result:
                logging.info(f"Consulta concluída com sucesso. {len(result)} registro(s) encontrado(s) para o mecânico '{mecanico}' em {mes}/{ano}.")
            else:
                logging.warning(f"Nenhum registro encontrado para o mecânico '{mecanico}' em {mes}/{ano}.")
            
            return result
        except Exception as e:
            logging.error(f"Erro ao buscar faturamento para o mecânico '{mecanico}' em {mes}/{ano}: {e}")
            raise

    def get_mecanicos(self):
        """
        Retorna a lista de nomes dos mecânicos cadastrados, ordenada alfabeticamente.

        Returns:
            list: Lista de tuplas contendo os nomes dos mecânicos.
        """
        try:
            logging.info("Iniciando consulta de mecânicos cadastrados.")
            
            query = 'SELECT nome FROM funcionarios ORDER BY nome ASC;'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            
            if result:
                logging.info(f"Consulta concluída com sucesso. {len(result)} mecânico(s) encontrado(s).")
            else:
                logging.warning("Nenhum mecânico encontrado na tabela 'funcionarios'.")
            
            return result
        except Exception as e:
            logging.error(f"Erro ao buscar mecânicos: {e}")
            raise

    def get_revitalizacao_mecanico(self, mecanico, mes, ano):
        """
        Consulta as revitalizações realizadas por um mecânico em um determinado mês e ano.

        Args:
            mecanico (str): Nome do mecânico.
            mes (str | int): Mês do faturamento.
            ano (str | int): Ano do faturamento.

        Returns:
            list: Lista de resultados contendo os valores de revitalizações realizadas pelo mecânico.
        """
        try:
            # Garantindo que os parâmetros são strings
            mecanico = str(mecanico)
            mes = str(mes)
            ano = str(ano)
            
            logging.info(f"Iniciando consulta de revitalizações para o mecânico '{mecanico}' em {mes}/{ano}.")
            
            # Montando a query SQL
            query = '''
                SELECT revitalizacao 
                FROM faturamento 
                WHERE mecanico = ? AND mes_faturamento = ? AND ano_faturamento = ?
            '''
            
            # Executando a consulta
            self.cursor.execute(query, (mecanico, mes, ano))
            result = self.cursor.fetchall()
            
            # Logando o resultado
            if result:
                logging.info(f"Consulta concluída. {len(result)} registro(s) encontrado(s) para o mecânico '{mecanico}' em {mes}/{ano}.")
            else:
                logging.warning(f"Nenhum registro encontrado para revitalizações do mecânico '{mecanico}' em {mes}/{ano}.")
            
            return result
        except Exception as e:
            logging.error(f"Erro ao buscar revitalizações para o mecânico '{mecanico}' em {mes}/{ano}: {e}")
            raise

    def get_cias(self):
        """
        Consulta todas as companhias cadastradas, ordenadas alfabeticamente pelo campo 'cia'.

        Returns:
            list: Lista de registros da tabela 'companhias'.
        """
        try:
            logging.info("Iniciando consulta de companhias.")

            # Query SQL para buscar e ordenar as companhias
            query = 'SELECT * FROM companhias ORDER BY CAST(cia AS NVARCHAR(MAX)) ASC;'
            self.cursor.execute(query)
            result = self.cursor.fetchall()

            # Logando o número de resultados
            if result:
                logging.info(f"Consulta concluída. {len(result)} companhia(s) encontrada(s).")
            else:
                logging.warning("Nenhuma companhia encontrada na tabela 'companhias'.")
            
            return result
        except Exception as e:
            logging.error(f"Erro ao buscar companhias: {e}")
            raise

    def faturamento_cia(self, cia, mes, ano):
        """
        Consulta o faturamento de uma companhia específica em um determinado mês e ano.

        Args:
            cia (str): Nome da companhia.
            mes (str | int): Mês do faturamento.
            ano (str | int): Ano do faturamento.

        Returns:
            list: Lista de valores de faturamento (valor_os) para a companhia no mês e ano informados.
        """
        try:
            # Garantindo que os parâmetros sejam strings
            cia = str(cia)
            mes = str(mes)
            ano = str(ano)
            
            logging.info(f"Iniciando consulta de faturamento para a companhia '{cia}' em {mes}/{ano}.")
            
            # Query SQL para buscar o valor de faturamento
            query = '''
                SELECT valor_os 
                FROM faturamento 
                WHERE cia = ? AND mes_faturamento = ? AND ano_faturamento = ?
            '''
            
            # Executando a consulta
            self.cursor.execute(query, (cia, mes, ano))
            result = self.cursor.fetchall()
            
            # Logando o resultado
            if result:
                logging.info(f"Consulta concluída. {len(result)} registro(s) encontrado(s) para a companhia '{cia}' em {mes}/{ano}.")
            else:
                logging.warning(f"Nenhum registro encontrado para faturamento da companhia '{cia}' em {mes}/{ano}.")
            
            return result
        except Exception as e:
            logging.error(f"Erro ao buscar faturamento para a companhia '{cia}' em {mes}/{ano}: {e}")
            raise

    def faturamento_serv(self, serv, mes, ano):
        """
        Consulta o valor de um serviço específico no faturamento de um determinado mês e ano.

        Args:
            serv (str): Nome do serviço (coluna) a ser consultado.
            mes (str | int): Mês do faturamento.
            ano (str | int): Ano do faturamento.

        Returns:
            list: Lista de valores para o serviço especificado no mês e ano informados.
        """
        try:
            # Garantir que os parâmetros sejam strings
            serv = str(serv)
            mes = str(mes)
            ano = str(ano)

            logging.info(f"Iniciando consulta de faturamento para o serviço '{serv}' em {mes}/{ano}.")
            
            # Montando a query SQL com placeholders para os parâmetros mes e ano
            query = f'SELECT {serv} FROM faturamento WHERE mes_faturamento = ? AND ano_faturamento = ?'

            # Executando a consulta
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()
            
            # Logando o resultado
            if result:
                logging.info(f"Consulta concluída. {len(result)} registro(s) encontrado(s) para o serviço '{serv}' em {mes}/{ano}.")
            else:
                logging.warning(f"Nenhum registro encontrado para o serviço '{serv}' em {mes}/{ano}.")
            
            return result
        except Exception as e:
            logging.error(f"Erro ao buscar faturamento para o serviço '{serv}' em {mes}/{ano}: {e}")
            raise

    def buscar_serv(self):
        """
        Consulta todos os serviços disponíveis na tabela 'servicos'.

        Returns:
            list: Lista de todos os registros da tabela 'servicos'.
        """
        try:
            logging.info("Iniciando a busca por todos os serviços.")
            
            # Montando e executando a query SQL
            query = 'SELECT * FROM servicos'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            
            # Logando o número de registros encontrados
            logging.info(f"{len(result)} serviço(s) encontrado(s).")
            
            return result
        except Exception as e:
            logging.error(f"Erro ao buscar serviços: {e}")
            raise e

    def faturamento_geral(self):
        """
        Consulta todos os registros de faturamento ordenados pela data de faturamento.

        Returns:
            list: Lista de todos os registros da tabela 'faturamento'.
        """
        try:
            logging.info("Iniciando a busca por todos os registros de faturamento.")

            # Montando e executando a query SQL
            query = 'SELECT * FROM faturamento ORDER BY data_faturamento ASC;'
            self.cursor.execute(query)
            result = self.cursor.fetchall()

            # Logando o número de registros encontrados
            logging.info(f"{len(result)} registro(s) de faturamento encontrado(s).")

            return result
        except Exception as e:
            logging.error(f"Erro ao buscar registros de faturamento: {e}")
            raise e

    def faturamento_pecas(self, mes, ano):
        """
        Consulta as peças faturadas no mês e ano fornecidos.

        Args:
            mes (str): O mês do faturamento.
            ano (str): O ano do faturamento.

        Returns:
            list: Lista de peças faturadas no mês e ano especificados.
        """
        try:
            logging.info(f"Iniciando a busca pelas peças faturadas para {mes}/{ano}.")

            # Montando e executando a query SQL
            query = 'SELECT pecas FROM faturamento WHERE mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()

            # Verificando se foram encontrados resultados
            if result:
                logging.info(f"{len(result)} peça(s) encontrada(s) para {mes}/{ano}.")
            else:
                logging.warning(f"Nenhuma peça encontrada para {mes}/{ano}.")

            return result
        except Exception as e:
            logging.error(f"Erro ao buscar peças faturadas para {mes}/{ano}: {e}")
            raise e

    def faturamento_servicos(self, mes, ano):
        """
        Consulta os serviços faturados no mês e ano fornecidos.

        Args:
            mes (str): O mês do faturamento.
            ano (str): O ano do faturamento.

        Returns:
            list: Lista de serviços faturados no mês e ano especificados.
        """
        try:
            logging.info(f"Iniciando a busca pelos serviços faturados para {mes}/{ano}.")

            # Montando e executando a query SQL
            query = 'SELECT servicos FROM faturamento WHERE mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()

            # Verificando se foram encontrados resultados
            if result:
                logging.info(f"{len(result)} serviço(s) encontrado(s) para {mes}/{ano}.")
            else:
                logging.warning(f"Nenhum serviço encontrado para {mes}/{ano}.")

            return result
        except Exception as e:
            logging.error(f"Erro ao buscar serviços faturados para {mes}/{ano}: {e}")
            raise e

    def faturamento_dinheiro(self, mes, ano):
        """
        Consulta o valor faturado em dinheiro no mês e ano fornecidos.

        Args:
            mes (str): O mês do faturamento.
            ano (str): O ano do faturamento.

        Returns:
            list: Lista de valores faturados em dinheiro no mês e ano especificados.
        """
        try:
            logging.info(f"Iniciando a busca pelo faturamento em dinheiro para {mes}/{ano}.")

            # Montando e executando a query SQL
            query = 'SELECT valor_dinheiro FROM faturamento WHERE mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()

            # Verificando se foram encontrados resultados
            if result:
                logging.info(f"{len(result)} valor(es) de faturamento em dinheiro encontrado(s) para {mes}/{ano}.")
            else:
                logging.warning(f"Nenhum faturamento em dinheiro encontrado para {mes}/{ano}.")

            return result
        except Exception as e:
            logging.error(f"Erro ao buscar faturamento em dinheiro para {mes}/{ano}: {e}")
            raise e

    def faturamento_dinheiro_ordens(self, mes, ano):
        """
        Consulta os registros de faturamento em dinheiro para um mês e ano específicos,
        ordenados pela data de faturamento.

        Args:
            mes (str): O mês do faturamento.
            ano (str): O ano do faturamento.

        Returns:
            list: Lista de registros de faturamento ordenados por data.
        """
        try:
            logging.info(f"Iniciando a busca pelo faturamento em dinheiro para {mes}/{ano}, ordenado por data.")

            # Montando e executando a query SQL
            query = 'SELECT * FROM faturamento WHERE mes_faturamento = ? AND ano_faturamento = ? ORDER BY data_faturamento ASC;'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()

            # Verificando se foram encontrados resultados
            if result:
                logging.info(f"{len(result)} registro(s) de faturamento em dinheiro encontrado(s) para {mes}/{ano}.")
            else:
                logging.warning(f"Nenhum faturamento em dinheiro encontrado para {mes}/{ano}.")

            return result
        except Exception as e:
            logging.error(f"Erro ao buscar faturamento em dinheiro para {mes}/{ano}: {e}")
            raise e

    
    def obter_ordens_filtradas(self, data_inicio=None, data_fim=None, placa=None, mecanico=None, num_os=None, cia=None):
        """
        Obtém ordens de faturamento filtradas por múltiplos parâmetros.

        Args:
            data_inicio (str): Data de início (formato: 'YYYY-MM-DD') para filtrar as ordens.
            data_fim (str): Data de fim (formato: 'YYYY-MM-DD') para filtrar as ordens.
            placa (str): Filtra por placa do veículo.
            mecanico (str): Filtra por nome do mecânico.
            num_os (str): Filtra por número da ordem de serviço.
            cia (str): Filtra por companhia.

        Returns:
            list: Lista de ordens filtradas.
        """
        try:
            # Construindo a query SQL
            query = "SELECT * FROM faturamento"
            params = []
            filters = []

            # Adicionando filtros com base nos parâmetros fornecidos
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

            # Adicionando filtros à query, se houver
            if filters:
                query += " WHERE " + " AND ".join(filters)

            # Ordenando os resultados pela data de faturamento
            query += " ORDER BY data_faturamento ASC;"

            # Logando a query que será executada
            logging.info(f"Executando consulta: {query} com parâmetros {params}")

            # Executando a consulta
            self.cursor.execute(query, params)
            resultados = self.cursor.fetchall()

            # Logando a quantidade de resultados encontrados
            logging.info(f"{len(resultados)} ordens encontradas com os filtros fornecidos.")

            return resultados

        except Exception as e:
            # Logando o erro caso ocorra uma exceção
            logging.error(f"Erro ao obter ordens filtradas: {e}")
            raise e
    
    def buscar_os_by_number(self, num_os):
        """
        Busca uma ordem de serviço no banco de dados pelo número da ordem.

        Args:
            num_os (str): Número da ordem de serviço a ser buscada.

        Returns:
            dict: Resultado da consulta, ou None se não encontrado.
        """
        try:
            # Logando o início da busca
            logging.info(f"Iniciando a busca pela ordem de serviço num_os: {num_os}")
            
            # Executando a consulta no banco
            self.cursor.execute('SELECT * FROM faturamento WHERE num_os = ?', (num_os,))
            result = self.cursor.fetchone()

            if result is None:
                logging.warning(f"Nenhum registro encontrado para num_os: {num_os}")
            else:
                logging.info(f"Ordem de serviço num_os: {num_os} encontrada.")

            return result

        except Exception as e:
            # Logando o erro
            logging.error(f"Erro ao buscar a ordem de serviço num_os: {num_os}. Detalhes do erro: {e}")
            return None
    
    def valor_filtro(self, mes, ano, mecanico):
        """
        Retorna o valor do filtro para um determinado mês, ano e mecânico, se encontrado.

        Args:
            mes (str): Mês de referência para a consulta.
            ano (str): Ano de referência para a consulta.
            mecanico (str): Nome do mecânico para o filtro.

        Returns:
            str or None: Valor do filtro ou None se não encontrado ou se o mecânico for 'BATERIA_DOMICILIO'.
        """
        try:
            # Verificando se o mecânico não é 'BATERIA_DOMICILIO'
            if mecanico != 'BATERIA_DOMICILIO':
                query = '''
                    SELECT filtro 
                    FROM faturamento 
                    WHERE mes_faturamento = ? 
                    AND ano_faturamento = ? 
                    AND filtro_mecanico = ?
                '''
                # Logando o início da consulta
                logging.info(f"Iniciando consulta para filtro: mes={mes}, ano={ano}, mecanico={mecanico}")
                
                # Executando a consulta no banco de dados
                self.cursor.execute(query, (mes, ano, mecanico))
                result = self.cursor.fetchone()

                # Verificando o resultado
                if result:
                    logging.info(f"Filtro encontrado para o mecânico {mecanico}: {result[0]}")
                    return result[0]  # Retorna o valor do filtro
                else:
                    logging.warning(f"Nenhum filtro encontrado para o mecânico {mecanico} no mês {mes} e ano {ano}.")
                    return None  # Retorna None caso não encontre resultado

            # Caso o mecânico seja 'BATERIA_DOMICILIO', retorna None
            logging.info("Mecânico é 'BATERIA_DOMICILIO', retornando None.")
            return None

        except Exception as e:
            # Logando o erro de exceção
            logging.error(f"Erro ao executar a consulta para filtro com mes={mes}, ano={ano}, mecanico={mecanico}. Detalhes do erro: {e}")
            return None
    
    def relatorio_filtro(self, mes, ano, mecanico):
        """
        Retorna os filtros e o filtro do mecânico para um determinado mês, ano e mecânico.

        Args:
            mes (str): Mês de referência para a consulta.
            ano (str): Ano de referência para a consulta.
            mecanico (str): Nome do mecânico para o filtro.

        Returns:
            list: Lista de resultados contendo o filtro e filtro_mecanico ou uma lista vazia se não encontrado.
        """
        try:
            # Logando o início da consulta
            logging.info(f"Iniciando consulta para relatório de filtro: mes={mes}, ano={ano}, mecanico={mecanico}")
            
            query = '''
                SELECT filtro, filtro_mecanico 
                FROM faturamento 
                WHERE mes_faturamento = ? 
                AND ano_faturamento = ? 
                AND filtro_mecanico = ?
            '''
            self.cursor.execute(query, (mes, ano, mecanico))
            result = self.cursor.fetchall()

            # Verificando se o resultado é vazio
            if result:
                logging.info(f"Consulta bem-sucedida. {len(result)} resultados encontrados.")
                return result
            else:
                logging.warning(f"Nenhum resultado encontrado para o mecânico {mecanico} no mês {mes} e ano {ano}.")
                return []  # Retorna uma lista vazia se não encontrar resultados

        except Exception as e:
            # Logando o erro de exceção
            logging.error(f"Erro ao executar a consulta para o filtro com mes={mes}, ano={ano}, mecanico={mecanico}. Detalhes do erro: {e}")
            return []  # Retorna uma lista vazia em caso de erro


    def relatorio_revitalizacao(self, mes, ano, mecanico):
        """
        Retorna os filtros e o filtro do mecânico para um determinado mês, ano e mecânico.

        Args:
            mes (str): Mês de referência para a consulta.
            ano (str): Ano de referência para a consulta.
            mecanico (str): Nome do mecânico para o filtro.

        Returns:
            list: Lista de resultados contendo o filtro e filtro_mecanico ou uma lista vazia se não encontrado.
        """
        try:
            # Logando o início da consulta
            logging.info(f"Iniciando consulta para relatório de revitalizacoes: mes={mes}, ano={ano}, mecanico={mecanico}")
            
            query = '''
                SELECT revitalizacao, mecanico 
                FROM faturamento 
                WHERE mes_faturamento = ? 
                AND ano_faturamento = ? 
                AND mecanico = ?
            '''
            self.cursor.execute(query, (mes, ano, mecanico))
            result = self.cursor.fetchall()

            # Verificando se o resultado é vazio
            if result:
                logging.info(f"Consulta bem-sucedida. {len(result)} resultados encontrados.")
                return result
            else:
                logging.warning(f"Nenhum resultado encontrado para o mecânico {mecanico} no mês {mes} e ano {ano}.")
                return []  # Retorna uma lista vazia se não encontrar resultados

        except Exception as e:
            # Logando o erro de exceção
            logging.error(f"Erro ao executar a consulta para a revitalizacao com mes={mes}, ano={ano}, mecanico={mecanico}. Detalhes do erro: {e}")
            return []  # Retorna uma lista vazia em caso de erro
        
    
    def buscar_faturamento(self, num_os):
        """
        Busca o faturamento com base no número da ordem de serviço.

        Args:
            num_os (str): Número da ordem de serviço a ser pesquisada.

        Returns:
            dict: Dados do faturamento ou None se não encontrado.
        """
        try:
            # Logando o início da consulta
            logging.info(f"Iniciando consulta para buscar faturamento com num_os: {num_os}")
            
            query = 'SELECT * FROM faturamentos WHERE num_os = ?'
            self.cursor.execute(query, (num_os,))
            result = self.cursor.fetchone()

            if result:
                # Logando sucesso na consulta
                logging.info(f"Consulta bem-sucedida. Faturamento encontrado para num_os: {num_os}")
                return result
            else:
                # Logando caso não encontre nenhum resultado
                logging.warning(f"Nenhum faturamento encontrado para num_os: {num_os}")
                return None  # Retorna None se não encontrar resultados

        except Exception as e:
            # Logando o erro de exceção
            logging.error(f"Erro ao executar a consulta para num_os: {num_os}. Detalhes do erro: {e}")
            return None  # Retorna None em caso de erro
    
    def atualizar_ordem_de_servico(self, num_os, dados):
        try:
            query = """
                    UPDATE tabela_veiculos
                    SET 
                        placa = ?,
                        modelo_veiculo = ?,
                        data_orcamento = ?,
                        data_faturamento = ?,
                        mes_faturamento = ?,
                        ano_faturamento = ?,
                        dias_servico = ?,
                        numero_os = ?,
                        companhia = ?,
                        conversao_ps = ?,
                        valor_pecas = ?,
                        valor_servicos = ?,
                        total_os = ?,
                        valor_revitalizacao = ?,
                        valor_aditivo = ?,
                        quantidade_litros = ?,
                        valor_fluido_sangria = ?,
                        valor_palheta = ?,
                        valor_limpeza_freios = ?,
                        valor_pastilha_parabrisa = ?,
                        valor_filtro = ?,
                        valor_pneu = ?,
                        valor_bateria = ?,
                        modelo_bateria = ?,
                        lts_oleo_motor = ?,
                        valor_lt_oleo = ?,
                        marca_e_tipo_oleo = ?,
                        valor_p_meta = ?,
                        mecanico_servico = ?,
                        servico_filtro = ?,
                        valor_em_dinheiro = ?,
                        valor_servico_freios = ?,
                        valor_servico_suspensao = ?,
                        valor_servico_injecao_ignicao = ?,
                        valor_servico_cabecote_motor_arr = ?,
                        valor_outros_servicos = ?,
                        valor_servicos_oleos = ?,
                        valor_servico_transmissao = ?,
                        usuario = ?,
                        obs = ?
                    WHERE num_os = ?;
                """
            valores = tuple(dados.values()) + (num_os,)
            cursor = self.conn.cursor()
            cursor.execute(query, valores)
            self.conn.commit()
            print(f"Ordem de serviço {num_os} atualizada com sucesso.")
        except Exception as e:
            print(f"Erro ao atualizar ordem de serviço {num_os}: {e}")
    
    def detalhes_filtros(self, mes, ano, mecanico):
        try:
            # Adicionando prints para verificar os valores recebidos
            print(f"Mes: {mes}, Ano: {ano}, Mecânico: {mecanico}")
            
            query = 'SELECT * FROM faturamento WHERE mes_faturamento = ? AND ano_faturamento = ? AND filtro_mecanico = ?'
            
            # Verificando a query antes da execução
            print(f"Executando query: {query} com os parâmetros ({mes}, {ano}, {mecanico})")
            
            self.cursor.execute(query, (mes, ano, mecanico))
            
            # Verificando o resultado obtido
            result = self.cursor.fetchall()
            print(f"Resultado da consulta: {result}")
            
            return result
        except Exception as e:
            # Adicionando print para verificar erros
            print(f"Erro ao executar a consulta: {e}")
            raise

    def detalhes_revitalizacao(self, mes, ano, mecanico):
        try:
            # Adicionando prints para verificar os valores recebidos
            print(f"Mes: {mes}, Ano: {ano}, Mecânico: {mecanico}")
            
            query = 'SELECT * FROM faturamento WHERE mes_faturamento = ? AND ano_faturamento = ? AND mecanico = ?'
            
            # Verificando a query antes da execução
            print(f"Executando query: {query} com os parâmetros ({mes}, {ano}, {mecanico})")
            
            self.cursor.execute(query, (mes, ano, mecanico))
            
            # Verificando o resultado obtido
            result = self.cursor.fetchall()
            print(f"Resultado da consulta: {result}")
            
            return result
        except Exception as e:
            # Adicionando print para verificar erros
            print(f"Erro ao executar a consulta: {e}")
            raise

    def ordens(self, mes, ano):
        try:
            # Adicionando prints para verificar os valores recebidos
            print(f"Mes: {mes}, Ano: {ano}")
            
            query = 'SELECT * FROM faturamento WHERE mes_faturamento = ? AND ano_faturamento = ?'
            
            # Verificando a query antes da execução
            print(f"Executando query: {query} com os parâmetros ({mes}, {ano})")
            
            self.cursor.execute(query, (mes, ano))
            
            # Verificando o resultado obtido
            result = self.cursor.fetchall()
            print(f"Resultado da consulta: {result}")
            
            return result
        except Exception as e:
            # Adicionando print para verificar erros
            print(f"Erro ao executar a consulta: {e}")
            raise

    def faturamento_ordens(self, mes, ano):
        try:
            logging.info(f"Consulta de faturamento iniciada para o mês {mes}/{ano}.")
            
            query = 'SELECT * FROM faturamento WHERE mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()
            
            if result:
                logging.info(f"Foram encontrados {len(result)} registros para o mês {mes}/{ano}.")
            else:
                logging.warning(f"Nenhum registro encontrado para o mês {mes}/{ano}.")
            
            return result
        except Exception as e:
            logging.error(f"Erro ao consultar faturamento para o mês {mes}/{ano}: {e}")
            return []
        
class DatabasePortal:
    def __init__(self):
        conn_str = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:gr7server.database.windows.net,1433;Database=admingr7;Uid=cristian;Pwd=viery2312@;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
        self.conn = pyodbc.connect(conn_str)
        self.cursor = self.conn.cursor()

    def cadastrar_faturamento(self, dados):
        try:
            query = 'INSERT INTO faturamento_portal VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
            self.cursor.execute(query, (dados['placa'], dados['modelo_veiculo'], dados['data_orcamento'], dados['data_faturamento'], dados['mes_faturamento'], dados['ano_faturamento'], dados['dias_servico'], dados['numero_os'], dados['companhia'], dados['conversao_ps'], dados['valor_pecas'], dados['valor_servicos'], dados['total_os'], dados['valor_revitalizacao'], dados['valor_aditivo'], dados['quantidade_litros'], dados['valor_fluido_sangria'], dados['valor_palheta'], dados['valor_limpeza_freios'], dados['valor_pastilha_parabrisa'],
                                dados['valor_filtro'], dados['valor_pneu'], dados['valor_bateria'], dados['modelo_bateria'], dados['lts_oleo_motor'], dados['valor_lt_oleo'], dados['marca_e_tipo_oleo'], dados['valor_p_meta'], dados['mecanico_servico'], dados['servico_filtro'],  dados['valor_em_dinheiro'], dados['valor_servico_freios'], dados['valor_servico_suspensao'], dados['valor_servico_injecao_ignicao'], dados['valor_servico_cabecote_motor_arr'], dados['valor_outros_servicos'], dados['valor_servicos_oleos'], dados['valor_servico_transmissao'], dados['usuario'], dados['obs']))
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
            query = 'SELECT * FROM companhias_portal ORDER BY CAST(cia AS NVARCHAR(MAX)) ASC;'
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

    def faturamento_dinheiro_ordens(self, mes, ano):
        try:
            query = 'SELECT * FROM faturamento_portal WHERE mes_faturamento = ? AND ano_faturamento = ?'
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

    def buscar_os_by_number(self, num_os):
        self.cursor.execute('SELECT * FROM faturamento_portal WHERE num_os = ?', (num_os,))
        result = self.cursor.fetchone()
        return result

    def faturamento_dinheiro_ordens(self, mes, ano):
        try:
            query = 'SELECT * FROM faturamento_portal WHERE mes_faturamento = ? AND ano_faturamento = ? ORDER BY data_faturamento ASC;'
            self.cursor.execute(query, mes, ano)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)
    
    def relatorio_filtro(self, mes, ano, mecanico):
        """
        Retorna os filtros e o filtro do mecânico para um determinado mês, ano e mecânico.

        Args:
            mes (str): Mês de referência para a consulta.
            ano (str): Ano de referência para a consulta.
            mecanico (str): Nome do mecânico para o filtro.

        Returns:
            list: Lista de resultados contendo o filtro e filtro_mecanico ou uma lista vazia se não encontrado.
        """
        try:
            # Logando o início da consulta
            logging.info(f"Iniciando consulta para relatório de filtro: mes={mes}, ano={ano}, mecanico={mecanico}")
            
            query = '''
                SELECT filtro, filtro_mecanico 
                FROM faturamento_portal 
                WHERE mes_faturamento = ? 
                AND ano_faturamento = ? 
                AND filtro_mecanico = ?
            '''
            self.cursor.execute(query, (mes, ano, mecanico))
            result = self.cursor.fetchall()

            # Verificando se o resultado é vazio
            if result:
                logging.info(f"Consulta bem-sucedida. {len(result)} resultados encontrados.")
                return result
            else:
                logging.warning(f"Nenhum resultado encontrado para o mecânico {mecanico} no mês {mes} e ano {ano}.")
                return []  # Retorna uma lista vazia se não encontrar resultados

        except Exception as e:
            # Logando o erro de exceção
            logging.error(f"Erro ao executar a consulta para o filtro com mes={mes}, ano={ano}, mecanico={mecanico}. Detalhes do erro: {e}")
            return []  # Retorna uma lista vazia em caso de erro
        
    def relatorio_revitalizacao(self, mes, ano, mecanico):
        """
        Retorna os filtros e o filtro do mecânico para um determinado mês, ano e mecânico.

        Args:
            mes (str): Mês de referência para a consulta.
            ano (str): Ano de referência para a consulta.
            mecanico (str): Nome do mecânico para o filtro.

        Returns:
            list: Lista de resultados contendo o filtro e filtro_mecanico ou uma lista vazia se não encontrado.
        """
        try:
            # Logando o início da consulta
            logging.info(f"Iniciando consulta para relatório de revitalizacoes: mes={mes}, ano={ano}, mecanico={mecanico}")
            
            query = '''
                SELECT revitalizacao, mecanico 
                FROM faturamento_portal 
                WHERE mes_faturamento = ? 
                AND ano_faturamento = ? 
                AND mecanico = ?
            '''
            self.cursor.execute(query, (mes, ano, mecanico))
            result = self.cursor.fetchall()

            # Verificando se o resultado é vazio
            if result:
                logging.info(f"Consulta bem-sucedida. {len(result)} resultados encontrados.")
                return result
            else:
                logging.warning(f"Nenhum resultado encontrado para o mecânico {mecanico} no mês {mes} e ano {ano}.")
                return []  # Retorna uma lista vazia se não encontrar resultados

        except Exception as e:
            # Logando o erro de exceção
            logging.error(f"Erro ao executar a consulta para a revitalizacao com mes={mes}, ano={ano}, mecanico={mecanico}. Detalhes do erro: {e}")
            return []  # Retorna uma lista vazia em caso de erro
        
    def detalhes_filtros(self, mes, ano, mecanico):
        try:
            # Adicionando prints para verificar os valores recebidos
            print(f"Mes: {mes}, Ano: {ano}, Mecânico: {mecanico}")
            
            query = 'SELECT * FROM faturamento_portal WHERE mes_faturamento = ? AND ano_faturamento = ? AND filtro_mecanico = ?'
            
            # Verificando a query antes da execução
            print(f"Executando query: {query} com os parâmetros ({mes}, {ano}, {mecanico})")
            
            self.cursor.execute(query, (mes, ano, mecanico))
            
            # Verificando o resultado obtido
            result = self.cursor.fetchall()
            print(f"Resultado da consulta: {result}")
            
            return result
        except Exception as e:
            # Adicionando print para verificar erros
            print(f"Erro ao executar a consulta: {e}")
            raise

    def detalhes_revitalizacao(self, mes, ano, mecanico):
        try:
            # Adicionando prints para verificar os valores recebidos
            print(f"Mes: {mes}, Ano: {ano}, Mecânico: {mecanico}")
            
            query = 'SELECT * FROM faturamento_portal WHERE mes_faturamento = ? AND ano_faturamento = ? AND mecanico = ?'
            
            # Verificando a query antes da execução
            print(f"Executando query: {query} com os parâmetros ({mes}, {ano}, {mecanico})")
            
            self.cursor.execute(query, (mes, ano, mecanico))
            
            # Verificando o resultado obtido
            result = self.cursor.fetchall()
            print(f"Resultado da consulta: {result}")
            
            return result
        except Exception as e:
            # Adicionando print para verificar erros
            print(f"Erro ao executar a consulta: {e}")
            raise

    def ordens(self, mes, ano):
        try:
            # Adicionando prints para verificar os valores recebidos
            print(f"Mes: {mes}, Ano: {ano}")
            
            query = 'SELECT * FROM faturamento_portal WHERE mes_faturamento = ? AND ano_faturamento = ?'
            
            # Verificando a query antes da execução
            print(f"Executando query: {query} com os parâmetros ({mes}, {ano})")
            
            self.cursor.execute(query, (mes, ano))
            
            # Verificando o resultado obtido
            result = self.cursor.fetchall()
            print(f"Resultado da consulta: {result}")
            
            return result
        except Exception as e:
            # Adicionando print para verificar erros
            print(f"Erro ao executar a consulta: {e}")
            raise

    def faturamento_ordens(self, mes, ano):
        try:
            logging.info(f"Consulta de faturamento iniciada para o mês {mes}/{ano}.")
            
            query = 'SELECT * FROM faturamento_portal WHERE mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()
            
            if result:
                logging.info(f"Foram encontrados {len(result)} registros para o mês {mes}/{ano}.")
            else:
                logging.warning(f"Nenhum registro encontrado para o mês {mes}/{ano}.")
            
            return result
        except Exception as e:
            logging.error(f"Erro ao consultar faturamento para o mês {mes}/{ano}: {e}")
            return []
