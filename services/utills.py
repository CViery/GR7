import requests
from database import conection, gastos_db
from services import faturamento, dados_notas

class Utills:
    def __init__(self):
        self.db = conection.Database()
        self.db_gastos = gastos_db.GastosDataBase()
        self.db_dados_notas = dados_notas.DadosGastos()
        self.faturamento_db = faturamento.Faturamento()

    def faturamento_pecas(self,mes,ano):
        try:
            
            dados = self.db.faturamento_pecas(mes,ano)
            valores = [valor[0] for valor in dados]
            valor_soma = sum(valores)
            valor_total = f'R$ {valor_soma:.2f}'
            return valor_total
        except Exception as e:
            print(e)
    
    def faturamento_servicos(self,mes,ano):
        try:
            
            dados = self.db.faturamento_servicos(mes,ano)
            valores = [valor[0] for valor in dados]
            valor_soma = sum(valores)
            valor_total = f'R$ {valor_soma:.2f}'
            return valor_total
        except Exception as e:
            print(e)

    def primeira_meta(self, mes, ano):
        try:
            valor_meta = self.db.faturamento_mes_meta(mes, ano)
            valores = [valor[0] for valor in valor_meta]
            valor_vendido = sum(valores)
            meta = 180000.00
            falta = meta - valor_vendido
            if falta <= 0:
                valor_total = 'Primeira meta Atingida'
            else:
                valor_total = f'R$ {falta:.2f}'
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
                valor_total = f'R$ {falta:.2f}'
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
            print("Faturamento é zero, não é possível calcular a porcentagem.")
            return "Faturamento é zero, não é possível calcular a porcentagem."

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

        calculo = (gasto / faturamento) * 100
        dados = f'{calculo:.2f} %'
        return dados

    def gastos_pecas(self, mes, ano):
        print(f"mes: {mes}")
        print(ano)
        dados_pecas = self.db_gastos.get_gatos_por_tipo('PEÇAS', mes, ano)
        valores_gastos = [dado[0] for dado in dados_pecas]
        gasto = sum(valores_gastos)
        valor_total = f'R$ {gasto:.2f}'
        return valor_total
    
    def valor_dinheiro(self,mes, ano):
        dados_dinheiro = self.db.faturamento_dinheiro( mes, ano)
        valores_dinheiro = [dado[0] for dado in dados_dinheiro]
        gasto = sum(valores_dinheiro)
        valor_total = f'R$ {gasto:.2f}'
        return valor_total