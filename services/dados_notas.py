from database import gastos_db
from datetime import datetime
import random


class DadosGastos:

    def __init__(self):
        self.db = gastos_db.GastosDataBase()
    
    def formatar_moeda(self, valor):
        if valor is None:
            return "R$ 0"
        if not isinstance(valor, (int, float)):
            raise ValueError("O valor deve ser um número ou None.")
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def boletos_do_dia(self, dia, mes, ano):
        dados = self.db.get_boleto_by_day(dia, mes, ano)
        
        valores = []
        boletos = []
        for dado in dados:
            valor = f'R$ {dado[8]:.2f}'
            data_objeto = datetime.strptime(dado[4], "%Y-%m-%d")
            data = data_objeto.strftime("%d/%m/%Y")
            boleto = {
                'numero_nota': dado[1],
                'notas': dado[2],
                'fornecedor': dado[3],
                'vencimento': data,
                'valor': valor
            }

            valores.append(dado[8])
            boletos.append(boleto)
        return boletos

    def valor_a_pagar(self, dia, mes, ano):
        dados = self.db.get_boleto_by_day(dia, mes, ano)
        valores = []
        for dado in dados:
            valores.append(dado[8])
        a_pagar = sum(valores)
        valor_a_pagar = self.formatar_moeda(a_pagar)
        return valor_a_pagar

    def cadastrar_despesa(self, despesa):
        cadastrar = self.db.set_despesas(despesa)
        

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
            valor_total = self.formatar_moeda(valor_soma)
            dados_despesas.append((despesa[0], valor_total))
        return dados_despesas

    def todas_as_notas(self):
        notas = self.db.get_all_notas()
        output = []
        for nota in notas:
           
            data_objeto = datetime.strptime(nota[8], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_nota = nota[13]
            valor = self.formatar_moeda(valor_nota)
            nfe = {
                'pago_por': nota[1],
                'emitido_para': nota[2],
                'status': nota[3],
                'boleto': nota[4],
                'numero_nota': nota[5],
                'fornecedor': nota[7],
                'data_emissao': data_formatada,
                'valor': valor,
                'duplicata': nota[6],
                'tipo_despesa': nota[14],
                'obs': nota[15]
            }
            output.append(nfe)
        return output
    
    def todas_as_notas_mes(self, mes, ano):
       
        notas = self.db.get_all_notas_mes(mes, ano)
        
        output = []
        if notas:
            for nota in notas:
                data_objeto = datetime.strptime(nota[8], "%Y-%m-%d")
                data_formatada = data_objeto.strftime("%d/%m/%Y")
                valor_nota = nota[13]
                valor = self.formatar_moeda(valor_nota)
                nfe = {
                    'pago_por': nota[1],
                    'emitido_para': nota[2],
                    'status': nota[3],
                    'boleto': nota[4],
                    'numero_nota': nota[5],
                    'fornecedor': nota[7],
                    'data_emissao': data_formatada,
                    'valor': valor,
                    'duplicata': nota[6],
                    'tipo_despesa': nota[14],
                    'obs': nota[15]
                }
                output.append(nfe)
            return output
        else:
            notas = []
            return notas

    def valor_nota(self):
        notas = self.db.get_all_notas()
        output = [nota[13] for nota in notas]
        soma = sum(output)
        result = self.formatar_moeda(soma)
        return result

    def filtrar_notas(self, data_inicio=None, data_fim=None, fornecedor=None, despesa=None, obs=None):
        resultado = self.db.obter_notas_filtradas(
            data_inicio, data_fim, fornecedor, despesa, obs)
        
        notas = []
        for dados in resultado:
            data_objeto = datetime.strptime(dados[8], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_nota = dados[13]
            valor = self.formatar_moeda(valor_nota)
            nfe = {
                'pago_por': dados[1],
                'emitido_para': dados[2],
                'status': dados[3],
                'boleto': dados[4],
                'numero_nota': dados[5],
                'fornecedor': dados[7],
                'data_emissao': data_formatada,
                'valor': valor,
                'duplicata': dados[6],
                'tipo_despesa': dados[14],
                'obs': dados[15]
            }
            notas.append(nfe)
        return notas

    def filtrar_notas_valor(self, data_inicio=None, data_fim=None, fornecedor=None, despesa=None, obs=None):
        resultado = self.db.obter_notas_filtradas(
            data_inicio, data_fim, fornecedor, despesa,obs)
        valores = [dados[13] for dados in resultado]
        soma = sum(valores)
        result = self.formatar_moeda(soma)
        return result

    def nota_por_numero(self, num_nota):
        dados = self.db.get_nota_por_numero(num_nota)
       
        if dados:
            data_objeto = datetime.strptime(dados[8], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_nota = dados[13]
            valor = self.formatar_moeda(valor_nota)
            nfe = {
                'fornecedor': dados[7],
                'data_emissao': data_formatada,
                'valor': valor,
                'obs': dados[15]
            }
            return nfe

    def todos_os_boletos(self):
        dados = self.db.get_boletos()
        boletos = []
        for dado in dados:
            
            data_objeto = datetime.strptime(dado[4], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_boleto = dado[8]
            valor = self.formatar_moeda(valor_boleto)
            boleto = {
                'num_nota': dado[1],
                'notas': dado[2],
                'fornecedor': dado[3],
                'data_vencimento': data_formatada,
                'valor': valor
            }
            boletos.append(boleto)
            
        return boletos
    
    def todos_os_boletos_por_nota(self, num_nota):
        dados = self.db.get_boletos_por_nota(num_nota)
        boletos = []
        for dado in dados:
            data_objeto = datetime.strptime(dado[4], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_boleto = dado[8]
            valor = self.formatar_moeda(valor_boleto)
            boleto = {
                'num_nota': dado[1],
                'notas': dado[2],
                'fornecedor': dado[3],
                'data_vencimento': data_formatada,
                'valor': valor
            }
            boletos.append(boleto)
            
        return boletos


    def valor_gastos_boletos_valor(self, num_nota):
        notas = self.db.get_boletos_por_nota_valor(num_nota)
        valores = [nota[0] for nota in notas]
        valor_soma = sum(valores)
        valor_total = self.formatar_moeda(valor_soma)
        return valor_total

    def filtrar_boletos(self, data_inicio=None, data_fim=None, fornecedor=None):
        dados = self.db.obter_boletos_filtrados(
            data_inicio, data_fim, fornecedor)
        boletos = []
        for dado in dados:
            
            data_objeto = datetime.strptime(dado[4], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_boleto = dado[8]
            valor = self.formatar_moeda(valor_boleto)
            boleto = {
                'num_nota': dado[1],
                'notas': dado[2],
                'fornecedor': dado[3],
                'data_vencimento': data_formatada,
                'valor': valor
            }
            boletos.append(boleto)
           
        return boletos

    def valor_gastos(self, mes, ano):
        notas = self.db.get_valor_notas(mes, ano)
        valores = []
        for nota in notas:
            valores.append(nota[0])
        valor_soma = sum(valores)
        valor_total = self.formatar_moeda(valor_soma)
        
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
        boletos = [dado[8] for dado in dados]
        soma = sum(boletos)
        result = self.formatar_moeda(soma)
        return result

    def valor_boleto(self):
        dados = self.db.get_boletos()
        boletos = [dado[8] for dado in dados]
        soma = sum(boletos)
        result = f'R$ {soma:.2f}'
        return result
    
    def dados_gastos(self, mes, ano):
        #Dados das despesas e subcategorias
        #print("Obtendo despesas...")
        despesas = self.db.get_despesas()
        #print(f"Despesas obtidas: {despesas}")

        #print("Obtendo subcategorias...")
        sub_categorias = self.db.get_all_subcategorias()
        #print(f"Subcategorias obtidas: {sub_categorias}")

        # Função para somar valores de um período específico
        def somar_valores_por_subcategoria(subcategoria, mes=None, ano=None):
            #print(f"Calculando valores para subcategoria: {subcategoria}, mês: {mes}, ano: {ano}")
            notas = self.db.notas_por_subcategoria(subcategoria, mes, ano)
            #print(f"Notas obtidas para subcategoria {subcategoria}: {notas}")
            if notas is None:
                print(f"Nenhuma nota encontrada para subcategoria {subcategoria}")
                return
            valores = [dado[13] for dado in notas]
            soma = sum(valores)
            #print(f"Soma dos valores para subcategoria {subcategoria}: {soma}")
            return soma

        def somar_valores_por_categoria(categoria, mes=None, ano=None):
            print(f"Calculando valores para categoria: {categoria[1]}, mês: {mes}, ano: {ano}")
            notas = self.db.notas_por_categoria(categoria[1], mes, ano)
            print(f"Notas obtidas para categoria {categoria[1]}: {notas}")
            if notas is None:
                print(f"Nenhuma nota encontrada para categoria {categoria[1]}")
                return 0
            valores = [dado[13] for dado in notas]
            soma = sum(valores)
            print(f"Soma dos valores para categoria {categoria[1]}: {soma}")
            return soma

        # Construir os dados finais com soma dos valores
        dados = []
        for despesa in despesas:
            print(f"Processando despesa: {despesa}")
            subs = []
            valor = somar_valores_por_categoria(despesa, mes, ano)
            for sub in sub_categorias:
                print(f'Sub: {sub}')
                if sub[2] == despesa[1]:  # Ajuste para verificar o nome da despesa
                    # Calcular valores da subcategoria
                    valor_mes = somar_valores_por_subcategoria(sub[3], mes=mes, ano=ano)
                    subs.append({
                        "codigo": sub[1],  # Ajuste para corresponder ao índice correto
                        "descricao": sub[3],
                        "valor_mes": self.formatar_moeda(valor_mes),
                    })
            dados.append({
                "despesa": despesa[1],
                "subs": subs,
                "valor": self.formatar_moeda(valor)
            })
        
        import pprint
        pprint.pprint(dados)
        
            
        return dados
        # Exibir os dados
        
    def buscar_notas(self, mes, ano):
        print(mes)
        print(ano)
        notas = self.db.get_all_notas_mes(mes, ano)
        
        output = []
        if notas:
            for nota in notas:
                data_objeto = datetime.strptime(nota[8], "%Y-%m-%d")
                data_formatada = data_objeto.strftime("%d/%m/%Y")
                valor_nota = nota[13]
                valor = self.formatar_moeda(valor_nota)
                nfe = {
                    'pago_por': nota[1],
                    'emitido_para': nota[2],
                    'status': nota[3],
                    'boleto': nota[4],
                    'numero_nota': nota[5],
                    'fornecedor': nota[7],
                    'data_emissao': data_formatada,
                    'valor': valor,
                    'duplicata': nota[8],
                    'tipo_despesa': nota[14],
                    'obs': nota[15],
                    'sub': nota[16]
                }
                output.append(nfe)
            return output
        else:
            notas = []
            return notas
        
    def buscar_boletos(self, mes, ano):
        dados = self.db.get_boletos_mes(mes, ano)
        boletos = []
        for dado in dados:
            
            data_objeto = datetime.strptime(dado[4], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_boleto = dado[8]
            valor = self.formatar_moeda(valor_boleto)
            boleto = {
                'num_nota': dado[1],
                'notas': dado[2],
                'fornecedor': dado[3],
                'data_vencimento': data_formatada,
                'valor': valor
            }
            boletos.append(boleto)
            
        return boletos


class DadosGastosPortal():
    def __init__(self):
        self.db = gastos_db.GastosDataBasePortal()
    
    def formatar_moeda(self, valor):
        if valor is None:
            return "R$ 0"
        if not isinstance(valor, (int, float)):
            raise ValueError("O valor deve ser um número ou None.")
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def boletos_do_dia(self, dia, mes, ano):
        dados = self.db.get_boleto_by_day(dia, mes, ano)
        valores = []
        boletos = []
        for dado in dados:
            valor = self.formatar_moeda(dado[8])
            data_objeto = datetime.strptime(dado[4], "%Y-%m-%d")
            data = data_objeto.strftime("%d/%m/%Y")
            boleto = {
                'numero_nota': dado[1],
                'notas': dado[2],
                'fornecedor': dado[3],
                'vencimento': data,
                'valor': valor
            }

            valores.append(dado[8])
            boletos.append(boleto)
        return boletos

    def valor_a_pagar(self, dia, mes, ano):
        dados = self.db.get_boleto_by_day(dia, mes, ano)
        valores = []
        for dado in dados:
            valores.append(dado[8])
        a_pagar = sum(valores)
        valor_a_pagar = self.formatar_moeda(a_pagar)
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
            valor_total = self.formatar_moeda(valor_soma)
            dados_despesas.append((despesa[0], valor_total))
        return dados_despesas

    def todas_as_notas(self):
        notas = self.db.get_all_notas()
        output = []
        for nota in notas:
            data_objeto = datetime.strptime(nota[8], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_nota = nota[13]
            valor = self.formatar_moeda(valor_nota)
            nfe = {
                'pago_por': nota[1],
                'emitido_para': nota[2],
                'status': nota[3],
                'boleto': nota[4],
                'numero_nota': nota[5],
                'fornecedor': nota[7],
                'data_emissao': data_formatada,
                'valor': valor,
                'duplicata': nota[9],
                'tipo_despesa': nota[14],
                'obs': nota[14]
            }
            output.append(nfe)
        return output

    def todas_as_notas_mes(self, mes, ano):
        print(mes)
        print(ano)
        notas = self.db.get_all_notas_mes(mes, ano)
        
        output = []
        if notas:
            for nota in notas:
                data_objeto = datetime.strptime(nota[8], "%Y-%m-%d")
                data_formatada = data_objeto.strftime("%d/%m/%Y")
                valor_nota = nota[13]
                valor = self.formatar_moeda(valor_nota)
                nfe = {
                    'pago_por': nota[1],
                    'emitido_para': nota[2],
                    'status': nota[3],
                    'boleto': nota[4],
                    'numero_nota': nota[5],
                    'fornecedor': nota[7],
                    'data_emissao': data_formatada,
                    'valor': valor,
                    'duplicata': nota[6],
                    'tipo_despesa': nota[14],
                    'obs': nota[15]
                }
                output.append(nfe)
            return output
        else:
            notas = []
            return notas

    def filtrar_notas_valor(self, data_inicio=None, data_fim=None, fornecedor=None, despesa=None):
        resultado = self.db.obter_notas_filtradas(
            data_inicio, data_fim, fornecedor, despesa)
        valores = [dados[12] for dados in resultado]
        soma = sum(valores)
        result = self.formatar_moeda(soma)
        return result

    def valor_nota(self):
        notas = self.db.get_all_notas()
        output = [nota[12] for nota in notas]
        soma = sum(output)
        result = self.formatar_moeda(soma)
        return result

    def valor_nota(self):
        notas = self.db.get_all_notas()
        output = [nota[13] for nota in notas]
        soma = sum(output)
        result = self.formatar_moeda(soma)
        return result

    def filtrar_notas(self, data_inicio=None, data_fim=None, fornecedor=None, despesa=None, obs=None):
        resultado = self.db.obter_notas_filtradas(
            data_inicio, data_fim, fornecedor, despesa)
        notas = []
        for dados in resultado:
            data_objeto = datetime.strptime(dados[8], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_nota = dados[13]
            valor = self.formatar_moeda(valor_nota)
            nfe = {
                'pago_por': dados[1],
                'emitido_para': dados[2],
                'status': dados[3],
                'boleto': dados[4],
                'numero_nota': dados[5],
                'fornecedor': dados[7],
                'data_emissao': data_formatada,
                'valor': valor,
                'duplicata': dados[6],
                'tipo_despesa': dados[14]
            }
            notas.append(nfe)
        return notas

    def filtrar_notas_valor(self, data_inicio=None, data_fim=None, fornecedor=None, despesa=None, obs=None):
        resultado = self.db.obter_notas_filtradas(
            data_inicio, data_fim, fornecedor, despesa)
        valores = [dados[13] for dados in resultado]
        soma = sum(valores)
        result = self.formatar_moeda(soma)
        return result

    def nota_por_numero(self, num_nota):
        dados = self.db.get_nota_por_numero(num_nota)
        if dados:
            data_objeto = datetime.strptime(dados[8], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_nota = dados[13]
            valor = self.formatar_moeda(valor_nota)
            nfe = {
                'fornecedor': dados[7],
                'data_emissao': data_formatada,
                'valor': valor
            }
            return nfe

    def todos_os_boletos(self):
        dados = self.db.get_boletos()
        boletos = []
        for dado in dados:
            data_objeto = datetime.strptime(dado[4], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_boleto = dado[8]
            valor = self.formatar_moeda(valor_boleto)
            boleto = {
                'num_nota': dado[1],
                'notas': dado[2],
                'fornecedor': dado[3],
                'data_vencimento': data_formatada,
                'valor': valor
            }
            boletos.append(boleto)
           
        return boletos

    def valor_boleto(self):
        dados = self.db.get_boletos()
        boletos = [dado[8] for dado in dados]
        soma = sum(boletos)
        result = self.formatar_moeda(soma)
        return result

    def filtrar_boletos(self, data_inicio=None, data_fim=None, fornecedor=None):
        dados = self.db.obter_boletos_filtrados(
            data_inicio, data_fim, fornecedor)
        boletos = []
        for dado in dados:
           
            data_objeto = datetime.strptime(dado[4], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_boleto = dado[8]
            valor = self.formatar_moeda(valor_boleto)
            boleto = {
                'num_nota': dado[1],
                'notas': dado[2],
                'fornecedor': dado[3],
                'data_vencimento': data_formatada,
                'valor': valor
            }
            boletos.append(boleto)
            
        return boletos

    def filtrar_boletos_valor(self, data_inicio=None, data_fim=None, fornecedor=None):
        dados = self.db.obter_boletos_filtrados(
            data_inicio, data_fim, fornecedor)
        boletos = [dado[8] for dado in dados]
        soma = sum(boletos)
        result = self.formatar_moeda(soma)
        return result

    def valor_gastos(self, mes, ano):
        notas = self.db.get_valor_notas(mes, ano)
        valores = []
        for nota in notas:
            valores.append(nota[0])
        valor_soma = sum(valores)
        valor_total = self.formatar_moeda(valor_soma)
       
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


    def todos_os_boletos_por_nota(self, num_nota):
        dados = self.db.get_boletos_por_nota(num_nota)
        boletos = []
        for dado in dados:
            data_objeto = datetime.strptime(dado[3], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_boleto = dado[7]
            valor = self.formatar_moeda(valor_boleto)
            boleto = {
                'num_nota': dado[0],
                'notas': dado[1],
                'fornecedor': dado[2],
                'data_vencimento': data_formatada,
                'valor': valor
            }
            boletos.append(boleto)
            
        return boletos


    def valor_gastos_boletos_valor(self, num_nota):
        notas = self.db.get_boletos_por_nota_valor(num_nota)
        valores = [nota[0] for nota in notas]
        valor_soma = sum(valores)
        valor_total = self.formatar_moeda(valor_soma)
        return valor_total
    
    def dados_gastos(self, mes, ano):
        #Dados das despesas e subcategorias
        
        despesas = self.db.get_despesas()
        

       
        sub_categorias = self.db.get_all_subcategorias()
       

        # Função para somar valores de um período específico
        def somar_valores_por_subcategoria(subcategoria, mes=None, ano=None):
            #print(f"Calculando valores para subcategoria: {subcategoria}, mês: {mes}, ano: {ano}")
            notas = self.db.notas_por_subcategoria(subcategoria, mes, ano)
            #print(f"Notas obtidas para subcategoria {subcategoria}: {notas}")
            if notas is None:
                print(f"Nenhuma nota encontrada para subcategoria {subcategoria}")
                return
            valores = [dado[13] for dado in notas]
            soma = sum(valores)
            #print(f"Soma dos valores para subcategoria {subcategoria}: {soma}")
            return soma

        def somar_valores_por_categoria(categoria, mes=None, ano=None):
            
            notas = self.db.notas_por_categoria(categoria[1], mes, ano)
            
            if notas is None:
                
                return 0
            valores = [dado[13] for dado in notas]
            soma = sum(valores)
           
            return soma

        # Construir os dados finais com soma dos valores
        dados = []
        for despesa in despesas:
            #print(f"Processando despesa: {despesa}")
            subs = []
            valor = somar_valores_por_categoria(despesa, mes, ano)
            for sub in sub_categorias:
                #print(f'Sub: {sub}')
                if sub[2] == despesa[1]:  # Ajuste para verificar o nome da despesa
                    # Calcular valores da subcategoria
                    valor_mes = somar_valores_por_subcategoria(sub[3], mes=mes, ano=ano)
                    subs.append({
                        "codigo": sub[1],  # Ajuste para corresponder ao índice correto
                        "descricao": sub[3],
                        "valor_mes": self.formatar_moeda(valor_mes),
                    })
            dados.append({
                "despesa": despesa[1],
                "subs": subs,
                "valor": self.formatar_moeda(valor)
            })
        
        import pprint
        pprint.pprint(dados)
        
            
        return dados
        # Exibir os dados

    def buscar_notas(self, mes, ano):
        notas = self.db.get_all_notas_mes(mes, ano)
        
        output = []
        if notas:
            for nota in notas:
                data_objeto = datetime.strptime(nota[7], "%Y-%m-%d")
                data_formatada = data_objeto.strftime("%d/%m/%Y")
                valor_nota = nota[12]
                valor = self.formatar_moeda(valor_nota)
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
                    'tipo_despesa': nota[13],
                    'obs': nota[14]
                }
                output.append(nfe)
            return output
        else:
            notas = []
            return notas
        
    def buscar_boletos(self, mes, ano):
        dados = self.db.get_boletos_mes(mes, ano)
        boletos = []
        for dado in dados:
            
            data_objeto = datetime.strptime(dado[4], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_boleto = dado[8]
            valor = self.formatar_moeda(valor_boleto)
            boleto = {
                'num_nota': dado[1],
                'notas': dado[2],
                'fornecedor': dado[3],
                'data_vencimento': data_formatada,
                'valor': valor
            }
            boletos.append(boleto)
            
        return boletos
    


class DadosGastosMorumbi:

    def __init__(self):
        self.db = gastos_db.GastosDataBaseMorumbi()
    
    def formatar_moeda(self, valor):
        if valor is None:
            return "R$ 0"
        if not isinstance(valor, (int, float)):
            raise ValueError("O valor deve ser um número ou None.")
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def boletos_do_dia(self, dia, mes, ano):
        dados = self.db.get_boleto_by_day(dia, mes, ano)
        valores = []
        boletos = []
        for dado in dados:
            valor = f'R$ {dado[8]:.2f}'
            data_objeto = datetime.strptime(dado[4], "%Y-%m-%d")
            data = data_objeto.strftime("%d/%m/%Y")
            boleto = {
                'numero_nota': dado[1],
                'notas': dado[2],
                'fornecedor': dado[3],
                'vencimento': data,
                'valor': valor
            }

            valores.append(dado[8])
            boletos.append(boleto)
        return boletos

    def valor_a_pagar(self, dia, mes, ano):
        dados = self.db.get_boleto_by_day(dia, mes, ano)
        valores = []
        for dado in dados:
            valores.append(dado[8])
        a_pagar = sum(valores)
        valor_a_pagar = self.formatar_moeda(a_pagar)
        return valor_a_pagar

    def cadastrar_despesa(self, despesa):
        cadastrar = self.db.set_despesas(despesa)
        

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
            valor_total = self.formatar_moeda(valor_soma)
            dados_despesas.append((despesa[0], valor_total))
        return dados_despesas

    def todas_as_notas(self):
        notas = self.db.get_all_notas()
        output = []
        for nota in notas:
           
            data_objeto = datetime.strptime(nota[8], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_nota = nota[13]
            valor = self.formatar_moeda(valor_nota)
            nfe = {
                'pago_por': nota[1],
                'emitido_para': nota[2],
                'status': nota[3],
                'boleto': nota[4],
                'numero_nota': nota[5],
                'fornecedor': nota[7],
                'data_emissao': data_formatada,
                'valor': valor,
                'duplicata': nota[6],
                'tipo_despesa': nota[14],
                'obs': nota[15]
            }
            output.append(nfe)
        return output
    
    def todas_as_notas_mes(self, mes, ano):
        
        notas = self.db.get_all_notas_mes(mes, ano)
        
        output = []
        if notas:
            for nota in notas:
                data_objeto = datetime.strptime(nota[8], "%Y-%m-%d")
                data_formatada = data_objeto.strftime("%d/%m/%Y")
                valor_nota = nota[13]
                valor = self.formatar_moeda(valor_nota)
                nfe = {
                    'pago_por': nota[1],
                    'emitido_para': nota[2],
                    'status': nota[3],
                    'boleto': nota[4],
                    'numero_nota': nota[5],
                    'fornecedor': nota[7],
                    'data_emissao': data_formatada,
                    'valor': valor,
                    'duplicata': nota[6],
                    'tipo_despesa': nota[14],
                    'obs': nota[15]
                }
                output.append(nfe)
            return output
        else:
            notas = []
            return notas

    def valor_nota(self):
        notas = self.db.get_all_notas()
        output = [nota[13] for nota in notas]
        soma = sum(output)
        result = self.formatar_moeda(soma)
        return result

    def filtrar_notas(self, data_inicio=None, data_fim=None, fornecedor=None, despesa=None, obs=None):
        resultado = self.db.obter_notas_filtradas(
            data_inicio, data_fim, fornecedor, despesa, obs)
       
        notas = []
        for dados in resultado:
            data_objeto = datetime.strptime(dados[8], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_nota = dados[13]
            valor = self.formatar_moeda(valor_nota)
            nfe = {
                'pago_por': dados[1],
                'emitido_para': dados[2],
                'status': dados[3],
                'boleto': dados[4],
                'numero_nota': dados[5],
                'fornecedor': dados[7],
                'data_emissao': data_formatada,
                'valor': valor,
                'duplicata': dados[6],
                'tipo_despesa': dados[14],
                'obs': dados[15]
            }
            notas.append(nfe)
        return notas

    def filtrar_notas_valor(self, data_inicio=None, data_fim=None, fornecedor=None, despesa=None, obs=None):
        resultado = self.db.obter_notas_filtradas(
            data_inicio, data_fim, fornecedor, despesa,obs)
        valores = [dados[13] for dados in resultado]
        soma = sum(valores)
        result = self.formatar_moeda(soma)
        return result

    def nota_por_numero(self, num_nota):
        dados = self.db.get_nota_por_numero(num_nota)
       
        if dados:
            data_objeto = datetime.strptime(dados[8], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_nota = dados[13]
            valor = self.formatar_moeda(valor_nota)
            nfe = {
                'fornecedor': dados[7],
                'data_emissao': data_formatada,
                'valor': valor,
                'obs': dados[15]
            }
            return nfe

    def todos_os_boletos(self):
        dados = self.db.get_boletos()
        boletos = []
        for dado in dados:
            
            data_objeto = datetime.strptime(dado[4], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_boleto = dado[8]
            valor = self.formatar_moeda(valor_boleto)
            boleto = {
                'num_nota': dado[1],
                'notas': dado[2],
                'fornecedor': dado[3],
                'data_vencimento': data_formatada,
                'valor': valor
            }
            boletos.append(boleto)
            
        return boletos
    
    def todos_os_boletos_por_nota(self, num_nota):
        dados = self.db.get_boletos_por_nota(num_nota)
        boletos = []
        for dado in dados:
            data_objeto = datetime.strptime(dado[4], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_boleto = dado[8]
            valor = self.formatar_moeda(valor_boleto)
            boleto = {
                'num_nota': dado[1],
                'notas': dado[2],
                'fornecedor': dado[3],
                'data_vencimento': data_formatada,
                'valor': valor
            }
            boletos.append(boleto)
            
        return boletos


    def valor_gastos_boletos_valor(self, num_nota):
        notas = self.db.get_boletos_por_nota_valor(num_nota)
        valores = [nota[0] for nota in notas]
        valor_soma = sum(valores)
        valor_total = self.formatar_moeda(valor_soma)
        return valor_total

    def filtrar_boletos(self, data_inicio=None, data_fim=None, fornecedor=None):
        dados = self.db.obter_boletos_filtrados(
            data_inicio, data_fim, fornecedor)
        boletos = []
        for dado in dados:
            
            data_objeto = datetime.strptime(dado[4], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_boleto = dado[8]
            valor = self.formatar_moeda(valor_boleto)
            boleto = {
                'num_nota': dado[1],
                'notas': dado[2],
                'fornecedor': dado[3],
                'data_vencimento': data_formatada,
                'valor': valor
            }
            boletos.append(boleto)
           
        return boletos

    def valor_gastos(self, mes, ano):
        notas = self.db.get_valor_notas(mes, ano)
        valores = []
        for nota in notas:
            valores.append(nota[0])
        valor_soma = sum(valores)
        valor_total = self.formatar_moeda(valor_soma)
        
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
        boletos = [dado[8] for dado in dados]
        soma = sum(boletos)
        result = self.formatar_moeda(soma)
        return result

    def valor_boleto(self):
        dados = self.db.get_boletos()
        boletos = [dado[8] for dado in dados]
        soma = sum(boletos)
        result = f'R$ {soma:.2f}'
        return result
    
    def dados_gastos(self, mes, ano):
        #Dados das despesas e subcategorias
        #print("Obtendo despesas...")
        despesas = self.db.get_despesas()
        #print(f"Despesas obtidas: {despesas}")

        #print("Obtendo subcategorias...")
        sub_categorias = self.db.get_all_subcategorias()
        #print(f"Subcategorias obtidas: {sub_categorias}")

        # Função para somar valores de um período específico
        def somar_valores_por_subcategoria(subcategoria, mes=None, ano=None):
            #print(f"Calculando valores para subcategoria: {subcategoria}, mês: {mes}, ano: {ano}")
            notas = self.db.notas_por_subcategoria(subcategoria, mes, ano)
            #print(f"Notas obtidas para subcategoria {subcategoria}: {notas}")
            if notas is None:
                print(f"Nenhuma nota encontrada para subcategoria {subcategoria}")
                return
            valores = [dado[13] for dado in notas]
            soma = sum(valores)
            #print(f"Soma dos valores para subcategoria {subcategoria}: {soma}")
            return soma

        def somar_valores_por_categoria(categoria, mes=None, ano=None):
            
            notas = self.db.notas_por_categoria(categoria[1], mes, ano)
            
            if notas is None:
                
                return 0
            valores = [dado[13] for dado in notas]
            soma = sum(valores)
            
            return soma

        # Construir os dados finais com soma dos valores
        dados = []
        for despesa in despesas:
            
            subs = []
            valor = somar_valores_por_categoria(despesa, mes, ano)
            for sub in sub_categorias:
               
                if sub[2] == despesa[1]:  # Ajuste para verificar o nome da despesa
                    # Calcular valores da subcategoria
                    valor_mes = somar_valores_por_subcategoria(sub[3], mes=mes, ano=ano)
                    subs.append({
                        "codigo": sub[1],  # Ajuste para corresponder ao índice correto
                        "descricao": sub[3],
                        "valor_mes": self.formatar_moeda(valor_mes),
                    })
            dados.append({
                "despesa": despesa[1],
                "subs": subs,
                "valor": self.formatar_moeda(valor)
            })
        
        import pprint
        
            
        return dados
        # Exibir os dados
        
    def buscar_notas(self, mes, ano):
        
        notas = self.db.get_all_notas_mes(mes, ano)
        
        output = []
        if notas:
            for nota in notas:
                data_objeto = datetime.strptime(nota[8], "%Y-%m-%d")
                data_formatada = data_objeto.strftime("%d/%m/%Y")
                valor_nota = nota[13]
                valor = self.formatar_moeda(valor_nota)
                nfe = {
                    'pago_por': nota[1],
                    'emitido_para': nota[2],
                    'status': nota[3],
                    'boleto': nota[4],
                    'numero_nota': nota[5],
                    'fornecedor': nota[7],
                    'data_emissao': data_formatada,
                    'valor': valor,
                    'duplicata': nota[8],
                    'tipo_despesa': nota[14],
                    'obs': nota[15],
                    'sub': nota[16]
                }
                output.append(nfe)
            return output
        else:
            notas = []
            return notas
        
    def buscar_boletos(self, mes, ano):
        dados = self.db.get_boletos_mes(mes, ano)
        boletos = []
        for dado in dados:
            
            data_objeto = datetime.strptime(dado[4], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%d/%m/%Y")
            valor_boleto = dado[8]
            valor = self.formatar_moeda(valor_boleto)
            boleto = {
                'num_nota': dado[1],
                'notas': dado[2],
                'fornecedor': dado[3],
                'data_vencimento': data_formatada,
                'valor': valor
            }
            boletos.append(boleto)
            
        return boletos