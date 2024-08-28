import requests
from database import conection, gastos_db
from services import faturamento, dados_notas


class Utills:
    def __init__(self):
        self.db = conection.Database()
        self.db_gastos = gastos_db.GastosDataBase()
        self.db_dados_notas = dados_notas.DadosGastos()
        self.faturamento_db = faturamento.Faturamento()

    def formatar_moeda(self, valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def faturamento_pecas(self, mes, ano):
        try:
            # Obtém os dados de faturamento de peças para o mês e ano fornecidos
            dados = self.db.faturamento_pecas(mes, ano)

            # Extrai os valores dos dados
            valores = [valor[0] for valor in dados]

            # Calcula a soma dos valores
            valor_soma = sum(valores)

            # Formata o valor total como moeda
            valor_total = self.formatar_moeda(valor_soma)

            return valor_total

        except Exception as e:
            # Imprime a exceção com uma mensagem clara
            print(f"Ocorreu um erro ao calcular o faturamento de peças: {e}")
            return None

    def faturamento_servicos(self, mes, ano):
        try:
            # Obtém os dados de faturamento de serviços para o mês e ano fornecidos
            dados = self.db.faturamento_servicos(mes, ano)

            # Extrai os valores dos dados
            valores = [valor[0] for valor in dados]

            # Calcula a soma dos valores
            valor_soma = sum(valores)

            # Formata o valor total como moeda
            valor_total = self.formatar_moeda(valor_soma)

            return valor_total

        except Exception as e:
            # Imprime a exceção com uma mensagem clara
            print(
                f"Ocorreu um erro ao calcular o faturamento de serviços: {e}")
            return None

    def primeira_meta(self, mes, ano):
        try:
            # Obtém os dados de faturamento para o mês e ano fornecidos
            valor_meta = self.db.faturamento_mes_meta(mes, ano)

            # Extrai os valores dos dados
            valores = [valor[0] for valor in valor_meta]

            # Calcula o valor total vendido
            valor_vendido = sum(valores)

            # Define a meta
            meta = 180000.00

            # Calcula quanto falta para atingir a meta
            falta = meta - valor_vendido

            # Verifica se a meta foi atingida
            if falta <= 0:
                valor_total = 'Primeira meta Atingida'
            else:
                valor_total = self.formatar_moeda(falta)

            return valor_total

        except Exception as e:
            # Imprime a exceção com uma mensagem clara
            print(f"Ocorreu um erro ao calcular a primeira meta: {e}")
            return None

    def segunda_meta(self, mes, ano):
        try:
            # Obtém os dados de faturamento para o mês e ano fornecidos
            valor_meta = self.db.faturamento_mes_meta(mes, ano)

            # Extrai os valores dos dados
            valores = [valor[0] for valor in valor_meta]

            # Calcula o valor total vendido
            valor_vendido = sum(valores)

            # Define a meta
            meta = 220000.00

            # Calcula quanto falta para atingir a meta
            falta = meta - valor_vendido

            # Verifica se a meta foi atingida
            if falta <= 0:
                valor_total = 'Segunda meta Atingida'
            else:
                valor_total = self.formatar_moeda(falta)

            return valor_total

        except Exception as e:
            # Imprime a exceção com uma mensagem clara
            print(f"Ocorreu um erro ao calcular a segunda meta: {e}")
            return None

    def ticket(self, mes, ano):
        try:
            # Obtém os dados de faturamento para o mês e ano fornecidos
            dados = self.db.faturamento_mes_meta(mes, ano)

            # Extrai os valores dos dados
            valores = [dado[0] for dado in dados]

            # Verifica se há valores para evitar divisão por zero
            if not valores:
                print(
                    "Nenhum dado de faturamento encontrado para o mês e ano fornecidos.")
                return "R$ 0,00"

            # Calcula a soma dos valores
            soma = sum(valores)

            # Calcula a quantidade de valores
            qntd = len(valores)

            # Calcula o valor médio
            valor = soma / qntd

            # Formata o valor médio como moeda
            result = self.formatar_moeda(valor)
            

            return result

        except Exception as e:
            # Imprime a exceção com uma mensagem clara
            print(f"Ocorreu um erro ao calcular o ticket médio: {e}")
            return None

    def passagens(self, mes, ano):
        try:
            # Obtém os dados de faturamento para o mês e ano fornecidos
            dados = self.db.faturamento_mes(mes, ano)

            # Extrai os valores dos dados
            valores = [dado[0] for dado in dados]

            # Calcula a quantidade de valores
            qntd = len(valores)

            # Imprime a quantidade de passagens
        

            return qntd

        except Exception as e:
            # Imprime a exceção com uma mensagem clara
            print(f"Ocorreu um erro ao obter as passagens: {e}")
            return None

    def despesas(self):
        try:
            # Inicializa uma lista para armazenar as despesas
            despesas = []

            # Obtém os dados de despesas do banco de dados
            dados = self.db_gastos.get_despesas()

            # Adiciona cada despesa à lista
            despesas = [dado[0] for dado in dados]

            return despesas

        except Exception as e:
            # Imprime a exceção com uma mensagem clara
            print(f"Ocorreu um erro ao obter as despesas: {e}")
            return None

    def fornecedores(self):
        try:
            # Inicializa uma lista para armazenar os fornecedores
            fornecedores = []

            # Obtém os dados de fornecedores do banco de dados
            dados = self.db_gastos.get_fornecedores()

            # Adiciona cada fornecedor à lista (considerando o segundo elemento de cada tupla)
            fornecedores = [dado[1] for dado in dados]

            return fornecedores

        except Exception as e:
            # Imprime a exceção com uma mensagem clara
            print(f"Ocorreu um erro ao obter os fornecedores: {e}")
            return None

    def gastos(self, mes, ano):
        try:
            # Obtém o valor total de gastos para o mês e ano fornecidos
            valor = self.db_dados_notas.valor_gastos(mes, ano)
            valor_moeda = self.formatar_moeda(valor)
            return valor_moeda
        except Exception as e:
            # Imprime a exceção com uma mensagem clara
            print(f"Ocorreu um erro ao obter os gastos para {mes}/{ano}: {e}")
            return None

    def porcentagem_faturamento(self, mes, ano):
        # Obtenha os dados dos gastos
        dados_gastos = self.db_gastos.get_valor_notas(mes, ano)
        valores = [dado[0] for dado in dados_gastos]
        gasto = sum(valores)

        # Obtenha os dados do faturamento
        dados_faturamento = self.db.faturamento_mes(mes, ano)

        valores_fat = [dado[0] for dado in dados_faturamento]
        faturamento = sum(valores_fat)

        # Verifique se o faturamento é zero para evitar divisão por zero
        if faturamento == 0:
            return 0

        # Calcule a porcentagem
        calculo = (gasto / faturamento) * 100
        dados = f'{calculo:.2f} %'
        return dados

    def porcentagem_gastos_pecas(self, mes, ano):
        try:
            # Obtém os dados de gastos com peças para o mês e ano fornecidos
            dados_pecas = self.db_gastos.get_gastos_por_tipo('PEÇAS', mes, ano)
            valores_gastos = [dado[0] for dado in dados_pecas]
            gasto = sum(valores_gastos)

            # Obtém os dados de faturamento de peças para o mês e ano fornecidos
            dados_faturamento = self.db.faturamento_pecas(mes, ano)
            valores_faturamento = [dado[0] for dado in dados_faturamento]
            faturamento = sum(valores_faturamento)

            # Calcula a porcentagem dos gastos em relação ao faturamento
            if faturamento == 0:
                return '0.00 %'

            calculo = (gasto / faturamento) * 100
            dados = f'{calculo:.2f} %'

            return dados

        except Exception as e:
            # Imprime a exceção com uma mensagem clara
            print(
                f"Ocorreu um erro ao calcular a porcentagem de gastos com peças: {e}")
            return None

    def gastos_pecas(self, mes, ano):
        try:
            # Obtém os dados de gastos com peças para o mês e ano fornecidos
            dados_pecas = self.db_gastos.get_gastos_por_tipo('PEÇAS', mes, ano)

            # Extrai os valores de gastos
            valores_gastos = [dado[0] for dado in dados_pecas]

            # Calcula o total de gastos
            gasto = sum(valores_gastos)

            # Formata o total de gastos como moeda
            valor_total = self.formatar_moeda(gasto)

            return valor_total

        except Exception as e:
            # Imprime a exceção com uma mensagem clara
            print(f"Ocorreu um erro ao calcular os gastos com peças: {e}")
            return None

    def valor_dinheiro(self, mes, ano):
        try:
            # Obtém os dados de faturamento em dinheiro para o mês e ano fornecidos
            dados_dinheiro = self.db.faturamento_dinheiro(mes, ano)

            # Extrai os valores de faturamento
            valores_dinheiro = [dado[0] for dado in dados_dinheiro]

            # Calcula o total de faturamento em dinheiro
            gasto = sum(valores_dinheiro)

            # Formata o total de faturamento como moeda
            valor_total = self.formatar_moeda(gasto)

            return valor_total

        except Exception as e:
            # Imprime a exceção com uma mensagem clara
            print(
                f"Ocorreu um erro ao calcular o faturamento em dinheiro: {e}")
            return None

    def emitido_para(self):
        try:
            # Obtém os dados de recebedores do banco de dados
            dados = self.db_gastos.get_recebedor()

            # Extrai a lista de recebedores
            lista = [dado[0] for dado in dados]

            return lista

        except Exception as e:
            # Imprime a exceção com uma mensagem clara
            print(f"Ocorreu um erro ao obter a lista de recebedores: {e}")
            return None

    def cadastrar_fornecedor(self, dados):
        try:
            # Verifica se todos os dados necessários estão presentes
            if 'cnpj' not in dados or 'nome_empresa' not in dados:
                raise ValueError(
                    "Dados incompletos: 'cnpj' e 'nome_empresa' são obrigatórios.")

            CNPJ = dados['cnpj']
            razao = dados['nome_empresa']

            # Cadastra o fornecedor no banco de dados
            self.db_gastos.set_fornecedor(CNPJ, razao)

            print(f"Fornecedor '{razao}' com CNPJ '{
                  CNPJ}' cadastrado com sucesso.")

        except ValueError as ve:
            # Trata erros de validação de dados
            print(f"Erro de validação: {ve}")

        except Exception as e:
            # Trata outros erros
            print(f"Ocorreu um erro ao cadastrar o fornecedor: {e}")

    def formatar_moeda(self, valor):

        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class Utills_portal():
    def __init__(self):
        self.db = conection.DatabasePortal()
        self.db_gastos = gastos_db.GastosDataBasePortal()
        self.db_dados_notas = dados_notas.DadosGastosPortal()
        self.faturamento_db = faturamento.FaturamentoPortal()

    def formatar_moeda(self, valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def faturamento_pecas(self, mes, ano):
        try:

            dados = self.db.faturamento_pecas(mes, ano)
            valores = [valor[0] for valor in dados]
            valor_soma = sum(valores)
            valor_total = self.formatar_moeda(valor_soma)
            return valor_total
        except Exception as e:
            print(e)

    def faturamento_servicos(self, mes, ano):
        try:

            dados = self.db.faturamento_servicos(mes, ano)
            valores = [valor[0] for valor in dados]
            valor_soma = sum(valores)
            valor_total = self.formatar_moeda(valor_soma)
            return valor_total
        except Exception as e:
            print(e)

    def primeira_meta(self, mes, ano):
        try:
            valor_meta = self.db.faturamento_mes_meta(mes, ano)
            valores = [valor[0] for valor in valor_meta]
            valor_vendido = sum(valores)
            meta = 0
            falta = meta - valor_vendido
            if falta <= 0:
                valor_total = 'Primeira meta Atingida'
            else:
                valor_total = self.formatar_moeda(falta)

            return valor_total
        except Exception as e:
            print(e)

    def segunda_meta(self, mes, ano):
        try:
            valor_meta = self.db.faturamento_mes_meta(mes, ano)
            valores = [valor[0] for valor in valor_meta]
            valor_vendido = sum(valores)
            meta = 220000.00
            falta = meta - valor_vendido
            if falta <= 0:
                valor_total = 'Segunda meta Atingida'
            else:
                valor_total = self.formatar_moeda(falta)
            return valor_total
        except Exception as e:
            print(e)

    def despesas(self):
        try:
            despesas = []
            dados = self.db_gastos.get_despesas()
            for dado in dados:
                despesas.append(dado[0])
            return despesas
        except Exception as e:
            print(e)

    def fornecedores(self):
        try:
            fornecedores = []
            dados = self.db_gastos.get_fornecedores()
            for dado in dados:
                fornecedores.append(dado[1])
            return fornecedores
        except Exception as e:
            print(e)

    def gastos(self, mes, ano):
        valor = self.db_dados_notas.valor_gastos(mes, ano)
        return valor

    def porcentagem_faturamento(self, mes, ano):
        # Obtenha os dados dos gastos
        dados_gastos = self.db_gastos.get_valor_notas(mes, ano)
        valores = [dado[0] for dado in dados_gastos]
        gasto = sum(valores)

        # Obtenha os dados do faturamento
        dados_faturamento = self.db.faturamento_mes(mes, ano)

        valores_fat = [dado[0] for dado in dados_faturamento]
        faturamento = sum(valores_fat)

        # Verifique se o faturamento é zero para evitar divisão por zero
        if faturamento == 0:
            msg = f'{0} %'
            return msg

        # Calcule a porcentagem
        calculo = (gasto / faturamento) * 100
        dados = f'{calculo:.2f} %'
        return dados

    def porcentagem_gastos_pecas(self, mes, ano):
        dados_peças = self.db_gastos.get_gatos_por_tipo('PEÇAS', mes, ano)
        valores_gastos = [dado[0] for dado in dados_peças]
        gasto = sum(valores_gastos)
        dados_faturamento = self.db.faturamento_pecas(mes, ano)
        valores_faturamento = [dado[0] for dado in dados_faturamento]
        faturamento = sum(valores_faturamento)
        if faturamento == 0:
            msg = f'{0} %'
            return msg

        calculo = (gasto / faturamento) * 100
        dados = f'{calculo:.2f} %'
        return dados

    def gastos_pecas(self, mes, ano):

        dados_pecas = self.db_gastos.get_gatos_por_tipo('PEÇAS', mes, ano)
        valores_gastos = [dado[0] for dado in dados_pecas]
        gasto = sum(valores_gastos)
        valor_total = self.formatar_moeda(gasto)
        return valor_total

    def valor_dinheiro(self, mes, ano):
        dados_dinheiro = self.db.faturamento_dinheiro(mes, ano)
        valores_dinheiro = [dado[0] for dado in dados_dinheiro]
        gasto = sum(valores_dinheiro)
        valor_total = self.formatar_moeda(gasto)
        return valor_total

    def emitido_para(self):
        dados = self.db_gastos.get_recebedor()
        lista = [dado[0] for dado in dados]
        return lista

    def cadastrar_fornecedor(self, dados):
        CNPJ = dados['cnpj']
        razao = dados['nome_empresa']
        self.db_gastos.set_fornecedor(CNPJ, razao)

        print(f"Ocorreu um erro ao calcular a segunda meta: {e}")
        return None

    def ticket(self, mes, ano):
        try:
            # Obtém os dados de faturamento para o mês e ano fornecidos
            dados = self.db.faturamento_mes_meta(mes, ano)

            # Extrai os valores dos dados
            valores = [dado[0] for dado in dados]

            # Verifica se há valores para evitar divisão por zero
            if not valores:
                print(
                    "Nenhum dado de faturamento encontrado para o mês e ano fornecidos.")
                return "R$ 0,00"

            # Calcula a soma dos valores
            soma = sum(valores)

            # Calcula a quantidade de valores
            qntd = len(valores)

            # Calcula o valor médio
            valor = soma / qntd

            # Formata o valor médio como moeda
            result = self.formatar_moeda(valor)
            

            return result

        except Exception as e:
            # Imprime a exceção com uma mensagem clara
            print(f"Ocorreu um erro ao calcular o ticket médio: {e}")
            return None

    def passagens(self, mes, ano):
        try:
            # Obtém os dados de faturamento para o mês e ano fornecidos
            dados = self.db.faturamento_mes(mes, ano)

            # Extrai os valores dos dados
            valores = [dado[0] for dado in dados]

            # Calcula a quantidade de valores
            qntd = len(valores)

            # Imprime a quantidade de passagens
        

            return qntd
        except Exception as e:
            # Imprime a exceção com uma mensagem clara
            print(f"Ocorreu um erro ao obter as passagens: {e}")
            return None
