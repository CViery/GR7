import requests
from database import conection
import locale
from services import faturamento

class Utills:
    def __init__(self):
        self.db = conection.Database()
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        self.faturamento_db = faturamento.Faturamento()
    def temperatura(self):
        try:
            API_KEY = "de354584bda26fb5d6ed074b532ccef9"
            cidade = "são paulo"
            link = f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={API_KEY}&lang=pt_br"

            requisicao = requests.get(link)
            requisicao_dic = requisicao.json()
            descricao = requisicao_dic['weather'][0]['description']
            temperatura = requisicao_dic['main']['temp'] - 273.15
            temp = int(temperatura)
            resposta = (descricao, f"{temp} ºC")
            return resposta
            
        except Exception as e:
            print(e)

    def faturamento_pecas(self,mes,ano):
        try:
            
            dados = self.db.faturamento_pecas(mes,ano)
            valores = [valor[0] for valor in dados]
            valor_soma = sum(valores)
            valor_total = locale.currency(valor_soma, grouping=True)
            return valor_total
        except Exception as e:
            print(e)
    
    def faturamento_servicos(self,mes,ano):
        try:
            
            dados = self.db.faturamento_servicos(mes,ano)
            valores = [valor[0] for valor in dados]
            valor_soma = sum(valores)
            valor_total = locale.currency(valor_soma, grouping=True)
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
                valor_total = locale.currency(falta, grouping=True)
            print(valor_total)
            return valor_total
        except Exception as e:
            print(e)
