from database import gastos_db
from datetime import datetime
import random


class DadosGastos:

    def __init__(self):
        self.db = gastos_db.GastosDataBase()

    def boletos_do_dia(self, dia, mes, ano):
        dados = self.db.get_boleto_by_day(dia, mes, ano)
        valores = []
        boletos = []
        for dado in dados:
            valor = f'R$ {dado[7]:.2f}'
            data_objeto = datetime.strptime(dado[3], "%Y-%m-%d")
            data = data_objeto.strftime("%d/%m/%Y")
            boleto = {
                'numero_nota': dado[0],
                'notas': dado[1],
                'fornecedor': dado[2],
                'vencimento': data,
                'valor': valor
            }

            valores.append(dado[7])
            boletos.append(boleto)
        return boletos

    def valor_a_pagar(self, dia, mes, ano):
        dados = self.db.get_boleto_by_day(dia, mes, ano)
        valores = []
        for dado in dados:
            valores.append(dado[7])
        a_pagar = sum(valores)
        valor_a_pagar = f'R$ {a_pagar:.2f}'
        return valor_a_pagar

    def cadastrar_despesa(self, despesa):
        cadastrar = self.db.set_despesas(despesa)
        print('cadastrado')

    def despesas(self, mes, ano):
        despesas = self.db.get_despesas()
        dados_despesas = []
        for despesa in despesas:
            item = despesa[0]
            valor_despesa = self.db.get_valor_despesa(item, mes, ano)
            valores = []
            for valor in valor_despesa:
                valores.append(valor[0])
            valor_soma = sum(valores)
            valor_total = f'R$ {valor_soma:.2f}'
            dados_despesas.append((despesa[0], valor_total))
        return dados_despesas

    def todas_as_notas(self):
        notas = self.db.get_all_notas()
        output = []
        for nota in notas:
            print(nota)
            data_objeto = datetime.strptime(nota[7], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_nota = nota[12]
            valor = f'R$ {valor_nota:.2f}'
            nfe = {
                'pago_por': nota[0],
                'emitido_para': nota[1],
                'status': nota[2],
                'boleto': nota[3],
                'numero_nota': nota[4],
                'fornecedor': nota[6],
                'data_emissao': data_formatada,
                'valor': valor,
                'duplicata': nota[5],
                'tipo_despesa': nota[13]
            }
            output.append(nfe)
        return output

    def valor_nota(self):
        notas = self.db.get_all_notas()
        output = [nota[12] for nota in notas]
        soma = sum(output)
        result = f'R$ {soma:.2f}'
        return result

    def filtrar_notas(self, data_inicio=None, data_fim=None, fornecedor=None, despesa=None):
        resultado = self.db.obter_notas_filtradas(
            data_inicio, data_fim, fornecedor, despesa)
        notas = []
        for dados in resultado:
            data_objeto = datetime.strptime(dados[7], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_nota = dados[12]
            valor = f'R$ {valor_nota:.2f}'
            nfe = {
                'pago_por': dados[0],
                'emitido_para': dados[1],
                'status': dados[2],
                'boleto': dados[3],
                'numero_nota': dados[4],
                'fornecedor': dados[6],
                'data_emissao': data_formatada,
                'valor': valor,
                'duplicata': dados[5],
                'tipo_despesa': dados[13]
            }
            notas.append(nfe)
        return notas

    def filtrar_notas_valor(self, data_inicio=None, data_fim=None, fornecedor=None, despesa=None):
        resultado = self.db.obter_notas_filtradas(
            data_inicio, data_fim, fornecedor, despesa)
        valores = [dados[12] for dados in resultado]
        soma = sum(valores)
        result = f'R$ {soma:.2f}'
        return result

    def nota_por_numero(self, num_nota):
        dados = self.db.get_nota_por_numero(num_nota)
        print(dados)
        if dados:
            data_objeto = datetime.strptime(dados[7], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_nota = dados[12]
            valor = f'R$ {valor_nota:.2f}'
            nfe = {
                'fornecedor': dados[6],
                'data_emissao': data_formatada,
                'valor': valor
            }
            return nfe

    def todos_os_boletos(self):
        dados = self.db.get_boletos()
        boletos = []
        for dado in dados:
            print(dado)
            data_objeto = datetime.strptime(dado[3], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_boleto = dado[7]
            valor = f'R$ {valor_boleto:.2f}'
            boleto = {
                'num_nota': dado[0],
                'notas': dado[1],
                'fornecedor': dado[2],
                'data_vencimento': data_formatada,
                'valor': valor
            }
            boletos.append(boleto)
            print(boleto)
        return boletos

    def filtrar_boletos(self, data_inicio=None, data_fim=None, fornecedor=None):
        dados = self.db.obter_boletos_filtrados(
            data_inicio, data_fim, fornecedor)
        boletos = []
        for dado in dados:
            print(dado)
            data_objeto = datetime.strptime(dado[3], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_boleto = dado[7]
            valor = f'R$ {valor_boleto:.2f}'
            boleto = {
                'num_nota': dado[0],
                'notas': dado[1],
                'fornecedor': dado[2],
                'data_vencimento': data_formatada,
                'valor': valor
            }
            boletos.append(boleto)
            print(boleto)
        return boletos

    def valor_gastos(self, mes, ano):
        notas = self.db.get_valor_notas(mes, ano)
        valores = []
        for nota in notas:
            valores.append(nota[0])
        valor_soma = sum(valores)
        valor_total = f'R$ {valor_soma:.2f}'
        print(valor_total)
        return valor_total

    def cadastrar_oleo(self, dados):
        tipo = dados['oleo']
        self.db.set_oleo(tipo)

    def cadastrar_companhia(self, dados):
        despesa = dados['depesa']
        self.db.cadastrar_companhia(despesa)

    def cadastrar_funcionario(self, dados):
        id = random.randint(1, 100)
        nome = dados['funcionario']
        self.db.cadastrar_funcionario(id, nome)

    def cadastrar_baterias(self, dados):
        modelo = dados['bateria']
        self.db.cadastrar_baterias(modelo)

    def filtrar_boletos_valor(self, data_inicio=None, data_fim=None, fornecedor=None):
        dados = self.db.obter_boletos_filtrados(
            data_inicio, data_fim, fornecedor)
        boletos = [dado[7] for dado in dados]
        soma = sum(boletos)
        result = f'R$ {soma:.2f}'
        return result

    def valor_boleto(self):
        dados = self.db.get_boletos()
        boletos = [dado[7] for dado in dados]
        soma = sum(boletos)
        result = f'R$ {soma:.2f}'
        return result


class DadosGastosPortal():
    def __init__(self):
        self.db = gastos_db.GastosDataBasePortal()

    def boletos_do_dia(self, dia, mes, ano):
        dados = self.db.get_boleto_by_day(dia, mes, ano)
        valores = []
        boletos = []
        for dado in dados:
            valor = f'R$ {dado[7]:.2f}'
            data_objeto = datetime.strptime(dado[3], "%Y-%m-%d")
            data = data_objeto.strftime("%d/%m/%Y")
            boleto = {
                'numero_nota': dado[0],
                'notas': dado[1],
                'fornecedor': dado[2],
                'vencimento': data,
                'valor': valor
            }

            valores.append(dado[7])
            boletos.append(boleto)
        return boletos

    def valor_a_pagar(self, dia, mes, ano):
        dados = self.db.get_boleto_by_day(dia, mes, ano)
        valores = []
        for dado in dados:
            valores.append(dado[7])
        a_pagar = sum(valores)
        valor_a_pagar = f'R$ {a_pagar:.2f}'
        return valor_a_pagar

    def cadastrar_despesa(self, despesa):
        cadastrar = self.db.set_despesas(despesa)
        print('cadastrado')

    def despesas(self, mes, ano):
        despesas = self.db.get_despesas()
        dados_despesas = []
        for despesa in despesas:
            item = despesa[0]
            valor_despesa = self.db.get_valor_despesa(item, mes, ano)
            valores = []
            for valor in valor_despesa:
                valores.append(valor[0])
            valor_soma = sum(valores)
            valor_total = f'R$ {valor_soma:.2f}'
            dados_despesas.append((despesa[0], valor_total))
        return dados_despesas

    def todas_as_notas(self):
        notas = self.db.get_all_notas()
        output = []
        for nota in notas:
            print(nota)
            data_objeto = datetime.strptime(nota[7], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_nota = nota[12]
            valor = f'R$ {valor_nota:.2f}'
            nfe = {
                'pago_por': nota[0],
                'emitido_para': nota[1],
                'status': nota[2],
                'boleto': nota[3],
                'numero_nota': nota[4],
                'fornecedor': nota[6],
                'data_emissao': data_formatada,
                'valor': valor,
                'duplicata': nota[5],
                'tipo_despesa': nota[13]
            }
            output.append(nfe)
        return output

    def filtrar_notas_valor(self, data_inicio=None, data_fim=None, fornecedor=None, despesa=None):
        resultado = self.db.obter_notas_filtradas(
            data_inicio, data_fim, fornecedor, despesa)
        valores = [dados[12] for dados in resultado]
        soma = sum(valores)
        result = f'R$ {soma:.2f}'
        return result

    def valor_nota(self):
        notas = self.db.get_all_notas()
        output = [nota[12] for nota in notas]
        soma = sum(output)
        result = f'R$ {soma:.2f}'
        return result

    def valor_nota(self):
        notas = self.db.get_all_notas()
        output = [nota[12] for nota in notas]
        soma = sum(output)
        result = f'R$ {soma:.2f}'
        return result

    def filtrar_notas(self, data_inicio=None, data_fim=None, fornecedor=None, despesa=None):
        resultado = self.db.obter_notas_filtradas(
            data_inicio, data_fim, fornecedor, despesa)
        notas = []
        for dados in resultado:
            data_objeto = datetime.strptime(dados[7], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_nota = dados[12]
            valor = f'R$ {valor_nota:.2f}'
            nfe = {
                'pago_por': dados[0],
                'emitido_para': dados[1],
                'status': dados[2],
                'boleto': dados[3],
                'numero_nota': dados[4],
                'fornecedor': dados[6],
                'data_emissao': data_formatada,
                'valor': valor,
                'duplicata': dados[5],
                'tipo_despesa': dados[13]
            }
            notas.append(nfe)
        return notas

    def filtrar_notas(self, data_inicio=None, data_fim=None, fornecedor=None, despesa=None):
        resultado = self.db.obter_notas_filtradas(
            data_inicio, data_fim, fornecedor, despesa)
        valores = [dados[12] for dados in resultado]
        soma = sum(valores)
        result = f'R$ {soma:.2f}'
        return result

    def nota_por_numero(self, num_nota):
        dados = self.db.get_nota_por_numero(num_nota)
        print(dados)
        if dados:
            data_objeto = datetime.strptime(dados[7], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_nota = dados[12]
            valor = f'R$ {valor_nota:.2f}'
            nfe = {
                'fornecedor': dados[6],
                'data_emissao': data_formatada,
                'valor': valor
            }
            return nfe

    def todos_os_boletos(self):
        dados = self.db.get_boletos()
        boletos = []
        for dado in dados:
            print(dado)
            data_objeto = datetime.strptime(dado[3], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_boleto = dado[7]
            valor = f'R$ {valor_boleto:.2f}'
            boleto = {
                'num_nota': dado[0],
                'notas': dado[1],
                'fornecedor': dado[2],
                'data_vencimento': data_formatada,
                'valor': valor
            }
            boletos.append(boleto)
            print(boleto)
        return boletos

    def valor_boleto(self):
        dados = self.db.get_boletos()
        boletos = [dado[7] for dado in dados]
        soma = sum(boletos)
        result = f'R$ {soma:.2f}'
        return result

    def filtrar_boletos(self, data_inicio=None, data_fim=None, fornecedor=None):
        dados = self.db.obter_boletos_filtrados(
            data_inicio, data_fim, fornecedor)
        boletos = []
        for dado in dados:
            print(dado)
            data_objeto = datetime.strptime(dado[3], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_boleto = dado[7]
            valor = f'R$ {valor_boleto:.2f}'
            boleto = {
                'num_nota': dado[0],
                'notas': dado[1],
                'fornecedor': dado[2],
                'data_vencimento': data_formatada,
                'valor': valor
            }
            boletos.append(boleto)
            print(boleto)
        return boletos

    def filtrar_boletos_valor(self, data_inicio=None, data_fim=None, fornecedor=None):
        dados = self.db.obter_boletos_filtrados(
            data_inicio, data_fim, fornecedor)
        boletos = [dado[7] for dado in dados]
        soma = sum(boletos)
        result = f'R$ {soma:.2f}'
        return result

    def valor_gastos(self, mes, ano):
        notas = self.db.get_valor_notas(mes, ano)
        valores = []
        for nota in notas:
            valores.append(nota[0])
        valor_soma = sum(valores)
        valor_total = f'R$ {valor_soma:.2f}'
        print(valor_total)
        return valor_total

    def cadastrar_oleo(self, dados):
        tipo = dados['oleo']
        self.db.set_oleo(tipo)

    def cadastrar_companhia(self, dados):
        despesa = dados['despesa']
        self.db.cadastrar_companhia(despesa)

    def cadastrar_funcionario(self, dados):
        id = random.randint(1, 100)
        nome = dados['funcionario']
        self.db.cadastrar_funcionario(id, nome)

    def cadastrar_baterias(self, dados):
        modelo = dados['bateria']
        self.db.cadastrar_baterias(modelo)
