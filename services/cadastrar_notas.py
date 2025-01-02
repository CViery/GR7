from database import gastos_db


class Notas:
    def __init__(self):
        self.db = gastos_db.GastosDataBase()

    def cadastrar(self, dados, usuario):
        try:
            emissao = dados['emissao']
            dia = emissao[8:]
            mes = emissao[5:7]
            ano = emissao[:4]
            valor_str = dados['valor']
            valor_aut = valor_str.replace(',', '.')
            valor = float(valor_aut)
            nota = {
                'pago_por': dados['empresa'],
                'emitido_para' : dados['emitido_para'],
                'status' : dados['status'],
                'boleto' : dados['boleto'],
                'nota' : dados['nota'],
                'duplicata' : dados['duplicata'],
                'fornecedor' : dados['fornecedor'],
                'data_emissao': dados['emissao'],
                'dia_emissao': dia,
                'mes_emissao': mes,
                'ano_emissao': ano,
                'vencimentos': '',
                'valor' : valor,
                'despesa' : dados['despesa'],
                'obs':dados['obs'],
                'usuario': usuario,
                'sub': dados['sub']
                
            }
            self.db.set_nota(nota)
        except Exception as e:
            print(e)

class Boletos:
    def __init__(self):
        self.db = gastos_db.GastosDataBase()
    
    def cadastrar(self, dados):
        try:
            vencimento = dados['vencimento']
            dia = vencimento[8:]
            mes = vencimento[5:7]
            ano = vencimento[:4]
            valor_str = dados['valor']
            valor_aut = valor_str.replace(',', '.')
            valor = float(valor_aut)
            boleto = {
                'num_nota': dados['num_nota'],
                'notas': dados['notas'],
                'fornecedor': dados['fornecedor'],
                'vencimento':dados['vencimento'],
                'dia_vencimento':dia,
                'mes_vencimento': mes,
                'ano_vencimento':ano,
                'valor': valor
                
            }
            self.db.set_boleto(boleto)
        except Exception as e:
            print(e)

class NotasPortal:
    def __init__(self):
        self.db = gastos_db.GastosDataBasePortal()

    def cadastrar(self, dados, usuario):
        try:
            emissao = dados['emissao']
            dia = emissao[8:]
            mes = emissao[5:7]
            ano = emissao[:4]
            valor_str = dados['valor']
            valor_aut = valor_str.replace(',', '.')
            valor = float(valor_aut)
            nota = {
                'pago_por': dados['empresa'],
                'emitido_para' : dados['emitido_para'],
                'status' : dados['status'],
                'boleto' : dados['boleto'],
                'nota' : dados['nota'],
                'duplicata' : dados['duplicata'],
                'fornecedor' : dados['fornecedor'],
                'data_emissao': dados['emissao'],
                'dia_emissao': dia,
                'mes_emissao': mes,
                'ano_emissao': ano,
                'vencimentos': '',
                'valor' : valor,
                'despesa' : dados['despesa'],
                'obs':dados['obs'],
                'usuario': usuario,
                'sub': dados['sub']
                
            }
            self.db.set_nota(nota)
        except Exception as e:
            print(e)

class BoletosPortal:
    def __init__(self):
        self.db = gastos_db.GastosDataBasePortal()
    
    def cadastrar(self, dados):
        try:
            vencimento = dados['vencimento']
            dia = vencimento[8:]
            mes = vencimento[5:7]
            ano = vencimento[:4]
            valor_str = dados['valor']
            valor_aut = valor_str.replace(',', '.')
            valor = float(valor_aut)
            boleto = {
                'num_nota': dados['num_nota'],
                'notas': dados['notas'],
                'fornecedor': dados['fornecedor'],
                'vencimento':dados['vencimento'],
                'dia_vencimento':dia,
                'mes_vencimento': mes,
                'ano_vencimento':ano,
                'valor': valor
                
            }
            self.db.set_boleto(boleto)
        except Exception as e:
            print(e)

