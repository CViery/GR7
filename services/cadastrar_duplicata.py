from database import gastos_db
from datetime import datetime
import json

class Boletos:
    def __init__(self):
        self.db = gastos_db.GastosDataBase()
        pass

    def cadastrar_duplicatas(self, duplicata):
        fornecedores = []
        numeros_notas = []
        numero_duplicata = duplicata['numero_duplicata']
        notas = duplicata['notas']
        for nota in notas:
            num_nota = nota['numero']
            fornecedor = nota['fornecedor']
            fornecedores.append(fornecedor)
            numeros_notas.append(num_nota)
            vencimentos = duplicata['parcelas']
            datas = []
            for data in vencimentos:
                parcela = data['vencimento']
                data_objeto = datetime.strptime(parcela, "%Y-%m-%d")
                data_formatada = data_objeto.strftime("%d/%m/%Y")
                datas.append(data_formatada)
            parcelas = json.dumps(datas)
            self.db.atualizar_notas(num_nota,numero_duplicata,parcelas)
        vencimentos = duplicata['parcelas']
        
        for vencimento in vencimentos:
            data = str(vencimento['vencimento'])
            dia = data[8:10]
            mes = data[5:7]
            ano = data[:4]
            valor_str = vencimento['valor']
            valor_aut = valor_str.replace(',', '.')
            valor = float(valor_aut)
            nfe = json.dumps(numeros_notas)
            boleto = {
                'num_nota': numero_duplicata,
                'notas': nfe,
                'fornecedor': fornecedor,
                'vencimento':data,
                'dia_vencimento':dia,
                'mes_vencimento': mes,
                'ano_vencimento':ano,
                'valor': valor
            }
           
            self.db.set_boleto(boleto)


class BoletosPortal:
    def __init__(self):
        self.db = gastos_db.GastosDataBasePortal()
        pass

    def cadastrar_duplicatas(self, duplicata):
        fornecedores = []
        numeros_notas = []
        numero_duplicata = duplicata['numero_duplicata']
        notas = duplicata['notas']
        for nota in notas:
            num_nota = nota['numero']
            fornecedor = nota['fornecedor']
            fornecedores.append(fornecedor)
            numeros_notas.append(num_nota)
            vencimentos = duplicata['parcelas']
            datas = []
            for data in vencimentos:
                parcela = data['vencimento']
                data_objeto = datetime.strptime(parcela, "%Y-%m-%d")
                data_formatada = data_objeto.strftime("%d/%m/%Y")
                datas.append(data_formatada)
            parcelas = json.dumps(datas)
            self.db.atualizar_notas(num_nota,numero_duplicata,parcelas)
        vencimentos = duplicata['parcelas']
        
        for vencimento in vencimentos:
            data = str(vencimento['vencimento'])
            dia = data[8:10]
            mes = data[5:7]
            ano = data[:4]
            valor_str = vencimento['valor']
            valor_aut = valor_str.replace(',', '.')
            valor = float(valor_aut)
            nfe = json.dumps(numeros_notas)
            boleto = {
                'num_nota': numero_duplicata,
                'notas': nfe,
                'fornecedor': fornecedor,
                'vencimento':data,
                'dia_vencimento':dia,
                'mes_vencimento': mes,
                'ano_vencimento':ano,
                'valor': valor
            }
            
            self.db.set_boleto(boleto)

class Boletos_morumbi:
    def __init__(self):
        self.db = gastos_db.GastosDataBaseMorumbi()
        pass

    def cadastrar_duplicatas(self, duplicata):
        fornecedores = []
        numeros_notas = []
        numero_duplicata = duplicata['numero_duplicata']
        notas = duplicata['notas']
        for nota in notas:
            num_nota = nota['numero']
            fornecedor = nota['fornecedor']
            fornecedores.append(fornecedor)
            numeros_notas.append(num_nota)
            vencimentos = duplicata['parcelas']
            datas = []
            for data in vencimentos:
                parcela = data['vencimento']
                data_objeto = datetime.strptime(parcela, "%Y-%m-%d")
                data_formatada = data_objeto.strftime("%d/%m/%Y")
                datas.append(data_formatada)
            parcelas = json.dumps(datas)
            self.db.atualizar_notas(num_nota,numero_duplicata,parcelas)
        vencimentos = duplicata['parcelas']
        
        for vencimento in vencimentos:
            data = str(vencimento['vencimento'])
            dia = data[8:10]
            mes = data[5:7]
            ano = data[:4]
            valor_str = vencimento['valor']
            valor_aut = valor_str.replace(',', '.')
            valor = float(valor_aut)
            nfe = json.dumps(numeros_notas)
            boleto = {
                'num_nota': numero_duplicata,
                'notas': nfe,
                'fornecedor': fornecedor,
                'vencimento':data,
                'dia_vencimento':dia,
                'mes_vencimento': mes,
                'ano_vencimento':ano,
                'valor': valor
            }
           
            self.db.set_boleto(boleto)