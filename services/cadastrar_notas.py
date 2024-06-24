


class Notas:
    def __init__(self):
        pass

    def cadastrar(self, dados):
        try:
            emitido_para = dados['emitido_para']
            status = dados['status']
            boleto = dados['boleto']
            nota = dados['nota']
            duplicata = dados['duplicata']
            fornecedor = dados['fornecedor']
            emissao = dados['emissao']
            valor_str = dados['valor']
            despesa = dados['despesa']
            valor_aut = valor_str.replace(',', '.')
            valor = float(valor_aut)
        except Exception as e:
            print(e)