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
            # fazer updatde usando o numero da nota para ads o num da duplicata, e os vencimentos para aql nota
        vencimentos = duplicata['parcelas']
        
        for vencimento in vencimentos:
            data = str(vencimento['vencimento'])
            dia = data[8:10]
            mes = data[5:7]
            ano = data[:4]
            valor_str = vencimento['valor']
            valor_aut = valor_str.replace(',', '.')
            valor = float(valor_aut)
            boleto = {
                'num_nota': numero_duplicata,
                'notas': numeros_notas,
                'fornecedor': fornecedor,
                'vencimento':data,
                'dia_vencimento':dia,
                'mes_vencimento': mes,
                'ano_vencimento':ano,
                'valor': valor
            }
            #enviar o boleto para o cadastro no banco 

        

    def cadastrar_boletos(self,boleto):
        print(boleto)
        num_nota = boleto['num_nota']
        fornecedor = boleto['fornecedor']
        vencimento = boleto['vencimento']
        dia = vencimento[8:]
        mes = vencimento[5:7]
        ano = vencimento[:4]
        valor = boleto['valor']

    def atualizar_nota():
        pass