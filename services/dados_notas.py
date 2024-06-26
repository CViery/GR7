from database import gastos_db
import locale
from datetime import datetime

class DadosGastos:

    def __init__(self):
        self.db = gastos_db.GastosDataBase()
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    
    def boletos_do_dia(self, dia, mes, ano):
        dados = self.db.get_boleto_by_day(dia, mes, ano)
        valores = []
        boletos = []
        for dado in dados:
            valor = locale.currency(dado[7], grouping=True)
            data_objeto = datetime.strptime(dado[3], "%Y-%m-%d")
            data = data_formatada = data_objeto.strftime("%d/%m/%Y")
            boleto ={
                'numero_nota' : dado[0],
                'notas' : dado[1],
                'fornecedor' : dado[2],
                'vencimento' : data,
                'valor' : valor
            }
            valores.append(boleto['valor'])
            boletos.append(boleto)
        return boletos
    def cadastrar_despesa(self,despesa):
        cadastrar = self.db.set_despesas(despesa)
        print('cadastrado')

    def despesas(self, mes, ano):
        despesas = self.db.get_despesas()
        dados_despesas = []
        for despesa in despesas:
            item  = despesa[0]
            print(item)
            valor_despesa = self.db.get_valor_despesa(item, mes, ano)
            print(valor_despesa)
            valores = []
            for valor in valor_despesa:
                valores.append(valor[0])
            valor_soma = sum(valores)
            valor_total = locale.currency(valor_soma, grouping=True)
            dados_despesas.append((despesa[0], valor_total))
        return dados_despesas
        


