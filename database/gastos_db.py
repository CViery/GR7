from database import conection
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GastosDataBase:
    def __init__(self):
        self.db = conection.Database()
        self.cursor = self.db.cursor

    def set_nota(self, nota):
        try:
            # Verificação de dados obrigatórios
            if not all(key in nota for key in ['pago_por', 'emitido_para', 'status', 'boleto', 'nota', 'duplicata', 'fornecedor', 
                                            'data_emissao', 'dia_emissao', 'mes_emissao', 'ano_emissao', 'vencimentos', 
                                            'valor', 'despesa', 'obs', 'usuario','sub']):
                raise ValueError("Faltam dados obrigatórios no objeto 'nota'")

            # Log para exibir a nota recebida
            logging.info(f"Recebendo nota: {nota}")
            
            # Obter o último ID salvo
            logging.info("Executando consulta para obter o último ID...")
            self.cursor.execute("SELECT MAX(id) FROM notas")
            ultimo_id = self.cursor.fetchone()[0]
            logging.info(f"Último ID obtido: {ultimo_id}")
            
            # Definir o novo ID incrementando em 1 (se último_id for None, começamos com 1)
            novo_id = (ultimo_id + 1) if ultimo_id else 1
            logging.info(f"Novo ID definido: {novo_id}")
            
            # Preparar a query de inserção
            logging.info("Preparando a query de inserção...")
            query = '''
                INSERT INTO notas (pago_por, emitido_para, status, boleto, num_nota, duplicata, fornecedor, 
                                data_emissao, dia_emissao, mes_emissao, ano_emissao, vencimentos, valor, 
                                despesa, observacoes, usuario, sub_categorias) 
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            '''
            
            # Log para exibir os valores que serão inseridos
            valores = (
                nota['pago_por'], nota['emitido_para'], nota['status'], nota['boleto'], nota['nota'], 
                nota['duplicata'], nota['fornecedor'], nota['data_emissao'], nota['dia_emissao'], 
                nota['mes_emissao'], nota['ano_emissao'], nota['vencimentos'], nota['valor'], 
                nota['despesa'], nota['obs'], nota['usuario'], nota['sub']
            )
            logging.info(f"Valores a serem inseridos: {valores}")
            
            # Executar a query
            logging.info("Executando a query de inserção...")
            self.cursor.execute(query, valores)
            
            # Confirmar transação no banco de dados
            logging.info("Comitando transação no banco de dados...")
            self.db.conn.commit()
            
            # Mensagem de sucesso
            result = 'Nota Cadastrada'
            print(result)
            logging.info(result)
            return result

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao cadastrar a nota: {e}")
            return f"Erro: {e}"


    def set_boleto(self, boleto):
        try:
            # Verificar se todos os dados obrigatórios estão presentes
            if not all(key in boleto for key in ['num_nota', 'notas', 'fornecedor', 'vencimento', 'dia_vencimento', 
                                                'mes_vencimento', 'ano_vencimento', 'valor']):
                raise ValueError("Faltam dados obrigatórios no objeto 'boleto'")
            
            # Log para exibir o boleto recebido
            logging.info(f"Recebendo boleto: {boleto}")
            
            # Preparar a query de inserção
            query = 'INSERT INTO boletos (num_nota, notas, fornecedor, data_vencimento, dia_vencimento, mes_vencimento, ano_vencimento, valor) VALUES (?,?,?,?,?,?,?,?)'
            valores = (boleto['num_nota'], boleto['notas'], boleto['fornecedor'], boleto['vencimento'],
                    boleto['dia_vencimento'], boleto['mes_vencimento'], boleto['ano_vencimento'], boleto['valor'])
            
            # Log para exibir os valores que serão inseridos
            logging.info(f"Valores a serem inseridos: {valores}")
            
            # Executar a query
            self.cursor.execute(query, valores)
            
            # Confirmar transação no banco de dados
            self.db.conn.commit()
            
            # Mensagem de sucesso
            result = 'Boleto Cadastrado'
            logging.info(result)
            return result

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao cadastrar o boleto: {e}")
            return f"Erro: {e}"

    def get_all_gastos(self):
        """
        Recupera todos os registros da tabela 'notas' no banco de dados,
        ordenados pela data de emissão de forma crescente.

        Returns:
            list: Uma lista com todos os registros de 'notas' ou um erro, se ocorrer.
        """
        try:
            # Log para indicar início da consulta
            logging.info("Iniciando a consulta para recuperar todos os registros de 'notas'.")
            
            # Definindo a query
            query = 'SELECT * FROM notas ORDER BY data_emissao ASC;'
            
            # Executando a consulta
            self.cursor.execute(query)
            
            # Recuperando todos os resultados
            result = self.cursor.fetchall()
            
            # Log para indicar sucesso e a quantidade de registros recuperados
            logging.info(f"Consulta concluída. {len(result)} registros encontrados.")
            
            return result

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao recuperar os registros de 'notas': {e}")
            return f"Erro: {e}"

    def get_gastos_por_tipo(self, tipo, mes, ano):
        """
        Recupera os valores das notas filtradas pelo tipo de despesa, mês e ano.

        Args:
            tipo (str): O tipo de despesa (ex: 'Bateria', 'Mecânico', etc.)
            mes (int): O mês de emissão das notas (1-12)
            ano (int): O ano de emissão das notas (ex: 2024)

        Returns:
            list: Uma lista com os valores das despesas ou uma mensagem de erro, se ocorrer.
        """
        try:
            # Validando os parâmetros
            if not isinstance(tipo, str) or not tipo:
                raise ValueError("O parâmetro 'tipo' deve ser uma string não vazia.")
            if not isinstance(mes, str) or not mes:
                raise ValueError("O parâmetro 'mes' deve ser um valor inteiro entre 1 e 12.")
            if not isinstance(ano, str):
                raise ValueError("O parâmetro 'ano' deve ser um valor inteiro positivo.")
            
            # Log para indicar início da consulta
            logging.info(f"Iniciando consulta para recuperar valores de {tipo} no mês {mes} e ano {ano}.")
            
            # Query para buscar os valores
            query = 'SELECT valor FROM notas WHERE sub_categorias = ? AND mes_emissao = ? AND ano_emissao = ?'
            self.cursor.execute(query, (tipo, mes, ano))
            
            # Recuperando os resultados
            result = self.cursor.fetchall()
            
            # Log para indicar o número de resultados encontrados
            logging.info(f"{len(result)} registros encontrados para o tipo '{tipo}', mês {mes} e ano {ano}.")
            
            return result

        except ValueError as ve:
            # Log de erro para entradas inválidas
            logging.error(f"Erro de validação de parâmetros: {ve}")
            return f"Erro de validação: {ve}"
        except Exception as e:
            # Log de erro para falhas de execução
            logging.error(f"Erro ao buscar gastos por tipo: {e}")
            return f"Erro: {e}"


    def get_boletos(self):
        """
        Recupera todos os boletos cadastrados no banco de dados, ordenados pela data de vencimento.

        Returns:
            list: Lista de boletos, ou uma mensagem de erro se ocorrer algum problema na consulta.
        """
        try:
            # Log para indicar início da consulta
            logging.info("Iniciando consulta para recuperar todos os boletos.")

            # Consulta SQL para recuperar os boletos
            query = 'SELECT * FROM boletos ORDER BY data_vencimento ASC'
            self.cursor.execute(query)

            # Recuperando os resultados
            result = self.cursor.fetchall()

            # Log para indicar o número de registros encontrados
            logging.info(f"{len(result)} boletos encontrados.")

            return result

        except Exception as e:
            # Log de erro para falha na consulta
            logging.error(f"Erro ao buscar boletos: {e}")
            return f"Erro: {e}"
        
    def get_boletos_mes(self, mes, ano):
        """
        Recupera todos os boletos cadastrados no banco de dados, ordenados pela data de vencimento.

        Returns:
            list: Lista de boletos, ou uma mensagem de erro se ocorrer algum problema na consulta.
        """
        try:
            # Log para indicar início da consulta
            logging.info("Iniciando consulta para recuperar todos os boletos.")

            # Consulta SQL para recuperar os boletos
            query = 'SELECT * FROM boletos WHERE mes_vencimento = ? AND ano_vencimento = ? ORDER BY data_vencimento ASC'
            self.cursor.execute(query, (mes, ano))

            # Recuperando os resultados
            result = self.cursor.fetchall()

            # Log para indicar o número de registros encontrados
            logging.info(f"{len(result)} boletos encontrados.")

            return result

        except Exception as e:
            # Log de erro para falha na consulta
            logging.error(f"Erro ao buscar boletos: {e}")
            return f"Erro: {e}"

    def get_boletos_por_nota(self, num_nota):
        """
        Recupera todos os boletos associados a uma nota específica, ordenados pela data de vencimento.

        Args:
            num_nota (int): O número da nota para buscar os boletos associados.

        Returns:
            list: Lista de boletos encontrados, ou uma mensagem de erro caso algo dê errado.
        """
        try:
            # Log para indicar início da consulta
            logging.info(f"Iniciando consulta para recuperar boletos com num_nota = {num_nota}.")

            # Consulta SQL para buscar boletos pela num_nota
            query = 'SELECT * FROM boletos WHERE num_nota = ? ORDER BY data_vencimento ASC'
            self.cursor.execute(query, (num_nota,))

            # Recuperando os resultados
            result = self.cursor.fetchall()

            # Log para indicar quantos boletos foram encontrados
            logging.info(f"{len(result)} boletos encontrados para a num_nota = {num_nota}.")

            return result

        except Exception as e:
            # Log de erro caso algo dê errado
            logging.error(f"Erro ao buscar boletos para num_nota = {num_nota}: {e}")
            return f"Erro: {e}"

    def get_boletos_por_nota_valor(self, num_nota):
        """
        Recupera todos os valores dos boletos associados a uma nota específica, ordenados pela data de vencimento.

        Args:
            num_nota (int): O número da nota para buscar os boletos associados.

        Returns:
            list: Lista de valores dos boletos encontrados, ou uma mensagem de erro caso algo dê errado.
        """
        try:
            # Log para indicar início da consulta
            logging.info(f"Iniciando consulta para recuperar os valores dos boletos com num_nota = {num_nota}.")

            # Consulta SQL para buscar os valores dos boletos pela num_nota
            query = 'SELECT valor FROM boletos WHERE num_nota = ? ORDER BY data_vencimento ASC'
            self.cursor.execute(query, (num_nota,))

            # Recuperando os resultados
            result = self.cursor.fetchall()

            # Log para indicar quantos valores de boletos foram encontrados
            logging.info(f"{len(result)} valores de boletos encontrados para num_nota = {num_nota}.")

            return result

        except Exception as e:
            # Log de erro caso algo dê errado
            logging.error(f"Erro ao buscar valores dos boletos para num_nota = {num_nota}: {e}")
            return f"Erro: {e}"

    def get_boleto_by_day(self, dia, mes, ano):
        """
        Recupera todos os boletos com vencimento no dia, mês e ano especificados.

        Args:
            dia (int): O dia do vencimento do boleto.
            mes (int): O mês do vencimento do boleto.
            ano (int): O ano do vencimento do boleto.

        Returns:
            list: Lista de boletos encontrados com as informações de vencimento ou uma mensagem de erro.
        """
        try:
            # Log para indicar início da consulta
            logging.info(f"Iniciando consulta para recuperar os boletos com vencimento em {dia}/{mes}/{ano}.")

            # Consulta SQL para buscar os boletos pelo dia, mês e ano de vencimento
            query = 'SELECT * FROM boletos WHERE dia_vencimento = ? AND mes_vencimento = ? AND ano_vencimento = ?'
            self.cursor.execute(query, (dia, mes, ano))

            # Recuperando os resultados
            result = self.cursor.fetchall()

            # Log para indicar quantos boletos foram encontrados
            logging.info(f"{len(result)} boletos encontrados com vencimento em {dia}/{mes}/{ano}.")

            return result

        except Exception as e:
            # Log de erro caso algo dê errado
            logging.error(f"Erro ao buscar boletos com vencimento em {dia}/{mes}/{ano}: {e}")
            return f"Erro: {e}"

    def set_despesas(self, despesa):
        """
        Insere uma nova despesa na tabela 'despesa'.

        Args:
            despesa (str): O nome ou descrição da despesa a ser inserida no banco de dados.

        Returns:
            str: Mensagem de sucesso ou erro.
        """
        try:
            # Log para indicar que a inserção está sendo iniciada
            logging.info(f"Iniciando a inserção da despesa: {despesa}")

            # Consulta SQL para inserir a nova despesa
            query = 'INSERT INTO despesa (despesa) VALUES (?)'
            self.cursor.execute(query, (despesa,))

            # Commit da transação
            self.db.conn.commit()

            # Log para indicar sucesso na inserção
            logging.info(f"Despesa '{despesa}' inserida com sucesso.")
            return 'Despesa Cadastrada'

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao inserir a despesa '{despesa}': {e}")
            return f"Erro: {e}"

    def get_despesas(self):
        """
        Obtém todas as despesas registradas na tabela 'despesa', ordenadas por nome de despesa.

        Returns:
            list: Lista de tuplas com os registros das despesas.
        """
        try:
            # Log para indicar que a busca está sendo iniciada
            logging.info("Iniciando a busca por todas as despesas.")

            # Consulta SQL para obter todas as despesas ordenadas
            query = 'SELECT * FROM despesa ORDER BY despesa ASC;'
            self.cursor.execute(query)

            # Obtendo os resultados
            result = self.cursor.fetchall()

            # Log para indicar que a busca foi concluída com sucesso
            logging.info(f"{len(result)} despesas encontradas.")
            return result

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao buscar as despesas: {e}")
            return f"Erro: {e}"

    def get_valor_despesa(self, despesa, mes, ano):
        """
        Obtém o valor da despesa filtrado por tipo de despesa, mês e ano.

        Args:
            despesa (str): O nome da despesa.
            mes (int): O mês de emissão.
            ano (int): O ano de emissão.

        Returns:
            list: Lista de tuplas com os valores encontrados para a despesa no período especificado.
        """
        try:
            # Log para indicar que a busca está sendo iniciada
            logging.info(f"Iniciando a busca do valor da despesa '{despesa}' para o mês {mes} e ano {ano}.")

            # Consulta SQL para buscar o valor da despesa
            query = 'SELECT valor FROM notas WHERE despesa = ? AND mes_emissao = ? AND ano_emissao = ?'
            self.cursor.execute(query, (despesa, mes, ano))

            # Obtendo os resultados
            result = self.cursor.fetchall()

            # Log para indicar que a busca foi concluída
            if result:
                logging.info(f"{len(result)} valores encontrados para a despesa '{despesa}'.")
            else:
                logging.info(f"Nenhum valor encontrado para a despesa '{despesa}'.")

            return result

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao buscar o valor da despesa '{despesa}' para o mês {mes} e ano {ano}: {e}")
            return f"Erro: {e}"

    def get_all_notas(self):
        """
        Obtém todas as notas cadastradas no banco de dados, ordenadas pela data de emissão.

        Returns:
            list: Lista de tuplas com os dados de todas as notas.
        """
        try:
            # Log para indicar que a busca está sendo iniciada
            logging.info("Iniciando a busca de todas as notas.")

            # Consulta SQL para obter todas as notas
            query = 'SELECT * FROM notas ORDER BY data_emissao ASC;'
            self.cursor.execute(query)

            # Obtendo os resultados
            result = self.cursor.fetchall()

            # Log para indicar que a busca foi concluída
            logging.info(f"{len(result)} notas encontradas.")

            return result

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao buscar todas as notas: {e}")
            return f"Erro: {e}"

    def get_all_notas_mes(self, mes, ano):
        """
        Obtém todas as notas do mês e ano especificados, ordenadas pela data de emissão.

        Parameters:
            mes (int): Mês das notas a serem buscadas.
            ano (int): Ano das notas a serem buscadas.

        Returns:
            list: Lista de tuplas com os dados das notas filtradas por mês e ano.
        """
        try:
            # Log para indicar que a busca está sendo iniciada
            logging.info(f"Iniciando a busca de notas para o mês {mes} e ano {ano}.")

            # Consulta SQL para obter todas as notas para o mês e ano fornecidos
            query = 'SELECT * FROM notas WHERE mes_emissao = ? AND ano_emissao = ? ORDER BY data_emissao ASC;'
            self.cursor.execute(query, (mes, ano))

            # Obtendo os resultados
            result = self.cursor.fetchall()

            # Log para indicar que a busca foi concluída
            logging.info(f"{len(result)} notas encontradas para o mês {mes} e ano {ano}.")

            return result

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao buscar as notas para o mês {mes} e ano {ano}: {e}")
            return f"Erro: {e}"

    def obter_notas_filtradas(self, data_inicio=None, data_fim=None, fornecedor=None, despesa=None, obs=None):
        """
        Obtém as notas filtradas com base em diversos parâmetros.
        
        Parameters:
            data_inicio (str, optional): Data de início para filtro de emissão (formato: 'YYYY-MM-DD').
            data_fim (str, optional): Data de fim para filtro de emissão (formato: 'YYYY-MM-DD').
            fornecedor (str, optional): Nome do fornecedor para filtrar as notas.
            despesa (str, optional): Número da nota ou despesa para filtrar.
            obs (str, optional): Observações para filtrar as notas.

        Returns:
            list: Lista de tuplas com as notas filtradas.
        """
        try:
            # Iniciando a construção da query
            query = "SELECT * FROM notas"
            params = []
            filters = []

            # Filtro por data de início
            if data_inicio:
                filters.append("data_emissao >= ?")
                params.append(data_inicio)
            
            # Filtro por data de fim
            if data_fim:
                filters.append("data_emissao <= ?")
                params.append(data_fim)
            
            # Filtro por fornecedor
            if fornecedor:
                filters.append("fornecedor = ?")
                params.append(fornecedor)
            
            # Filtro por despesa (num_nota)
            if despesa:
                filters.append("num_nota = ?")
                params.append(despesa)
            
            # Filtro por observações
            if obs:
                filters.append("observacoes LIKE ?")
                params.append(f'%{obs}%')

            # Se houver filtros, adicionamos a cláusula WHERE
            if filters:
                query += " WHERE " + " AND ".join(filters)

            # Ordenando os resultados pela data de emissão
            query += " ORDER BY data_emissao ASC;"

            # Log para mostrar a consulta que será executada
            logging.info(f"Executando a consulta: {query}")
            logging.info(f"Parâmetros da consulta: {params}")

            # Executando a consulta
            self.cursor.execute(query, params)

            # Obtendo os resultados
            resultados = self.cursor.fetchall()

            # Log para indicar o número de resultados encontrados
            logging.info(f"{len(resultados)} notas encontradas.")

            return resultados

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao executar a consulta de notas filtradas: {e}")
            return f"Erro: {e}"

    def get_nota_por_numero(self, num_nota):
        """
        Obtém uma nota com base no número da nota.
        
        Parameters:
            num_nota (str): O número da nota a ser buscado.

        Returns:
            tuple: A tupla contendo os dados da nota, ou None se a nota não for encontrada.
        """
        try:
            # Preparando a consulta SQL
            query = 'SELECT * FROM notas WHERE num_nota = ?'

            # Log para mostrar a consulta que será executada
            logging.info(f"Executando a consulta: {query} com o parâmetro num_nota = {num_nota}")
            
            # Executando a consulta
            self.cursor.execute(query, (num_nota,))
            
            # Obtendo o resultado
            result = self.cursor.fetchone()

            # Log para indicar se a nota foi encontrada ou não
            if result:
                logging.info(f"Nota encontrada: {result}")
            else:
                logging.warning(f"Nota com num_nota = {num_nota} não encontrada.")

            return result

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao buscar a nota com num_nota = {num_nota}: {e}")
            return None

    def atualizar_notas(self, num_nota, numero_duplicata, datas):
        """
        Atualiza os dados de uma nota com base no número da nota.

        Atualiza o número da duplicata e a data de vencimento da nota especificada.

        Parameters:
            num_nota (str): O número da nota a ser atualizada.
            numero_duplicata (str): O número da duplicata a ser associado à nota.
            datas (str): As novas datas de vencimento associadas à nota.

        Returns:
            str: Mensagem de sucesso ou erro, dependendo do resultado da atualização.
        """
        try:
            # Preparando a consulta para atualizar a duplicata
            query1 = 'UPDATE notas SET duplicata = ? WHERE num_nota = ?'
            
            # Log para mostrar o que está sendo atualizado
            logging.info(f"Atualizando duplicata da nota {num_nota} para {numero_duplicata}")

            # Executando a atualização da duplicata
            self.cursor.execute(query1, (numero_duplicata, num_nota))
            
            # Preparando a consulta para atualizar a data de vencimento
            query2 = 'UPDATE notas SET vencimentos = ? WHERE num_nota = ?'
            
            # Log para mostrar o que está sendo atualizado
            logging.info(f"Atualizando data de vencimento da nota {num_nota} para {datas}")
            
            # Executando a atualização da data de vencimento
            self.cursor.execute(query2, (datas, num_nota))

            # Confirmando a transação no banco de dados
            self.db.conn.commit()

            # Log de sucesso
            logging.info(f"Notas com num_nota {num_nota} atualizadas com sucesso.")
            
            return 'Atualização realizada com sucesso.'

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao atualizar as notas com num_nota {num_nota}: {e}")
            return f"Erro ao atualizar a nota: {e}"

    def obter_boletos_filtrados(self, data_inicio=None, data_fim=None, fornecedor=None):
        """
        Obtém boletos filtrados com base em parâmetros específicos.

        Parâmetros:
            data_inicio (str): Data de início para o filtro de vencimento (formato 'YYYY-MM-DD').
            data_fim (str): Data de fim para o filtro de vencimento (formato 'YYYY-MM-DD').
            fornecedor (str): Nome do fornecedor para filtrar os boletos.

        Retorna:
            list: Lista de boletos que atendem aos filtros fornecidos.
        """
        try:
            # Construindo a query SQL
            query = "SELECT * FROM boletos"
            params = []
            filters = []

            if data_inicio:
                filters.append("data_vencimento >= ?")
                params.append(data_inicio)
                logging.info(f"Filtrando boletos com vencimento a partir de {data_inicio}")
            
            if data_fim:
                filters.append("data_vencimento <= ?")
                params.append(data_fim)
                logging.info(f"Filtrando boletos com vencimento até {data_fim}")
            
            if fornecedor:
                filters.append("fornecedor = ?")
                params.append(fornecedor)
                logging.info(f"Filtrando boletos do fornecedor: {fornecedor}")

            if filters:
                query += " WHERE " + " AND ".join(filters)

            query += " ORDER BY data_vencimento ASC;"

            # Executando a consulta
            logging.info(f"Executando consulta SQL: {query} com os parâmetros {params}")
            self.cursor.execute(query, params)
            resultados = self.cursor.fetchall()

            # Retornando os resultados
            logging.info(f"{len(resultados)} boletos encontrados.")
            return resultados

        except Exception as e:
            logging.error(f"Erro ao obter boletos filtrados: {e}")
            return f"Erro ao obter boletos filtrados: {e}"

    def get_valor_notas(self, mes, ano):
        """
        Obtém os valores das notas fiscais para um mês e ano específicos.

        Parâmetros:
            mes (int): Mês de emissão das notas (1 a 12).
            ano (int): Ano de emissão das notas.

        Retorna:
            list: Lista de valores das notas para o mês e ano informados.
        """
        try:
            # Construção da query SQL
            query = 'SELECT valor FROM notas WHERE mes_emissao = ? AND ano_emissao = ?'
            
            # Executando a consulta
            logging.info(f"Buscando valores das notas para o mês {mes} e ano {ano}.")
            self.cursor.execute(query, (mes, ano))
            
            # Obtendo os resultados
            result = self.cursor.fetchall()

            # Verificando se algum valor foi encontrado
            if result:
                logging.info(f"{len(result)} valores encontrados para o mês {mes} e ano {ano}.")
            else:
                logging.info(f"Nenhum valor encontrado para o mês {mes} e ano {ano}.")
            
            return result

        except Exception as e:
            # Tratamento de erro com log
            logging.error(f"Erro ao obter os valores das notas para o mês {mes} e ano {ano}: {e}")
            return f"Erro ao obter os valores das notas: {e}"

    def get_fornecedores(self):
        """
        Obtém todos os fornecedores cadastrados no banco de dados, ordenados pelo nome.

        Retorna:
            list: Lista de fornecedores ordenada por nome.
        """
        try:
            # Construção da query SQL
            query = 'SELECT * FROM fornecedores ORDER BY nome ASC;'

            # Executando a consulta
            logging.info("Buscando todos os fornecedores cadastrados.")
            self.cursor.execute(query)
            
            # Obtendo os resultados
            result = self.cursor.fetchall()

            # Verificando se algum fornecedor foi encontrado
            if result:
                logging.info(f"{len(result)} fornecedores encontrados.")
            else:
                logging.info("Nenhum fornecedor encontrado.")

            return result

        except Exception as e:
            # Tratamento de erro com log
            logging.error(f"Erro ao obter fornecedores: {e}")
            return f"Erro ao obter fornecedores: {e}"

    def get_recebedor(self):
        """
        Obtém todos os registros de 'emitido_para' (recebedores), ordenados pelo nome.

        Retorna:
            list: Lista de recebedores ordenada por nome.
        """
        try:
            # Construção da query SQL
            query = 'SELECT * FROM emitido_para ORDER BY nome ASC;'

            # Executando a consulta
            logging.info("Buscando todos os recebedores cadastrados.")
            self.cursor.execute(query)
            
            # Obtendo os resultados
            result = self.cursor.fetchall()

            # Verificando se algum recebedor foi encontrado
            if result:
                logging.info(f"{len(result)} recebedores encontrados.")
            else:
                logging.info("Nenhum recebedor encontrado.")

            return result

        except Exception as e:
            # Tratamento de erro com log
            logging.error(f"Erro ao obter recebedores: {e}")
            return f"Erro ao obter recebedores: {e}"


    def set_fornecedor(self, cnpj, nome):
        """
        Cadastra um novo fornecedor no banco de dados.

        Parâmetros:
            cnpj (str): O CNPJ do fornecedor.
            nome (str): O nome do fornecedor.

        Retorna:
            str: Mensagem de sucesso ou erro.
        """
        try:
            # Preparação da query SQL para inserção
            query = 'INSERT INTO fornecedores (cnpj, nome) VALUES (?,?)'

            # Log de inserção
            logging.info(f"Cadastrando fornecedor: {nome} com CNPJ: {cnpj}")
            
            # Executando a query
            self.cursor.execute(query, (cnpj, nome))
            
            # Confirmar a transação no banco de dados
            self.db.conn.commit()

            # Mensagem de sucesso
            logging.info(f"Fornecedor {nome} cadastrado com sucesso.")
            return f"Fornecedor {nome} cadastrado com sucesso."

        except Exception as e:
            # Tratamento de erro com log
            logging.error(f"Erro ao cadastrar fornecedor: {e}")
            return f"Erro ao cadastrar fornecedor: {e}"

    def set_oleo(self, oleo):
        """
        Cadastra um novo óleo no banco de dados.

        Parâmetro:
            oleo (str): O nome do óleo.

        Retorna:
            str: Mensagem de sucesso ou erro.
        """
        try:
            # Preparação da query SQL para inserção
            query = 'INSERT INTO oleos (nome) VALUES (?)'

            # Log de inserção
            logging.info(f"Cadastrando óleo: {oleo}")
            
            # Executando a query
            self.cursor.execute(query, (oleo,))
            
            # Confirmar a transação no banco de dados
            self.db.conn.commit()

            # Mensagem de sucesso
            logging.info(f"Óleo {oleo} cadastrado com sucesso.")
            return f"Óleo {oleo} cadastrado com sucesso."

        except Exception as e:
            # Tratamento de erro com log
            logging.error(f"Erro ao cadastrar óleo: {e}")
            return f"Erro ao cadastrar óleo: {e}"

    def cadastrar_companhia(self, companhia):
        """
        Cadastra uma nova companhia no banco de dados.

        Parâmetro:
            companhia (str): Nome da companhia a ser cadastrada.

        Retorna:
            str: Mensagem de sucesso ou erro.
        """
        try:
            # Preparação da query SQL para inserção
            query = 'INSERT INTO compahias (cia) VALUES (?)'

            # Log de inserção
            logging.info(f"Cadastrando companhia: {companhia}")
            
            # Executando a query
            self.cursor.execute(query, (companhia,))
            
            # Confirmar a transação no banco de dados
            self.db.conn.commit()

            # Mensagem de sucesso
            logging.info(f"Companhia {companhia} cadastrada com sucesso.")
            return f"Companhia {companhia} cadastrada com sucesso."

        except Exception as e:
            # Tratamento de erro com log
            logging.error(f"Erro ao cadastrar companhia: {e}")
            return f"Erro ao cadastrar companhia: {e}"

    def cadastrar_funcionario(self, id, funcionario):
        """
        Cadastra um novo funcionário na tabela de funcionários.

        Parâmetros:
            id (int): ID do funcionário.
            funcionario (str): Nome do funcionário a ser cadastrado.

        Retorna:
            str: Mensagem de sucesso ou erro.
        """
        try:
            # Preparação da query SQL para inserção
            query = 'INSERT INTO funcionarios (id, funcionario) VALUES (?, ?)'

            # Log de inserção
            logging.info(f"Cadastrando funcionário: {funcionario}, ID: {id}")
            
            # Executando a query
            self.cursor.execute(query, (id, funcionario))
            
            # Confirmar a transação no banco de dados
            self.db.conn.commit()

            # Mensagem de sucesso
            logging.info(f"Funcionário {funcionario} cadastrado com sucesso.")
            return f"Funcionário {funcionario} cadastrado com sucesso."

        except Exception as e:
            # Tratamento de erro com log
            logging.error(f"Erro ao cadastrar funcionário: {e}")
            return f"Erro ao cadastrar funcionário: {e}"

    def cadastrar_baterias(self, modelo):
        """
        Cadastra um novo modelo de bateria na tabela de baterias.

        Parâmetros:
            modelo (str): Modelo da bateria a ser cadastrado.

        Retorna:
            str: Mensagem de sucesso ou erro.
        """
        try:
            # Preparação da query SQL para inserção
            query = 'INSERT INTO baterias (modelo) VALUES (?)'

            # Log de inserção
            logging.info(f"Cadastrando bateria: {modelo}")
            
            # Passando o modelo como tupla
            self.cursor.execute(query, (modelo,))
            
            # Confirmar a transação no banco de dados
            self.db.conn.commit()

            # Mensagem de sucesso
            logging.info(f"Bateria modelo {modelo} cadastrada com sucesso.")
            return f"Bateria modelo {modelo} cadastrada com sucesso."

        except Exception as e:
            # Tratamento de erro com log
            logging.error(f"Erro ao cadastrar bateria: {e}")
            return f"Erro ao cadastrar bateria: {e}"
    
    def get_subcategorias(self, despesa):
        """
        Obtém as subcategorias associadas a uma categoria de despesa específica.

        Parâmetros:
            despesa (str): Nome ou ID da categoria de despesa para filtrar as subcategorias.

        Retorna:
            list: Lista de subcategorias que correspondem à categoria fornecida.
        """
        try:
            # Preparação da query SQL
            query = 'SELECT * FROM sub_categorias WHERE despesa = ?'

            # Log da operação
            logging.info(f"Buscando subcategorias para a despesa: {despesa}")
            
            # Executando a query
            self.cursor.execute(query, (despesa,))
            
            # Recuperando os resultados
            result = self.cursor.fetchall()

            # Log do resultado
            logging.info(f"Encontradas {len(result)} subcategorias para a despesa {despesa}.")
            
            return result

        except Exception as e:
            # Tratamento de erro com log
            logging.error(f"Erro ao buscar subcategorias para a despesa {despesa}: {e}")
            return f"Erro ao buscar subcategorias: {e}"

    def notas_por_subcategoria(self, subcategorias, mes, ano):
        try:
            query  = 'SELECT * FROM notas WHERE sub_categorias = ? AND mes_emissao = ? AND ano_emissao = ?'
            parametros = (subcategorias, mes, ano)
            self.cursor.execute(query, parametros)
            response = self.cursor.fetchall()
            return response
        except Exception as e:
            ...

    def notas_por_categoria(self, categorias, mes, ano):
        try:
            query  = 'SELECT * FROM notas WHERE despesa = ? AND mes_emissao = ? AND ano_emissao = ?'
            parametros = (categorias, mes, ano)
            self.cursor.execute(query, parametros)
            response = self.cursor.fetchall()
            print(f'Notas Categoria {categorias}: {response}')
            return response
        except Exception as e:
            ...

    def get_all_subcategorias(self):
        query = 'SELECT * from sub_categorias' 
        self.cursor.execute(query)
        response = self.cursor.fetchall()
        return response

class GastosDataBasePortal():
    def __init__(self):
        self.db = conection.Database()
        self.cursor = self.db.cursor

    def set_nota(self, nota):
        try:
            # Verificação de dados obrigatórios
            if not all(key in nota for key in ['pago_por', 'emitido_para', 'status', 'boleto', 'nota', 'duplicata', 'fornecedor', 
                                            'data_emissao', 'dia_emissao', 'mes_emissao', 'ano_emissao', 'vencimentos', 
                                            'valor', 'despesa', 'obs', 'usuario','sub']):
                raise ValueError("Faltam dados obrigatórios no objeto 'nota'")

            # Log para exibir a nota recebida
            logging.info(f"Recebendo nota: {nota}")
            
            # Obter o último ID salvo
            logging.info("Executando consulta para obter o último ID...")
            self.cursor.execute("SELECT MAX(id) FROM notas")
            ultimo_id = self.cursor.fetchone()[0]
            logging.info(f"Último ID obtido: {ultimo_id}")
            
            # Definir o novo ID incrementando em 1 (se último_id for None, começamos com 1)
            novo_id = (ultimo_id + 1) if ultimo_id else 1
            logging.info(f"Novo ID definido: {novo_id}")
            
            # Preparar a query de inserção
            logging.info("Preparando a query de inserção...")
            query = '''
                INSERT INTO notas_portal (pago_por, emitido_para, status, boleto, num_nota, duplicata, fornecedor, 
                                data_emissao, dia_emissao, mes_emissao, ano_emissao, vencimentos, valor, 
                                despesa, observacoes, usuario, sub_categorias) 
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            '''
            
            # Log para exibir os valores que serão inseridos
            valores = (
                nota['pago_por'], nota['emitido_para'], nota['status'], nota['boleto'], nota['nota'], 
                nota['duplicata'], nota['fornecedor'], nota['data_emissao'], nota['dia_emissao'], 
                nota['mes_emissao'], nota['ano_emissao'], nota['vencimentos'], nota['valor'], 
                nota['despesa'], nota['obs'], nota['usuario'], nota['sub']
            )
            logging.info(f"Valores a serem inseridos: {valores}")
            
            # Executar a query
            logging.info("Executando a query de inserção...")
            self.cursor.execute(query, valores)
            
            # Confirmar transação no banco de dados
            logging.info("Comitando transação no banco de dados...")
            self.db.conn.commit()
            
            # Mensagem de sucesso
            result = 'Nota Cadastrada'
            logging.info(result)
            return result

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao cadastrar a nota: {e}")
            return f"Erro: {e}"

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
            query = 'SELECT valor FROM notas_portal WHERE sub_categorias = ? AND mes_emissao = ? AND ano_emissao = ? '
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
            query = 'SELECT * FROM despesa ORDER BY despesa ASC;'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)

    def get_valor_despesa(self, despesa, mes, ano):
        try:
            query = 'SELECT valor FROM notas_portal WHERE despesa = ? AND mes_emissao = ? AND ano_emissao = ?'
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
        query = "SELECT * FROM boletos_portal "
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
            query = 'SELECT * FROM emitido_para_portal ORDER BY nome ASC;'
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

    def get_boletos_por_nota_valor(self, num_nota):
        try:
            query = 'SELECT valor FROM boletos_portal WHERE num_nota = ? ORDER BY data_vencimento ASC'
            self.cursor.execute(query, (num_nota,))
            result = self.cursor.fetchall()
            print(result)
            return result
        except Exception as e:
            print(e)
        
    def get_boletos_por_nota(self, num_nota):
        try:
            query = 'SELECT * FROM boletos_portal WHERE num_nota = ? ORDER BY data_vencimento ASC'
            self.cursor.execute(query, (num_nota,))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)
    
    
    def get_subcategorias(self, despesa):
            """
            Obtém as subcategorias associadas a uma categoria de despesa específica.

            Parâmetros:
                despesa (str): Nome ou ID da categoria de despesa para filtrar as subcategorias.

            Retorna:
                list: Lista de subcategorias que correspondem à categoria fornecida.
            """
            try:
                # Preparação da query SQL
                query = 'SELECT * FROM sub_categorias WHERE categoria = ?'

                # Log da operação
                logging.info(f"Buscando subcategorias para a despesa: {despesa}")
                
                # Executando a query
                self.cursor.execute(query, (despesa,))
                
                # Recuperando os resultados
                result = self.cursor.fetchall()

                # Log do resultado
                logging.info(f"Encontradas {len(result)} subcategorias para a despesa {despesa}.")
                
                return result

            except Exception as e:
                # Tratamento de erro com log
                logging.error(f"Erro ao buscar subcategorias para a despesa {despesa}: {e}")
                return f"Erro ao buscar subcategorias: {e}"

    def notas_por_subcategoria(self, subcategorias, mes, ano):
        try:
            query  = 'SELECT * FROM notas_portal WHERE sub_categorias = ? AND mes_emissao = ? AND ano_emissao = ?'
            parametros = (subcategorias, mes, ano)
            self.cursor.execute(query, parametros)
            response = self.cursor.fetchall()
            print(response)
            return response
        except Exception as e:
            ...

    def notas_por_categoria(self, categorias, mes, ano):
        try:
            query  = 'SELECT * FROM notas_portal WHERE despesa = ? AND mes_emissao = ? AND ano_emissao = ?'
            parametros = (categorias, mes, ano)
            self.cursor.execute(query, parametros)
            response = self.cursor.fetchall()
            return response
        except Exception as e:
            ...

    def get_all_subcategorias(self):
        query = 'SELECT * from sub_categorias' 
        self.cursor.execute(query)
        response = self.cursor.fetchall()
        return response

    def get_all_notas_mes(self, mes, ano):
        """
        Obtém todas as notas do mês e ano especificados, ordenadas pela data de emissão.

        Parameters:
            mes (int): Mês das notas a serem buscadas.
            ano (int): Ano das notas a serem buscadas.

        Returns:
            list: Lista de tuplas com os dados das notas filtradas por mês e ano.
        """
        try:
            # Log para indicar que a busca está sendo iniciada
            logging.info(f"Iniciando a busca de notas para o mês {mes} e ano {ano}.")

            # Consulta SQL para obter todas as notas para o mês e ano fornecidos
            query = 'SELECT * FROM notas_portal WHERE mes_emissao = ? AND ano_emissao = ? ORDER BY data_emissao ASC;'
            self.cursor.execute(query, (mes, ano))

            # Obtendo os resultados
            result = self.cursor.fetchall()

            # Log para indicar que a busca foi concluída
            logging.info(f"{len(result)} notas encontradas para o mês {mes} e ano {ano}.")

            return result

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao buscar as notas para o mês {mes} e ano {ano}: {e}")
            return f"Erro: {e}"
        
    def get_boletos_mes(self, mes, ano):
        """
        Recupera todos os boletos cadastrados no banco de dados, ordenados pela data de vencimento.

        Returns:
            list: Lista de boletos, ou uma mensagem de erro se ocorrer algum problema na consulta.
        """
        try:
            # Log para indicar início da consulta
            logging.info("Iniciando consulta para recuperar todos os boletos.")

            # Consulta SQL para recuperar os boletos
            query = 'SELECT * FROM boletos_portal WHERE mes_vencimento = ? AND ano_vencimento = ? ORDER BY data_vencimento ASC'
            self.cursor.execute(query, (mes, ano))

            # Recuperando os resultados
            result = self.cursor.fetchall()

            # Log para indicar o número de registros encontrados
            logging.info(f"{len(result)} boletos encontrados.")

            return result

        except Exception as e:
            # Log de erro para falha na consulta
            logging.error(f"Erro ao buscar boletos: {e}")
            return f"Erro: {e}"
        
class GastosDataBaseMorumbi:
    def __init__(self):
        self.db = conection.DatabaseMorumbi()
        self.cursor = self.db.cursor

    def set_nota(self, nota):
        try:
            # Verificação de dados obrigatórios
            if not all(key in nota for key in ['pago_por', 'emitido_para', 'status', 'boleto', 'nota', 'duplicata', 'fornecedor', 
                                            'data_emissao', 'dia_emissao', 'mes_emissao', 'ano_emissao', 'vencimentos', 
                                            'valor', 'despesa', 'obs', 'usuario','sub']):
                raise ValueError("Faltam dados obrigatórios no objeto 'nota'")

            # Log para exibir a nota recebida
            logging.info(f"Recebendo nota: {nota}")
            
            # Obter o último ID salvo
            logging.info("Executando consulta para obter o último ID...")
            self.cursor.execute("SELECT MAX(id) FROM notas_morumbi")
            ultimo_id = self.cursor.fetchone()[0]
            logging.info(f"Último ID obtido: {ultimo_id}")
            
            # Definir o novo ID incrementando em 1 (se último_id for None, começamos com 1)
            novo_id = (ultimo_id + 1) if ultimo_id else 1
            logging.info(f"Novo ID definido: {novo_id}")
            
            # Preparar a query de inserção
            logging.info("Preparando a query de inserção...")
            query = '''
                INSERT INTO notas_morumbi (pago_por, emitido_para, status, boleto, num_nota, duplicata, fornecedor, 
                                data_emissao, dia_emissao, mes_emissao, ano_emissao, vencimentos, valor, 
                                despesa, observacoes, usuario, sub_categorias) 
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            '''
            
            # Log para exibir os valores que serão inseridos
            valores = (
                nota['pago_por'], nota['emitido_para'], nota['status'], nota['boleto'], nota['nota'], 
                nota['duplicata'], nota['fornecedor'], nota['data_emissao'], nota['dia_emissao'], 
                nota['mes_emissao'], nota['ano_emissao'], nota['vencimentos'], nota['valor'], 
                nota['despesa'], nota['obs'], nota['usuario'], nota['sub']
            )
            logging.info(f"Valores a serem inseridos: {valores}")
            
            # Executar a query
            logging.info("Executando a query de inserção...")
            self.cursor.execute(query, valores)
            
            # Confirmar transação no banco de dados
            logging.info("Comitando transação no banco de dados...")
            self.db.conn.commit()
            
            # Mensagem de sucesso
            result = 'Nota Cadastrada'
            print(result)
            logging.info(result)
            return result

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao cadastrar a nota: {e}")
            return f"Erro: {e}"


    def set_boleto(self, boleto):
        try:
            # Verificar se todos os dados obrigatórios estão presentes
            if not all(key in boleto for key in ['num_nota', 'notas', 'fornecedor', 'vencimento', 'dia_vencimento', 
                                                'mes_vencimento', 'ano_vencimento', 'valor']):
                raise ValueError("Faltam dados obrigatórios no objeto 'boleto'")
            
            # Log para exibir o boleto recebido
            logging.info(f"Recebendo boleto: {boleto}")
            
            # Preparar a query de inserção
            query = 'INSERT INTO boletos_morumbi (num_nota, notas, fornecedor, data_vencimento, dia_vencimento, mes_vencimento, ano_vencimento, valor) VALUES (?,?,?,?,?,?,?,?)'
            valores = (boleto['num_nota'], boleto['notas'], boleto['fornecedor'], boleto['vencimento'],
                    boleto['dia_vencimento'], boleto['mes_vencimento'], boleto['ano_vencimento'], boleto['valor'])
            
            # Log para exibir os valores que serão inseridos
            logging.info(f"Valores a serem inseridos: {valores}")
            
            # Executar a query
            self.cursor.execute(query, valores)
            
            # Confirmar transação no banco de dados
            self.db.conn.commit()
            
            # Mensagem de sucesso
            result = 'Boleto Cadastrado'
            logging.info(result)
            return result

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao cadastrar o boleto: {e}")
            return f"Erro: {e}"

    def get_all_gastos(self):
        """
        Recupera todos os registros da tabela 'notas' no banco de dados,
        ordenados pela data de emissão de forma crescente.

        Returns:
            list: Uma lista com todos os registros de 'notas' ou um erro, se ocorrer.
        """
        try:
            # Log para indicar início da consulta
            logging.info("Iniciando a consulta para recuperar todos os registros de 'notas'.")
            
            # Definindo a query
            query = 'SELECT * FROM notas_morumbi ORDER BY data_emissao ASC;'
            
            # Executando a consulta
            self.cursor.execute(query)
            
            # Recuperando todos os resultados
            result = self.cursor.fetchall()
            
            # Log para indicar sucesso e a quantidade de registros recuperados
            logging.info(f"Consulta concluída. {len(result)} registros encontrados.")
            
            return result

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao recuperar os registros de 'notas': {e}")
            return f"Erro: {e}"

    def get_gastos_por_tipo(self, tipo, mes, ano):
        """
        Recupera os valores das notas filtradas pelo tipo de despesa, mês e ano.

        Args:
            tipo (str): O tipo de despesa (ex: 'Bateria', 'Mecânico', etc.)
            mes (int): O mês de emissão das notas (1-12)
            ano (int): O ano de emissão das notas (ex: 2024)

        Returns:
            list: Uma lista com os valores das despesas ou uma mensagem de erro, se ocorrer.
        """
        try:
            # Validando os parâmetros
            if not isinstance(tipo, str) or not tipo:
                raise ValueError("O parâmetro 'tipo' deve ser uma string não vazia.")
            if not isinstance(mes, str) or not mes:
                raise ValueError("O parâmetro 'mes' deve ser um valor inteiro entre 1 e 12.")
            if not isinstance(ano, str):
                raise ValueError("O parâmetro 'ano' deve ser um valor inteiro positivo.")
            
            # Log para indicar início da consulta
            logging.info(f"Iniciando consulta para recuperar valores de {tipo} no mês {mes} e ano {ano}.")
            
            # Query para buscar os valores
            query = 'SELECT valor FROM notas_morumbi WHERE sub_categorias = ? AND mes_emissao = ? AND ano_emissao = ?'
            self.cursor.execute(query, (tipo, mes, ano))
            
            # Recuperando os resultados
            result = self.cursor.fetchall()
            
            # Log para indicar o número de resultados encontrados
            logging.info(f"{len(result)} registros encontrados para o tipo '{tipo}', mês {mes} e ano {ano}.")
            
            return result

        except ValueError as ve:
            # Log de erro para entradas inválidas
            logging.error(f"Erro de validação de parâmetros: {ve}")
            return f"Erro de validação: {ve}"
        except Exception as e:
            # Log de erro para falhas de execução
            logging.error(f"Erro ao buscar gastos por tipo: {e}")
            return f"Erro: {e}"


    def get_boletos(self):
        """
        Recupera todos os boletos cadastrados no banco de dados, ordenados pela data de vencimento.

        Returns:
            list: Lista de boletos, ou uma mensagem de erro se ocorrer algum problema na consulta.
        """
        try:
            # Log para indicar início da consulta
            logging.info("Iniciando consulta para recuperar todos os boletos.")

            # Consulta SQL para recuperar os boletos
            query = 'SELECT * FROM boletos_morumbi ORDER BY data_vencimento ASC'
            self.cursor.execute(query)

            # Recuperando os resultados
            result = self.cursor.fetchall()

            # Log para indicar o número de registros encontrados
            logging.info(f"{len(result)} boletos encontrados.")

            return result

        except Exception as e:
            # Log de erro para falha na consulta
            logging.error(f"Erro ao buscar boletos: {e}")
            return f"Erro: {e}"
        
    def get_boletos_mes(self, mes, ano):
        """
        Recupera todos os boletos cadastrados no banco de dados, ordenados pela data de vencimento.

        Returns:
            list: Lista de boletos, ou uma mensagem de erro se ocorrer algum problema na consulta.
        """
        try:
            # Log para indicar início da consulta
            logging.info("Iniciando consulta para recuperar todos os boletos.")

            # Consulta SQL para recuperar os boletos
            query = 'SELECT * FROM boletos_morumbi WHERE mes_vencimento = ? AND ano_vencimento = ? ORDER BY data_vencimento ASC'
            self.cursor.execute(query, (mes, ano))

            # Recuperando os resultados
            result = self.cursor.fetchall()

            # Log para indicar o número de registros encontrados
            logging.info(f"{len(result)} boletos encontrados.")

            return result

        except Exception as e:
            # Log de erro para falha na consulta
            logging.error(f"Erro ao buscar boletos: {e}")
            return f"Erro: {e}"

    def get_boletos_por_nota(self, num_nota):
        """
        Recupera todos os boletos associados a uma nota específica, ordenados pela data de vencimento.

        Args:
            num_nota (int): O número da nota para buscar os boletos associados.

        Returns:
            list: Lista de boletos encontrados, ou uma mensagem de erro caso algo dê errado.
        """
        try:
            # Log para indicar início da consulta
            logging.info(f"Iniciando consulta para recuperar boletos com num_nota = {num_nota}.")

            # Consulta SQL para buscar boletos pela num_nota
            query = 'SELECT * FROM boletos_morumbi WHERE num_nota = ? ORDER BY data_vencimento ASC'
            self.cursor.execute(query, (num_nota,))

            # Recuperando os resultados
            result = self.cursor.fetchall()

            # Log para indicar quantos boletos foram encontrados
            logging.info(f"{len(result)} boletos encontrados para a num_nota = {num_nota}.")

            return result

        except Exception as e:
            # Log de erro caso algo dê errado
            logging.error(f"Erro ao buscar boletos para num_nota = {num_nota}: {e}")
            return f"Erro: {e}"

    def get_boletos_por_nota_valor(self, num_nota):
        """
        Recupera todos os valores dos boletos associados a uma nota específica, ordenados pela data de vencimento.

        Args:
            num_nota (int): O número da nota para buscar os boletos associados.

        Returns:
            list: Lista de valores dos boletos encontrados, ou uma mensagem de erro caso algo dê errado.
        """
        try:
            # Log para indicar início da consulta
            logging.info(f"Iniciando consulta para recuperar os valores dos boletos com num_nota = {num_nota}.")

            # Consulta SQL para buscar os valores dos boletos pela num_nota
            query = 'SELECT valor FROM boletos_morumbi WHERE num_nota = ? ORDER BY data_vencimento ASC'
            self.cursor.execute(query, (num_nota,))

            # Recuperando os resultados
            result = self.cursor.fetchall()

            # Log para indicar quantos valores de boletos foram encontrados
            logging.info(f"{len(result)} valores de boletos encontrados para num_nota = {num_nota}.")

            return result

        except Exception as e:
            # Log de erro caso algo dê errado
            logging.error(f"Erro ao buscar valores dos boletos para num_nota = {num_nota}: {e}")
            return f"Erro: {e}"

    def get_boleto_by_day(self, dia, mes, ano):
        """
        Recupera todos os boletos com vencimento no dia, mês e ano especificados.

        Args:
            dia (int): O dia do vencimento do boleto.
            mes (int): O mês do vencimento do boleto.
            ano (int): O ano do vencimento do boleto.

        Returns:
            list: Lista de boletos encontrados com as informações de vencimento ou uma mensagem de erro.
        """
        try:
            # Log para indicar início da consulta
            logging.info(f"Iniciando consulta para recuperar os boletos com vencimento em {dia}/{mes}/{ano}.")

            # Consulta SQL para buscar os boletos pelo dia, mês e ano de vencimento
            query = 'SELECT * FROM boletos_morumbi WHERE dia_vencimento = ? AND mes_vencimento = ? AND ano_vencimento = ?'
            self.cursor.execute(query, (dia, mes, ano))

            # Recuperando os resultados
            result = self.cursor.fetchall()

            # Log para indicar quantos boletos foram encontrados
            logging.info(f"{len(result)} boletos encontrados com vencimento em {dia}/{mes}/{ano}.")

            return result

        except Exception as e:
            # Log de erro caso algo dê errado
            logging.error(f"Erro ao buscar boletos com vencimento em {dia}/{mes}/{ano}: {e}")
            return f"Erro: {e}"

    def set_despesas(self, despesa):
        """
        Insere uma nova despesa na tabela 'despesa'.

        Args:
            despesa (str): O nome ou descrição da despesa a ser inserida no banco de dados.

        Returns:
            str: Mensagem de sucesso ou erro.
        """
        try:
            # Log para indicar que a inserção está sendo iniciada
            logging.info(f"Iniciando a inserção da despesa: {despesa}")

            # Consulta SQL para inserir a nova despesa
            query = 'INSERT INTO despesa (despesa) VALUES (?)'
            self.cursor.execute(query, (despesa,))

            # Commit da transação
            self.db.conn.commit()

            # Log para indicar sucesso na inserção
            logging.info(f"Despesa '{despesa}' inserida com sucesso.")
            return 'Despesa Cadastrada'

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao inserir a despesa '{despesa}': {e}")
            return f"Erro: {e}"

    def get_despesas(self):
        """
        Obtém todas as despesas registradas na tabela 'despesa', ordenadas por nome de despesa.

        Returns:
            list: Lista de tuplas com os registros das despesas.
        """
        try:
            # Log para indicar que a busca está sendo iniciada
            logging.info("Iniciando a busca por todas as despesas.")

            # Consulta SQL para obter todas as despesas ordenadas
            query = 'SELECT * FROM despesa ORDER BY despesa ASC;'
            self.cursor.execute(query)

            # Obtendo os resultados
            result = self.cursor.fetchall()

            # Log para indicar que a busca foi concluída com sucesso
            logging.info(f"{len(result)} despesas encontradas.")
            return result

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao buscar as despesas: {e}")
            return f"Erro: {e}"

    def get_valor_despesa(self, despesa, mes, ano):
        """
        Obtém o valor da despesa filtrado por tipo de despesa, mês e ano.

        Args:
            despesa (str): O nome da despesa.
            mes (int): O mês de emissão.
            ano (int): O ano de emissão.

        Returns:
            list: Lista de tuplas com os valores encontrados para a despesa no período especificado.
        """
        try:
            # Log para indicar que a busca está sendo iniciada
            logging.info(f"Iniciando a busca do valor da despesa '{despesa}' para o mês {mes} e ano {ano}.")

            # Consulta SQL para buscar o valor da despesa
            query = 'SELECT valor FROM notas_morumbi WHERE despesa = ? AND mes_emissao = ? AND ano_emissao = ?'
            self.cursor.execute(query, (despesa, mes, ano))

            # Obtendo os resultados
            result = self.cursor.fetchall()

            # Log para indicar que a busca foi concluída
            if result:
                logging.info(f"{len(result)} valores encontrados para a despesa '{despesa}'.")
            else:
                logging.info(f"Nenhum valor encontrado para a despesa '{despesa}'.")

            return result

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao buscar o valor da despesa '{despesa}' para o mês {mes} e ano {ano}: {e}")
            return f"Erro: {e}"

    def get_all_notas(self):
        """
        Obtém todas as notas cadastradas no banco de dados, ordenadas pela data de emissão.

        Returns:
            list: Lista de tuplas com os dados de todas as notas.
        """
        try:
            # Log para indicar que a busca está sendo iniciada
            logging.info("Iniciando a busca de todas as notas.")

            # Consulta SQL para obter todas as notas
            query = 'SELECT * FROM notas_morumbi ORDER BY data_emissao ASC;'
            self.cursor.execute(query)

            # Obtendo os resultados
            result = self.cursor.fetchall()

            # Log para indicar que a busca foi concluída
            logging.info(f"{len(result)} notas encontradas.")

            return result

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao buscar todas as notas: {e}")
            return f"Erro: {e}"

    def get_all_notas_mes(self, mes, ano):
        """
        Obtém todas as notas do mês e ano especificados, ordenadas pela data de emissão.

        Parameters:
            mes (int): Mês das notas a serem buscadas.
            ano (int): Ano das notas a serem buscadas.

        Returns:
            list: Lista de tuplas com os dados das notas filtradas por mês e ano.
        """
        try:
            # Log para indicar que a busca está sendo iniciada
            logging.info(f"Iniciando a busca de notas para o mês {mes} e ano {ano}.")

            # Consulta SQL para obter todas as notas para o mês e ano fornecidos
            query = 'SELECT * FROM notas_morumbi WHERE mes_emissao = ? AND ano_emissao = ? ORDER BY data_emissao ASC;'
            self.cursor.execute(query, (mes, ano))

            # Obtendo os resultados
            result = self.cursor.fetchall()

            # Log para indicar que a busca foi concluída
            logging.info(f"{len(result)} notas encontradas para o mês {mes} e ano {ano}.")

            return result

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao buscar as notas para o mês {mes} e ano {ano}: {e}")
            return f"Erro: {e}"

    def obter_notas_filtradas(self, data_inicio=None, data_fim=None, fornecedor=None, despesa=None, obs=None):
        """
        Obtém as notas filtradas com base em diversos parâmetros.
        
        Parameters:
            data_inicio (str, optional): Data de início para filtro de emissão (formato: 'YYYY-MM-DD').
            data_fim (str, optional): Data de fim para filtro de emissão (formato: 'YYYY-MM-DD').
            fornecedor (str, optional): Nome do fornecedor para filtrar as notas.
            despesa (str, optional): Número da nota ou despesa para filtrar.
            obs (str, optional): Observações para filtrar as notas.

        Returns:
            list: Lista de tuplas com as notas filtradas.
        """
        try:
            # Iniciando a construção da query
            query = "SELECT * FROM notas_morumbi"
            params = []
            filters = []

            # Filtro por data de início
            if data_inicio:
                filters.append("data_emissao >= ?")
                params.append(data_inicio)
            
            # Filtro por data de fim
            if data_fim:
                filters.append("data_emissao <= ?")
                params.append(data_fim)
            
            # Filtro por fornecedor
            if fornecedor:
                filters.append("fornecedor = ?")
                params.append(fornecedor)
            
            # Filtro por despesa (num_nota)
            if despesa:
                filters.append("num_nota = ?")
                params.append(despesa)
            
            # Filtro por observações
            if obs:
                filters.append("observacoes LIKE ?")
                params.append(f'%{obs}%')

            # Se houver filtros, adicionamos a cláusula WHERE
            if filters:
                query += " WHERE " + " AND ".join(filters)

            # Ordenando os resultados pela data de emissão
            query += " ORDER BY data_emissao ASC;"

            # Log para mostrar a consulta que será executada
            logging.info(f"Executando a consulta: {query}")
            logging.info(f"Parâmetros da consulta: {params}")

            # Executando a consulta
            self.cursor.execute(query, params)

            # Obtendo os resultados
            resultados = self.cursor.fetchall()

            # Log para indicar o número de resultados encontrados
            logging.info(f"{len(resultados)} notas encontradas.")

            return resultados

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao executar a consulta de notas filtradas: {e}")
            return f"Erro: {e}"

    def get_nota_por_numero(self, num_nota):
        """
        Obtém uma nota com base no número da nota.
        
        Parameters:
            num_nota (str): O número da nota a ser buscado.

        Returns:
            tuple: A tupla contendo os dados da nota, ou None se a nota não for encontrada.
        """
        try:
            # Preparando a consulta SQL
            query = 'SELECT * FROM notas_morumbi WHERE num_nota = ?'

            # Log para mostrar a consulta que será executada
            logging.info(f"Executando a consulta: {query} com o parâmetro num_nota = {num_nota}")
            
            # Executando a consulta
            self.cursor.execute(query, (num_nota,))
            
            # Obtendo o resultado
            result = self.cursor.fetchone()

            # Log para indicar se a nota foi encontrada ou não
            if result:
                logging.info(f"Nota encontrada: {result}")
            else:
                logging.warning(f"Nota com num_nota = {num_nota} não encontrada.")

            return result

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao buscar a nota com num_nota = {num_nota}: {e}")
            return None

    def atualizar_notas(self, num_nota, numero_duplicata, datas):
        """
        Atualiza os dados de uma nota com base no número da nota.

        Atualiza o número da duplicata e a data de vencimento da nota especificada.

        Parameters:
            num_nota (str): O número da nota a ser atualizada.
            numero_duplicata (str): O número da duplicata a ser associado à nota.
            datas (str): As novas datas de vencimento associadas à nota.

        Returns:
            str: Mensagem de sucesso ou erro, dependendo do resultado da atualização.
        """
        try:
            # Preparando a consulta para atualizar a duplicata
            query1 = 'UPDATE notas_morumbi SET duplicata = ? WHERE num_nota = ?'
            
            # Log para mostrar o que está sendo atualizado
            logging.info(f"Atualizando duplicata da nota {num_nota} para {numero_duplicata}")

            # Executando a atualização da duplicata
            self.cursor.execute(query1, (numero_duplicata, num_nota))
            
            # Preparando a consulta para atualizar a data de vencimento
            query2 = 'UPDATE notas_morumbi SET vencimentos = ? WHERE num_nota = ?'
            
            # Log para mostrar o que está sendo atualizado
            logging.info(f"Atualizando data de vencimento da nota {num_nota} para {datas}")
            
            # Executando a atualização da data de vencimento
            self.cursor.execute(query2, (datas, num_nota))

            # Confirmando a transação no banco de dados
            self.db.conn.commit()

            # Log de sucesso
            logging.info(f"Notas com num_nota {num_nota} atualizadas com sucesso.")
            
            return 'Atualização realizada com sucesso.'

        except Exception as e:
            # Log detalhado do erro
            logging.error(f"Erro ao atualizar as notas com num_nota {num_nota}: {e}")
            return f"Erro ao atualizar a nota: {e}"

    def obter_boletos_filtrados(self, data_inicio=None, data_fim=None, fornecedor=None):
        """
        Obtém boletos filtrados com base em parâmetros específicos.

        Parâmetros:
            data_inicio (str): Data de início para o filtro de vencimento (formato 'YYYY-MM-DD').
            data_fim (str): Data de fim para o filtro de vencimento (formato 'YYYY-MM-DD').
            fornecedor (str): Nome do fornecedor para filtrar os boletos.

        Retorna:
            list: Lista de boletos que atendem aos filtros fornecidos.
        """
        try:
            # Construindo a query SQL
            query = "SELECT * FROM boletos_morumbi"
            params = []
            filters = []

            if data_inicio:
                filters.append("data_vencimento >= ?")
                params.append(data_inicio)
                logging.info(f"Filtrando boletos com vencimento a partir de {data_inicio}")
            
            if data_fim:
                filters.append("data_vencimento <= ?")
                params.append(data_fim)
                logging.info(f"Filtrando boletos com vencimento até {data_fim}")
            
            if fornecedor:
                filters.append("fornecedor = ?")
                params.append(fornecedor)
                logging.info(f"Filtrando boletos do fornecedor: {fornecedor}")

            if filters:
                query += " WHERE " + " AND ".join(filters)

            query += " ORDER BY data_vencimento ASC;"

            # Executando a consulta
            logging.info(f"Executando consulta SQL: {query} com os parâmetros {params}")
            self.cursor.execute(query, params)
            resultados = self.cursor.fetchall()

            # Retornando os resultados
            logging.info(f"{len(resultados)} boletos encontrados.")
            return resultados

        except Exception as e:
            logging.error(f"Erro ao obter boletos filtrados: {e}")
            return f"Erro ao obter boletos filtrados: {e}"

    def get_valor_notas(self, mes, ano):
        """
        Obtém os valores das notas fiscais para um mês e ano específicos.

        Parâmetros:
            mes (int): Mês de emissão das notas (1 a 12).
            ano (int): Ano de emissão das notas.

        Retorna:
            list: Lista de valores das notas para o mês e ano informados.
        """
        try:
            # Construção da query SQL
            query = 'SELECT valor FROM notas_morumbi WHERE mes_emissao = ? AND ano_emissao = ?'
            
            # Executando a consulta
            logging.info(f"Buscando valores das notas para o mês {mes} e ano {ano}.")
            self.cursor.execute(query, (mes, ano))
            
            # Obtendo os resultados
            result = self.cursor.fetchall()

            # Verificando se algum valor foi encontrado
            if result:
                logging.info(f"{len(result)} valores encontrados para o mês {mes} e ano {ano}.")
            else:
                logging.info(f"Nenhum valor encontrado para o mês {mes} e ano {ano}.")
            
            return result

        except Exception as e:
            # Tratamento de erro com log
            logging.error(f"Erro ao obter os valores das notas para o mês {mes} e ano {ano}: {e}")
            return f"Erro ao obter os valores das notas: {e}"

    def get_fornecedores(self):
        """
        Obtém todos os fornecedores cadastrados no banco de dados, ordenados pelo nome.

        Retorna:
            list: Lista de fornecedores ordenada por nome.
        """
        try:
            # Construção da query SQL
            query = 'SELECT * FROM fornecedores_morumbi ORDER BY nome ASC;'

            # Executando a consulta
            logging.info("Buscando todos os fornecedores cadastrados.")
            self.cursor.execute(query)
            
            # Obtendo os resultados
            result = self.cursor.fetchall()

            # Verificando se algum fornecedor foi encontrado
            if result:
                logging.info(f"{len(result)} fornecedores encontrados.")
            else:
                logging.info("Nenhum fornecedor encontrado.")

            return result

        except Exception as e:
            # Tratamento de erro com log
            logging.error(f"Erro ao obter fornecedores: {e}")
            return f"Erro ao obter fornecedores: {e}"

    def get_recebedor(self):
        """
        Obtém todos os registros de 'emitido_para' (recebedores), ordenados pelo nome.

        Retorna:
            list: Lista de recebedores ordenada por nome.
        """
        try:
            # Construção da query SQL
            query = 'SELECT * FROM emitido_para_morumbi ORDER BY nome ASC;'

            # Executando a consulta
            logging.info("Buscando todos os recebedores cadastrados.")
            self.cursor.execute(query)
            
            # Obtendo os resultados
            result = self.cursor.fetchall()

            # Verificando se algum recebedor foi encontrado
            if result:
                logging.info(f"{len(result)} recebedores encontrados.")
            else:
                logging.info("Nenhum recebedor encontrado.")

            return result

        except Exception as e:
            # Tratamento de erro com log
            logging.error(f"Erro ao obter recebedores: {e}")
            return f"Erro ao obter recebedores: {e}"


    def set_fornecedor(self, cnpj, nome):
        """
        Cadastra um novo fornecedor no banco de dados.

        Parâmetros:
            cnpj (str): O CNPJ do fornecedor.
            nome (str): O nome do fornecedor.

        Retorna:
            str: Mensagem de sucesso ou erro.
        """
        try:
            # Preparação da query SQL para inserção
            query = 'INSERT INTO fornecedores_morumbi (cnpj, nome) VALUES (?,?)'

            # Log de inserção
            logging.info(f"Cadastrando fornecedor: {nome} com CNPJ: {cnpj}")
            
            # Executando a query
            self.cursor.execute(query, (cnpj, nome))
            
            # Confirmar a transação no banco de dados
            self.db.conn.commit()

            # Mensagem de sucesso
            logging.info(f"Fornecedor {nome} cadastrado com sucesso.")
            return f"Fornecedor {nome} cadastrado com sucesso."

        except Exception as e:
            # Tratamento de erro com log
            logging.error(f"Erro ao cadastrar fornecedor: {e}")
            return f"Erro ao cadastrar fornecedor: {e}"

    def set_oleo(self, oleo):
        """
        Cadastra um novo óleo no banco de dados.

        Parâmetro:
            oleo (str): O nome do óleo.

        Retorna:
            str: Mensagem de sucesso ou erro.
        """
        try:
            # Preparação da query SQL para inserção
            query = 'INSERT INTO oleos (nome) VALUES (?)'

            # Log de inserção
            logging.info(f"Cadastrando óleo: {oleo}")
            
            # Executando a query
            self.cursor.execute(query, (oleo,))
            
            # Confirmar a transação no banco de dados
            self.db.conn.commit()

            # Mensagem de sucesso
            logging.info(f"Óleo {oleo} cadastrado com sucesso.")
            return f"Óleo {oleo} cadastrado com sucesso."

        except Exception as e:
            # Tratamento de erro com log
            logging.error(f"Erro ao cadastrar óleo: {e}")
            return f"Erro ao cadastrar óleo: {e}"

    def cadastrar_companhia(self, companhia):
        """
        Cadastra uma nova companhia no banco de dados.

        Parâmetro:
            companhia (str): Nome da companhia a ser cadastrada.

        Retorna:
            str: Mensagem de sucesso ou erro.
        """
        try:
            # Preparação da query SQL para inserção
            query = 'INSERT INTO compahias (cia) VALUES (?)'

            # Log de inserção
            logging.info(f"Cadastrando companhia: {companhia}")
            
            # Executando a query
            self.cursor.execute(query, (companhia,))
            
            # Confirmar a transação no banco de dados
            self.db.conn.commit()

            # Mensagem de sucesso
            logging.info(f"Companhia {companhia} cadastrada com sucesso.")
            return f"Companhia {companhia} cadastrada com sucesso."

        except Exception as e:
            # Tratamento de erro com log
            logging.error(f"Erro ao cadastrar companhia: {e}")
            return f"Erro ao cadastrar companhia: {e}"

    def cadastrar_funcionario(self, id, funcionario):
        """
        Cadastra um novo funcionário na tabela de funcionários.

        Parâmetros:
            id (int): ID do funcionário.
            funcionario (str): Nome do funcionário a ser cadastrado.

        Retorna:
            str: Mensagem de sucesso ou erro.
        """
        try:
            # Preparação da query SQL para inserção
            query = 'INSERT INTO funcionarios_morumbi (id, funcionario) VALUES (?, ?)'

            # Log de inserção
            logging.info(f"Cadastrando funcionário: {funcionario}, ID: {id}")
            
            # Executando a query
            self.cursor.execute(query, (id, funcionario))
            
            # Confirmar a transação no banco de dados
            self.db.conn.commit()

            # Mensagem de sucesso
            logging.info(f"Funcionário {funcionario} cadastrado com sucesso.")
            return f"Funcionário {funcionario} cadastrado com sucesso."

        except Exception as e:
            # Tratamento de erro com log
            logging.error(f"Erro ao cadastrar funcionário: {e}")
            return f"Erro ao cadastrar funcionário: {e}"

    def cadastrar_baterias(self, modelo):
        """
        Cadastra um novo modelo de bateria na tabela de baterias.

        Parâmetros:
            modelo (str): Modelo da bateria a ser cadastrado.

        Retorna:
            str: Mensagem de sucesso ou erro.
        """
        try:
            # Preparação da query SQL para inserção
            query = 'INSERT INTO baterias (modelo) VALUES (?)'

            # Log de inserção
            logging.info(f"Cadastrando bateria: {modelo}")
            
            # Passando o modelo como tupla
            self.cursor.execute(query, (modelo,))
            
            # Confirmar a transação no banco de dados
            self.db.conn.commit()

            # Mensagem de sucesso
            logging.info(f"Bateria modelo {modelo} cadastrada com sucesso.")
            return f"Bateria modelo {modelo} cadastrada com sucesso."

        except Exception as e:
            # Tratamento de erro com log
            logging.error(f"Erro ao cadastrar bateria: {e}")
            return f"Erro ao cadastrar bateria: {e}"
    
    def get_subcategorias(self, despesa):
        """
        Obtém as subcategorias associadas a uma categoria de despesa específica.

        Parâmetros:
            despesa (str): Nome ou ID da categoria de despesa para filtrar as subcategorias.

        Retorna:
            list: Lista de subcategorias que correspondem à categoria fornecida.
        """
        try:
            # Preparação da query SQL
            query = 'SELECT * FROM sub_categorias WHERE despesa = ?'

            # Log da operação
            logging.info(f"Buscando subcategorias para a despesa: {despesa}")
            
            # Executando a query
            self.cursor.execute(query, (despesa,))
            
            # Recuperando os resultados
            result = self.cursor.fetchall()

            # Log do resultado
            logging.info(f"Encontradas {len(result)} subcategorias para a despesa {despesa}.")
            
            return result

        except Exception as e:
            # Tratamento de erro com log
            logging.error(f"Erro ao buscar subcategorias para a despesa {despesa}: {e}")
            return f"Erro ao buscar subcategorias: {e}"

    def notas_por_subcategoria(self, subcategorias, mes, ano):
        try:
            query  = 'SELECT * FROM notas WHERE sub_categorias = ? AND mes_emissao = ? AND ano_emissao = ?'
            parametros = (subcategorias, mes, ano)
            self.cursor.execute(query, parametros)
            response = self.cursor.fetchall()
            return response
        except Exception as e:
            ...

    def notas_por_categoria(self, categorias, mes, ano):
        try:
            query  = 'SELECT * FROM notas_morumbi WHERE despesa = ? AND mes_emissao = ? AND ano_emissao = ?'
            parametros = (categorias, mes, ano)
            self.cursor.execute(query, parametros)
            response = self.cursor.fetchall()
            print(f'Notas Categoria {categorias}: {response}')
            return response
        except Exception as e:
            ...

    def get_all_subcategorias(self):
        query = 'SELECT * from sub_categorias' 
        self.cursor.execute(query)
        response = self.cursor.fetchall()
        return response
