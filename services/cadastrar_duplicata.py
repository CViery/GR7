

class Boletos:
    def __init__(self):
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
            # fazer updatde usando o numero da nota para ads o num da duplicata, e os vencimentos para aql nota
        vencimentos = duplicata['parcelas']
        for vencimento in vencimentos:
            boleto = {
                'numero_duplicata': numero_duplicata,
                'fornecedor' : fornecedores[0],
                'notas': numeros_notas,
                'vencimento': vencimento
            }
            #enviar o boleto para o cadastro no banco 
            print(boleto)
        

    def cadastrar_boletos(self,boleto):
        num_nota = boleto['num_nota']
        fornecedor = boleto['fornecedor']
        vencimento = boleto['vencimento']
        dia = vencimento[8:]
        mes = vencimento[5:7]
        ano = vencimento[:4]
        valor = boleto['valor']

    def atualizar_nota():
        pass