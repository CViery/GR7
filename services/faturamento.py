from database import conection
import json
import pyodbc

from datetime import datetime


class Faturamento:
    def __init__(self):
        self.db = conection.Database()

    def formatar_moeda(self, valor):
        """
        Formata um valor numérico como uma string de moeda no formato brasileiro (R$).
        
        Parâmetros:
            valor (float): O valor numérico a ser formatado.
            
        Retorna:
            str: O valor formatado como moeda no formato brasileiro (R$).
        """
        try:
            # Formatação do valor como moeda no formato brasileiro
            return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except Exception as e:
            # Caso haja um erro, retornamos uma mensagem
            return f"Erro ao formatar o valor: {e}"

    def cadastrar(self, dados, usuario):
        try:
            # Valida campos obrigatórios
            required_fields = [
                'data_faturamento', 'pecas', 'servicos', 'revitalizacao', 'aditivo',
                'fluido_sangria', 'palheta', 'detergente_parabrisa', 'filtro',
                'pneus', 'bateria', 'valor_oleo', 'valor_dinheiro', 'freios',
                'suspensao', 'injecao_ignicao', 'cabeote_motor_arrefecimento', 'outros',
                'oleos', 'transmissao', 'placa', 'modelo_veiculo', 'data_orcamento',
                'dias', 'num_os', 'cia', 'conversao_pneustore', 'valor_total',
                'quantidade_aditivo', 'modelo_bateria', 'quantidade_oleo',
                'tipo_marca_oleo', 'mecanico', 'filtro_mecanico', 'valor_meta', 'terceiros'
            ]

            for field in required_fields:
                if field not in dados:
                    raise ValueError(f"Campo obrigatório ausente: {field}")

            # Processa dados da ordem de serviço
            data = dados['data_faturamento']
            mes, ano = data[5:7], data[:4]

            # Função para processar valores monetários
            def process_value(value_str):
                return float(value_str.replace(',', '.'))

            ordem_servico = {
                'placa': dados['placa'],
                'modelo_veiculo': dados['modelo_veiculo'],
                'data_orcamento': dados['data_orcamento'],
                'data_faturamento': dados['data_faturamento'],
                'mes_faturamento': mes,
                'ano_faturamento': ano,
                'dias_servico': int(dados['dias']),
                'numero_os': int(dados['num_os']),
                'companhia': dados['cia'],
                'conversao_ps': dados['conversao_pneustore'],
                'valor_pecas': process_value(dados['pecas']),
                'valor_servicos': process_value(dados['servicos']),
                'total_os': float(dados['valor_total']),
                'valor_revitalizacao': process_value(dados['revitalizacao']),
                'valor_aditivo': process_value(dados['aditivo']),
                'quantidade_litros': int(dados['quantidade_aditivo']),
                'valor_fluido_sangria': process_value(dados['fluido_sangria']),
                'valor_palheta': process_value(dados['palheta']),
                'valor_limpeza_freios': process_value(dados.get('limpeza_freios', '0')),
                'valor_pastilha_parabrisa': process_value(dados['detergente_parabrisa']),
                'valor_filtro': process_value(dados['filtro']),
                'valor_pneu': process_value(dados['pneus']),
                'valor_bateria': process_value(dados['bateria']),
                'modelo_bateria': dados['modelo_bateria'],
                'lts_oleo_motor': int(dados['quantidade_oleo']),
                'valor_lt_oleo': process_value(dados['valor_oleo']),
                'marca_e_tipo_oleo': dados['tipo_marca_oleo'],
                'mecanico_servico': dados['mecanico'],
                'servico_filtro': dados['filtro_mecanico'],
                'valor_p_meta': process_value(dados['valor_meta']),
                'valor_em_dinheiro': process_value(dados['valor_dinheiro']),
                'valor_servico_freios': process_value(dados['freios']),
                'valor_servico_suspensao': process_value(dados['suspensao']),
                'valor_servico_injecao_ignicao': process_value(dados['injecao_ignicao']),
                'valor_servico_cabecote_motor_arr': process_value(dados['cabeote_motor_arrefecimento']),
                'valor_outros_servicos': process_value(dados['outros']),
                'valor_servicos_oleos': process_value(dados['oleos']),
                'valor_servico_transmissao': process_value(dados['transmissao']),
                'usuario': usuario,
                'obs': dados.get('obs', ''),  # Caso o campo 'obs' seja opcional
                'valor_terceiros': process_value(dados['terceiros'])
            }
           
            # Verifica se a ordem de serviço já existe
            buscar_os = self.db.buscar_os_by_number(int(dados['num_os']))
            if buscar_os:
                return True  # Ordem já cadastrada, retorna True
            else:
                # Cadastra a ordem de serviço
                self.db.cadastrar_faturamento(ordem_servico)
                return False  # Ordem cadastrada com sucesso

        except ValueError as ve:
            print(f"Erro de validação: {ve}")
        except Exception as e:
            print(f"Erro ao cadastrar ordem de serviço: {e}")

    def filtrar_os(self, data_inicio=None, data_fim=None, placa=None, mecanico=None, num_os=None, cia=None):
        try:
            # Obtém as ordens de serviço filtradas do banco de dados
            faturamento = self.db.obter_ordens_filtradas(
                data_inicio, data_fim, placa, mecanico, num_os, cia)
            faturamentos = []

            for ordem_servico in faturamento:
                # Formata as datas
                data_objeto_orcamento = datetime.strptime(
                    ordem_servico[3], "%Y-%m-%d")
                data_orcamento = data_objeto_orcamento.strftime("%d/%m/%Y")
                data_objeto_faturamento = datetime.strptime(
                    ordem_servico[4], "%Y-%m-%d")
                data_faturamento = data_objeto_faturamento.strftime("%d/%m/%Y")

                # Cria um dicionário com as informações formatadas
                os = {
                    'placa': ordem_servico[1],
                    'modelo_veiculo': ordem_servico[2],
                    'data_orcamento': data_orcamento,
                    'data_faturamento': data_faturamento,
                    'dias_servico': ordem_servico[7],
                    'numero_os': ordem_servico[8],
                    'companhia': ordem_servico[9],
                    'valor_pecas': self.formatar_moeda(ordem_servico[11]),
                    'valor_servicos': self.formatar_moeda(ordem_servico[12]),
                    'total_os': self.formatar_moeda(ordem_servico[13]),
                    'valor_revitalizacao': self.formatar_moeda(ordem_servico[14]),
                    'valor_aditivo': self.formatar_moeda(ordem_servico[15]),
                    'quantidade_litros': ordem_servico[16],
                    'valor_fluido_sangria': self.formatar_moeda(ordem_servico[17]),
                    'valor_palheta': self.formatar_moeda(ordem_servico[18]),
                    'valor_limpeza_freios': self.formatar_moeda(ordem_servico[19]),
                    'valor_pastilha_parabrisa': self.formatar_moeda(ordem_servico[20]),
                    'valor_filtro': self.formatar_moeda(ordem_servico[21]),
                    'valor_pneu': self.formatar_moeda(ordem_servico[22]),
                    'valor_bateria': self.formatar_moeda(ordem_servico[23]),
                    'modelo_bateria': ordem_servico[24],
                    'lts_oleo_motor': ordem_servico[25],
                    'valor_lt_oleo': self.formatar_moeda(ordem_servico[26]),
                    'marca_e_tipo_oleo': ordem_servico[27],
                    'mecanico_servico': ordem_servico[29],
                    'servico_filtro': ordem_servico[30],
                    'valor_p_meta': self.formatar_moeda(ordem_servico[28]),
                    'valor_em_dinheiro': self.formatar_moeda(ordem_servico[31]),
                    'valor_servico_freios': self.formatar_moeda(ordem_servico[32]),
                    'valor_servico_suspensao': self.formatar_moeda(ordem_servico[33]),
                    'valor_servico_injecao_ignicao': self.formatar_moeda(ordem_servico[34]),
                    'valor_servico_cabecote_motor_arr': self.formatar_moeda(ordem_servico[35]),
                    'valor_outros_servicos': self.formatar_moeda(ordem_servico[36]),
                    'valor_servicos_oleos': self.formatar_moeda(ordem_servico[37]),
                    'valor_servico_transmissao': self.formatar_moeda(ordem_servico[38]),
                    'obs':ordem_servico[40]
                }
                faturamentos.append(os)
                
            return faturamentos
        except Exception as e:
            print(f"Erro ao obter faturamentos: {e}")
            return []
        
    def filtrar_valores(self, data_inicio=None, data_fim=None, placa=None, mecanico=None, num_os=None, cia=None):
        try:
            dados = self.db.obter_ordens_filtradas(
                data_inicio, data_fim, placa, mecanico, num_os, cia)
            
            valores_total = [dado[12] for dado in dados]
            valores_meta = [dado[12] for dado in dados]

        except Exception as e:
            print(e)
    def faturamento_total_mes(self, mes, ano):
        """
        Calcula o faturamento total para um mês e ano específicos.

        :param mes: Mês para o qual o faturamento deve ser calculado (formato 'MM').
        :param ano: Ano para o qual o faturamento deve ser calculado (formato 'YYYY').
        :return: Valor total do faturamento formatado como moeda.
        """
        try:
            # Obtém os dados de faturamento do banco de dados
            dados = self.db.faturamento_mes(mes, ano)
            # Extrai os valores da lista de dados
            valores = [dado[0] for dado in dados]
          
            # Calcula a soma dos valores
            valor_soma = sum(valores)

            # Formata o valor total como moeda
            valor_total = self.formatar_moeda(valor_soma)

            return valor_total
        except Exception as e:
            print(f"Erro ao calcular faturamento total do mês: {e}")
            raise

    def faturamento_meta_mes(self, mes, ano):
        try:
            
            dados = self.db.faturamento_mes_meta(mes, ano)
            
            valores = [dado[0] for dado in dados]
            valor_soma = sum(valores)
            valor_total = self.formatar_moeda(valor_soma)
            return valor_total
        except Exception as e:
            print(f"Erro ao calcular faturamento total da meta do mês: {e}")
            raise e
    
    def faturamento_meta_mes_int(self, mes, ano):
        try:
            dados = self.db.faturamento_mes_meta(mes, ano)
            valores = [dado[0] for dado in dados]
            valor_soma = sum(valores)
            valor_total = valor_soma
            return valor_total
        except Exception as e:
            print(f"Erro ao calcular faturamento total da meta do mês: {e}")
            raise e

    def faturamento_mecanico(self, mes, ano):
        try:
            faturamentos = []
            mecanicos = self.db.get_mecanicos()
            
            for mecanico in mecanicos:
                print(mecanico)
                # Faturamento de serviço por mecânico
                dados = self.db.faturamento_por_mecanico(mecanico[0], mes, ano) or []
                valores = [dado[0] for dado in dados]
                valor_soma = sum(valores)
                valor_total = self.formatar_moeda(valor_soma)

                # Faturamento de peças por mecanico
                dados_pecas = self.db.faturamento_por_mecanico_peças(mecanico[0], mes, ano) or []
                pecas = [dado[0] for dado in dados_pecas]
                valor_soma_peças = sum(pecas)
                valor_pecas = self.formatar_moeda(valor_soma_peças)

                # Dados de filtros
                dados_filtro = self.db.get_qntd_filtros_mec(mecanico[0], mes, ano) or []
                qntd_filtro = [qntd[0] for qntd in dados_filtro]
                filtro_valor = self.db.valor_filtro(mes, ano, mecanico[0])
                if not filtro_valor:
                    filtro_valor = 0
                # Se filtro_valor for um float, soma diretamente, senão soma a lista
                filtro_count = len(qntd_filtro)

                # Dados de revitalização
                dados_revitalizacao = self.db.get_revitalizacao_mecanico(mecanico[0], mes, ano) or []
                valores_revi = [valor[0] for valor in dados_revitalizacao if valor[0] > 0.00]
                qntd_revi = len(valores_revi)
                valor_soma_revi = sum(valores_revi)
                valor_total_revi = self.formatar_moeda(valor_soma_revi)

                # Adicionando ao faturamento
                faturamentos.append((
                    mecanico[0],         # Nome do mecânico ou identificador
                    valor_total,         # Valor total faturado (formatado)
                    valor_pecas,
                    len(valores),        # Quantidade de serviços
                    filtro_count,        # Quantidade de filtros
                    filtro_valor,
                    qntd_revi,           # Quantidade de revitalizações
                    valor_total_revi,    # Valor total de revitalizações (formatado)
                             # Soma dos valores de filtros
                ))

            return faturamentos

        except Exception as e:
            print(f"Erro ao calcular faturamento dos mecânicos: {e}")
            raise e

    def valor_filtro_mecanico(self, mecanico, mes, ano):
        dados = self.db.valor_filtro(mecanico, mes, ano)
        return dados
        
    def faturamento_companhia(self, mes, ano):
        try:
            faturamentos = []
            cias = self.db.get_cias()
            for cia in cias:
                dados = self.db.faturamento_cia(cia[1], mes, ano)
                valores = [dado[0] for dado in dados]
                valor_soma = sum(valores)
                valor_total = self.formatar_moeda(valor_soma)
                faturamentos.append((cia[1], valor_total, len(valores)))
            return faturamentos
        except Exception as e:
            raise e

    def faturamento_servico(self, mes, ano):
        try:
            faturamento = []
            servicos = self.db.buscar_serv()
            
            for servico in servicos:
                
                dados = self.db.faturamento_serv(servico[1], mes, ano)
                valores = []
                for valor in dados:
                    if valor[0] > 0.00:
                        valores.append(valor[0])
                valor_soma = sum(valores)
                valor_total = self.formatar_moeda(valor_soma)
                faturamento.append((servico[1], valor_total, len(valores)))
            return faturamento
        except Exception as e:
            raise e

    def faturamentos_gerais(self):
        try:
            faturamentos = []
            faturamento = self.db.faturamento_geral()
            
            for ordem_servico in faturamento:
                data_objeto_orcamento = datetime.strptime(
                    ordem_servico[3], "%Y-%m-%d")
                data_orcamento = data_objeto_orcamento.strftime("%d/%m/%Y")
                data_objeto_faturamento = datetime.strptime(
                    ordem_servico[4], "%Y-%m-%d")
                data_faturamento = data_objeto_faturamento.strftime("%d/%m/%Y")
                os = {
                    'placa': ordem_servico[1],
                    'modelo_veiculo': ordem_servico[2],
                    'data_orcamento': data_orcamento,
                    'data_faturamento': data_faturamento,
                    'dias_servico': ordem_servico[7],
                    'numero_os': ordem_servico[8],
                    'companhia': ordem_servico[9],
                    'valor_pecas': self.formatar_moeda(ordem_servico[11]),
                    'valor_servicos': self.formatar_moeda(ordem_servico[12]),
                    'total_os': self.formatar_moeda(ordem_servico[13]),
                    'valor_revitalizacao': self.formatar_moeda(ordem_servico[14]),
                    'valor_aditivo': self.formatar_moeda(ordem_servico[15]),
                    'quantidade_litros': ordem_servico[16],
                    'valor_fluido_sangria': self.formatar_moeda(ordem_servico[17]),
                    'valor_palheta': self.formatar_moeda(ordem_servico[18]),
                    'valor_limpeza_freios': self.formatar_moeda(ordem_servico[19]),
                    'valor_pastilha_parabrisa': self.formatar_moeda(ordem_servico[20]),
                    'valor_filtro': self.formatar_moeda(ordem_servico[21]),
                    'valor_pneu': self.formatar_moeda(ordem_servico[22]),
                    'valor_bateria': self.formatar_moeda(ordem_servico[23]),
                    'modelo_bateria': ordem_servico[24],
                    'lts_oleo_motor': ordem_servico[25],
                    'valor_lt_oleo': self.formatar_moeda(ordem_servico[26]),
                    'marca_e_tipo_oleo': ordem_servico[27],
                    'mecanico_servico': ordem_servico[29],
                    'servico_filtro': ordem_servico[30],
                    'valor_p_meta': self.formatar_moeda(ordem_servico[28]),
                    'valor_em_dinheiro': self.formatar_moeda(ordem_servico[31]),
                    'valor_servico_freios': self.formatar_moeda(ordem_servico[32]),
                    'valor_servico_suspensao': self.formatar_moeda(ordem_servico[33]),
                    'valor_servico_injecao_ignicao': self.formatar_moeda(ordem_servico[34]),
                    'valor_servico_cabecote_motor_arr': self.formatar_moeda(ordem_servico[35]),
                    'valor_outros_servicos': self.formatar_moeda(ordem_servico[36]),
                    'valor_servicos_oleos': self.formatar_moeda(ordem_servico[37]),
                    'valor_servico_transmissao': self.formatar_moeda(ordem_servico[38]),
                    'obs':ordem_servico[40]
                }
                print(os)
                faturamentos.append(os)
            return faturamentos
        except Exception as e:
            print(f"Erro ao obter faturamentos: {e}")
            return []

        except Exception as e:
            pass

    def companhias(self):
        try:
            cias = []
            dados = self.db.get_cias()
            for cia in dados:
                cias.append(cia[1])

            return cias

        except Exception as e:
            print(e)

    def funcionarios(self):
        try:
            mecanicos = []
            dados = self.db.get_mecanicos()
            for mecanico in dados:
                mecanicos.append(mecanico[0])

            return mecanicos

        except Exception as e:
            print(e)

    def faturamento_dinheiro(self, mes, ano):
        try:
            dados = self.db.faturamento_dinheiro(mes, ano)
            valores = [dado[0] for dado in dados]
            soma = sum(valores)
            result = self.formatar_moeda(soma)
            return result
        except Exception as e:
            print(e)

    def faturamento_dinheiro_ordens(self, mes, ano):
        try:
            dados = self.db.faturamento_dinheiro_ordens(mes, ano)
            faturamentos = []
            for ordem_servico in dados:
                data_objeto_orcamento = datetime.strptime(
                    ordem_servico[3], "%Y-%m-%d")
                data_orcamento = data_objeto_orcamento.strftime("%d/%m/%Y")
                data_objeto_faturamento = datetime.strptime(
                    ordem_servico[4], "%Y-%m-%d")
                data_faturamento = data_objeto_faturamento.strftime("%d/%m/%Y")
                if ordem_servico[31] > 0:
                    os = {
                    'placa': ordem_servico[1],
                    'modelo_veiculo': ordem_servico[2],
                    'data_orcamento': data_orcamento,
                    'data_faturamento': data_faturamento,
                    'dias_servico': ordem_servico[7],
                    'numero_os': ordem_servico[8],
                    'companhia': ordem_servico[9],
                    'valor_pecas': self.formatar_moeda(ordem_servico[11]),
                    'valor_servicos': self.formatar_moeda(ordem_servico[12]),
                    'total_os': self.formatar_moeda(ordem_servico[13]),
                    'valor_revitalizacao': self.formatar_moeda(ordem_servico[14]),
                    'valor_aditivo': self.formatar_moeda(ordem_servico[15]),
                    'quantidade_litros': ordem_servico[16],
                    'valor_fluido_sangria': self.formatar_moeda(ordem_servico[17]),
                    'valor_palheta': self.formatar_moeda(ordem_servico[18]),
                    'valor_limpeza_freios': self.formatar_moeda(ordem_servico[19]),
                    'valor_pastilha_parabrisa': self.formatar_moeda(ordem_servico[20]),
                    'valor_filtro': self.formatar_moeda(ordem_servico[21]),
                    'valor_pneu': self.formatar_moeda(ordem_servico[22]),
                    'valor_bateria': self.formatar_moeda(ordem_servico[23]),
                    'modelo_bateria': ordem_servico[24],
                    'lts_oleo_motor': ordem_servico[25],
                    'valor_lt_oleo': self.formatar_moeda(ordem_servico[26]),
                    'marca_e_tipo_oleo': ordem_servico[27],
                    'mecanico_servico': ordem_servico[29],
                    'servico_filtro': ordem_servico[30],
                    'valor_p_meta': self.formatar_moeda(ordem_servico[28]),
                    'valor_em_dinheiro': self.formatar_moeda(ordem_servico[31]),
                    'valor_servico_freios': self.formatar_moeda(ordem_servico[32]),
                    'valor_servico_suspensao': self.formatar_moeda(ordem_servico[33]),
                    'valor_servico_injecao_ignicao': self.formatar_moeda(ordem_servico[34]),
                    'valor_servico_cabecote_motor_arr': self.formatar_moeda(ordem_servico[35]),
                    'valor_outros_servicos': self.formatar_moeda(ordem_servico[36]),
                    'valor_servicos_oleos': self.formatar_moeda(ordem_servico[37]),
                    'valor_servico_transmissao': self.formatar_moeda(ordem_servico[38]),
                    'obs':ordem_servico[40]
                }
                    faturamentos.append(os)
            return faturamentos
        except Exception as e:
            print(e)

    def filtrar_os_valor(self, data_inicio=None, data_fim=None, placa=None, mecanico=None, num_os=None, cia=None):
        try:
            # Obtém as ordens de serviço filtradas do banco de dados
            faturamento = self.db.obter_ordens_filtradas(
                data_inicio, data_fim, placa, mecanico, num_os, cia)
            valores = [dados[13] for dados in faturamento]
            soma = sum(valores)
            result = self.formatar_moeda(soma)
            return result
        except Exception as e:
            print(e)
    def filtrar_os_valor_meta(self, data_inicio=None, data_fim=None, placa=None, mecanico=None, num_os=None, cia=None):
        try:
            # Obtém as ordens de serviço filtradas do banco de dados
            faturamento = self.db.obter_ordens_filtradas(
                data_inicio, data_fim, placa, mecanico, num_os, cia)
            valores = [dados[28] for dados in faturamento]
            soma = sum(valores)
            result = self.formatar_moeda(soma)
            return result
        except Exception as e:
            print(e)
    def faturamentos_gerais_valor(self):
        try:
            faturamento = self.db.faturamento_geral()
            faturamentos = [dados[13] for dados in faturamento]
            soma = sum(faturamentos)
            result = self.formatar_moeda(soma)
            return result
        except Exception as e:
            print(e)

    def faturamentos_gerais_valor_meta(self):
        try:
            faturamento = self.db.faturamento_geral()
            faturamentos = [dados[28] for dados in faturamento]
            soma = sum(faturamentos)
            result = self.formatar_moeda(soma)
            return result
        except Exception as e:
            print(e)
    
    def filtros_mecanico(self, mes, ano):
        try: 
            mecanicos = self.db.get_mecanicos()  # Obtém a lista de mecânicos
            dados = []
            
            for mecanico in mecanicos:
                if mecanico[0] == 'BATERIA_DOMICILIO':
                    continue  # Ignora o mecânico 'BATERIA_DOMICILIO'
                if mecanico[0] == 'OUTROS':
                    continue  # Ignora o mecânico 'BATERIA_DOMICILIO'
                if mecanico[0] == 'DOMICILIO':
                    continue  # Ignora o mecânico 'BATERIA_DOMICILIO'
                if mecanico[0] == 'TERCEIROS':
                    continue  # Ignora o mecânico 'BATERIA_DOMICILIO'

                filtros = self.db.relatorio_filtro(mes, ano, mecanico[0])
               
                # Filtra apenas valores numéricos
                filtro_valores = [info[0] for info in filtros]
                valor = sum(filtro_valores)  # Soma os valores
                quantidade = len(filtro_valores)  # Conta as entradas

                dados.append({
                    'mecanico': mecanico[0],
                    'valor': valor,
                    'quantidade': quantidade
                })

              # Mostra os resultados finais
            return dados  # Retorna os dados processados

        except Exception as e:
            print(f"Erro ao processar filtros: {e}")  # Mensagem detalhada do erro
            return []  # Retorna uma lista vazia em caso de erro
        
    def revitalizacao_mecanico(self, mes, ano):
        try: 
            mecanicos = self.db.get_mecanicos()  # Obtém a lista de mecânicos
            dados = []
            
            for mecanico in mecanicos:
                if mecanico[0] == 'BATERIA_DOMICILIO':
                    continue  # Ignora o mecânico 'BATERIA_DOMICILIO'
                if mecanico[0] == 'OUTROS':
                    continue  # Ignora o mecânico 'BATERIA_DOMICILIO'
                if mecanico[0] == 'DOMICILIO':
                    continue  # Ignora o mecânico 'BATERIA_DOMICILIO'
                if mecanico[0] == 'TERCEIROS':
                    continue  # Ignora o mecânico 'BATERIA_DOMICILIO'

                revitalizacoes = self.db.relatorio_revitalizacao(mes, ano, mecanico[0])
               
                # Filtra apenas valores numéricos
                revitalizacao_valores = []
                for info in revitalizacoes:
                    if info[0] != 0.0:
                        revitalizacao_valores.append(info[0])

                valor = sum(revitalizacao_valores)  # Soma os valores
                quantidade = len(revitalizacao_valores)  # Conta as entradas

                dados.append({
                    'mecanico': mecanico[0],
                    'valor': valor,
                    'quantidade': quantidade
                })

              # Mostra os resultados finais
            return dados  # Retorna os dados processados

        except Exception as e:
            print(f"Erro ao processar revitalizacao: {e}")  # Mensagem detalhada do erro
            return []  # Retorna uma lista vazia em caso de erro
    
    

    def ordem_de_servico(self, num_os):
        try:
            # Buscando a ordem de serviço pelo número
            db = self.db.buscar_os_by_number(num_os)
            
            # Verificando se não há retorno
            if not db:
                return json.dumps({"erro": "Ordem de serviço não encontrada"}, ensure_ascii=False)
            
            

            # Lista das chaves fornecidas
            keys = [
                "placa", "modelo_veiculo", "data_orcamento", "data_faturamento",
                "mes_faturamento", "ano_faturamento", "dias", "num_os", "cia",
                "conversao_pneustore", "pecas", "servicos", "valor_os",
                "revitalizacao", "aditivo", "quantidade_aditivo", "fluido_sangria",
                "palheta", "limpeza_freios", "detergente_parabrisa", "filtro",
                "pneus", "bateria", "modelo_bateria", "quantidade_oleo",
                "valor_oleo", "tipo_marca_oleo", "valor_meta", "mecanico",
                "filtro_mecanico", "valor_dinheiro", "freios", "suspensao",
                "injecao_ignicao", "cabecote_motor_arrefecimento", "outros",
                "oleos", "transmissao", "usuario", "observacoes"
            ]
            
            # Convertendo os dados
            if isinstance(db, pyodbc.Row):
                db_dict = {key: value for key, value in zip(keys, db)}
            else:
                return json.dumps({"erro": "Formato de dados inesperado", "tipo": str(type(db))}, ensure_ascii=False)
            
            # Retornando o dicionário como JSON
            return json.dumps(db_dict, ensure_ascii=False)
        
        except Exception as e:
            print(f"Erro ao buscar ordem de serviço: {e}")
            return json.dumps({"erro": "Não foi possível buscar a ordem de serviço"}, ensure_ascii=False)

    def ordens_filtro_e_higienizacao(self, mes, ano, mecanico):
        try:
            # Adicionando print para verificar os parâmetros recebidos
            print(f"Mes: {mes}, Ano: {ano}, Mecânico: {mecanico}")
            
            dados = self.db.detalhes_filtros(mes, ano, mecanico)
            
            # Verificando os dados obtidos de detalhes_filtros
            print(f"Dados recebidos de detalhes_filtros: {dados}")
            
            faturamentos = []
            
            for ordem_servico in dados:
                # Verificando os dados de cada ordem de serviço
                print(f"Processando ordem de serviço: {ordem_servico}")
                
                data_objeto_orcamento = datetime.strptime(ordem_servico[3], "%Y-%m-%d")
                
                data_objeto_faturamento = datetime.strptime(ordem_servico[4], "%Y-%m-%d")
                data_faturamento = data_objeto_faturamento.strftime("%d/%m/%Y")
                
                # Verificando a condição do valor na posição 30
                os = {
                        'placa': ordem_servico[1],
                        'data_faturamento': data_faturamento,
                        'numero_os': ordem_servico[8],
                        'companhia': ordem_servico[9],
                        'valor_pecas': self.formatar_moeda(ordem_servico[11]),
                        'valor_servicos': self.formatar_moeda(ordem_servico[12]),
                        'total_os': self.formatar_moeda(ordem_servico[13]),
                        'valor_revitalizacao': self.formatar_moeda(ordem_servico[14]),
                        'valor_aditivo': self.formatar_moeda(ordem_servico[15]),
                        'quantidade_litros': ordem_servico[16],
                        'valor_fluido_sangria': self.formatar_moeda(ordem_servico[17]),
                        'valor_limpeza_freios': self.formatar_moeda(ordem_servico[19]),
                        'valor_filtro': self.formatar_moeda(ordem_servico[21]),
                        'valor_pneu': self.formatar_moeda(ordem_servico[22]),
                        'valor_bateria': self.formatar_moeda(ordem_servico[23]),
                        'lts_oleo_motor': ordem_servico[25],
                        'valor_lt_oleo': self.formatar_moeda(ordem_servico[26]),
                        'mecanico_servico': ordem_servico[29],
                        'servico_filtro': ordem_servico[30],
                        'valor_p_meta': self.formatar_moeda(ordem_servico[28]),
                        'obs': ordem_servico[40]
                    }
                    
                    # Verificando o objeto os antes de adicionar
                print(f"Ordem de serviço preparada para adicionar: {os}")
                    
                faturamentos.append(os)
            
            # Verificando o resultado final
            print(f"Faturamentos preparados: {faturamentos}")
            
            return faturamentos
        except Exception as e:
            # Verificando erros
            print(f"Erro ao processar ordens de serviço: {e}")

    def ordens_revitalizacao(self, mes, ano, mecanico):
        try:
            # Adicionando print para verificar os parâmetros recebidos
            print(f"Mes: {mes}, Ano: {ano}, Mecânico: {mecanico}")
            
            dados = self.db.detalhes_revitalizacao(mes, ano, mecanico)
            
            # Verificando os dados obtidos de detalhes_filtros
            print(f"Dados recebidos de detalhes_filtros: {dados}")
            
            faturamentos = []
            
            for ordem_servico in dados:
                if ordem_servico[14] > 0:
                    # Verificando os dados de cada ordem de serviço
                    print(f"Processando ordem de serviço: {ordem_servico}")
                    
                    data_objeto_orcamento = datetime.strptime(ordem_servico[3], "%Y-%m-%d")
                    
                    data_objeto_faturamento = datetime.strptime(ordem_servico[4], "%Y-%m-%d")
                    data_faturamento = data_objeto_faturamento.strftime("%d/%m/%Y")
                    
                    # Verificando a condição do valor na posição 30
                    os = {
                            'placa': ordem_servico[1],
                            'data_faturamento': data_faturamento,
                            'numero_os': ordem_servico[8],
                            'companhia': ordem_servico[9],
                            'valor_pecas': self.formatar_moeda(ordem_servico[11]),
                            'valor_servicos': self.formatar_moeda(ordem_servico[12]),
                            'total_os': self.formatar_moeda(ordem_servico[13]),
                            'valor_revitalizacao': self.formatar_moeda(ordem_servico[14]),
                            'valor_aditivo': self.formatar_moeda(ordem_servico[15]),
                            'quantidade_litros': ordem_servico[16],
                            'valor_fluido_sangria': self.formatar_moeda(ordem_servico[17]),
                            'valor_limpeza_freios': self.formatar_moeda(ordem_servico[19]),
                            'valor_filtro': self.formatar_moeda(ordem_servico[21]),
                            'valor_pneu': self.formatar_moeda(ordem_servico[22]),
                            'valor_bateria': self.formatar_moeda(ordem_servico[23]),
                            'lts_oleo_motor': ordem_servico[25],
                            'valor_lt_oleo': self.formatar_moeda(ordem_servico[26]),
                            'mecanico_servico': ordem_servico[29],
                            'servico_filtro': ordem_servico[30],
                            'valor_p_meta': self.formatar_moeda(ordem_servico[28]),
                            'obs': ordem_servico[40]
                        }
                        
                        # Verificando o objeto os antes de adicionar
                    print(f"Ordem de serviço preparada para adicionar: {os}")
                        
                    faturamentos.append(os)
                
            # Verificando o resultado final
            print(f"Faturamentos preparados: {faturamentos}")
            
            return faturamentos
        except Exception as e:
            # Verificando erros
            print(f"Erro ao processar ordens de serviço: {e}")
    
    def ordens_dinheiro_relat(self, mes, ano):
        try:
            # Adicionando print para verificar os parâmetros recebidos
            print(f"Mes: {mes}, Ano: {ano}")
            
            dados = self.db.ordens(mes, ano)
            
            # Verificando os dados obtidos de detalhes_filtros
            print(f"Dados recebidos de detalhes_filtros: {dados}")
            
            faturamentos = []
            
            for ordem_servico in dados:
                if ordem_servico[31] > 0:
                    # Verificando os dados de cada ordem de serviço
                    print(f"Processando ordem de serviço: {ordem_servico}")
                    
                    data_objeto_orcamento = datetime.strptime(ordem_servico[3], "%Y-%m-%d")
                    
                    data_objeto_faturamento = datetime.strptime(ordem_servico[4], "%Y-%m-%d")
                    data_faturamento = data_objeto_faturamento.strftime("%d/%m/%Y")
                    
                    # Verificando a condição do valor na posição 30
                    os = {
                            'placa': ordem_servico[1],
                            'data_faturamento': data_faturamento,
                            'numero_os': ordem_servico[8],
                            'companhia': ordem_servico[9],
                            'valor_pecas': self.formatar_moeda(ordem_servico[11]),
                            'valor_servicos': self.formatar_moeda(ordem_servico[12]),
                            'total_os': self.formatar_moeda(ordem_servico[13]),
                            'valor_revitalizacao': self.formatar_moeda(ordem_servico[14]),
                            'valor_aditivo': self.formatar_moeda(ordem_servico[15]),
                            'quantidade_litros': ordem_servico[16],
                            'valor_fluido_sangria': self.formatar_moeda(ordem_servico[17]),
                            'valor_limpeza_freios': self.formatar_moeda(ordem_servico[19]),
                            'valor_filtro': self.formatar_moeda(ordem_servico[21]),
                            'valor_pneu': self.formatar_moeda(ordem_servico[22]),
                            'valor_bateria': self.formatar_moeda(ordem_servico[23]),
                            'lts_oleo_motor': ordem_servico[25],
                            'valor_lt_oleo': self.formatar_moeda(ordem_servico[26]),
                            'mecanico_servico': ordem_servico[29],
                            'servico_filtro': ordem_servico[30],
                            'valor_p_meta': self.formatar_moeda(ordem_servico[28]),
                            'valor_em_dinheiro': self.formatar_moeda(ordem_servico[31]),
                            'obs': ordem_servico[40]
                        }
                        
                        # Verificando o objeto os antes de adicionar
                    print(f"Ordem de serviço preparada para adicionar: {os}")
                        
                    faturamentos.append(os)
                
            # Verificando o resultado final
            print(f"Faturamentos preparados: {faturamentos}")
            
            return faturamentos
        except Exception as e:
            # Verificando erros
            print(f"Erro ao processar ordens de serviço: {e}")

    def faturamentos_ordens(self, mes, ano):
        try:
            faturamentos = []
            faturamento = self.db.faturamento_ordens(mes, ano)
            for ordem_servico in faturamento:
                data_objeto_orcamento = datetime.strptime(
                    ordem_servico[3], "%Y-%m-%d")
                data_orcamento = data_objeto_orcamento.strftime("%d/%m/%Y")
                data_objeto_faturamento = datetime.strptime(
                    ordem_servico[4], "%Y-%m-%d")
                data_faturamento = data_objeto_faturamento.strftime("%d/%m/%Y")
                os = {
                    'placa': ordem_servico[1],
                    'modelo_veiculo': ordem_servico[2],
                    'data_orcamento': data_orcamento,
                    'data_faturamento': data_faturamento,
                    'dias_servico': ordem_servico[7],
                    'numero_os': ordem_servico[8],
                    'companhia': ordem_servico[9],
                    'valor_pecas': self.formatar_moeda(ordem_servico[11]),
                    'valor_servicos': self.formatar_moeda(ordem_servico[12]),
                    'total_os': self.formatar_moeda(ordem_servico[13]),
                    'valor_revitalizacao': self.formatar_moeda(ordem_servico[14]),
                    'valor_aditivo': self.formatar_moeda(ordem_servico[15]),
                    'quantidade_litros': ordem_servico[16],
                    'valor_fluido_sangria': self.formatar_moeda(ordem_servico[17]),
                    'valor_palheta': self.formatar_moeda(ordem_servico[18]),
                    'valor_limpeza_freios': self.formatar_moeda(ordem_servico[19]),
                    'valor_pastilha_parabrisa': self.formatar_moeda(ordem_servico[20]),
                    'valor_filtro': self.formatar_moeda(ordem_servico[21]),
                    'valor_pneu': self.formatar_moeda(ordem_servico[22]),
                    'valor_bateria': self.formatar_moeda(ordem_servico[23]),
                    'modelo_bateria': ordem_servico[24],
                    'lts_oleo_motor': ordem_servico[25],
                    'valor_lt_oleo': self.formatar_moeda(ordem_servico[26]),
                    'marca_e_tipo_oleo': ordem_servico[27],
                    'mecanico_servico': ordem_servico[29],
                    'servico_filtro': ordem_servico[30],
                    'valor_p_meta': self.formatar_moeda(ordem_servico[28]),
                    'valor_em_dinheiro': self.formatar_moeda(ordem_servico[31]),
                    'valor_servico_freios': self.formatar_moeda(ordem_servico[32]),
                    'valor_servico_suspensao': self.formatar_moeda(ordem_servico[33]),
                    'valor_servico_injecao_ignicao': self.formatar_moeda(ordem_servico[34]),
                    'valor_servico_cabecote_motor_arr': self.formatar_moeda(ordem_servico[35]),
                    'valor_outros_servicos': self.formatar_moeda(ordem_servico[36]),
                    'valor_servicos_oleos': self.formatar_moeda(ordem_servico[37]),
                    'valor_servico_transmissao': self.formatar_moeda(ordem_servico[38]),
                    'obs':ordem_servico[40]
                }
                faturamentos.append(os)
            return faturamentos
        except Exception as e:
            print(f"Erro ao obter faturamentos: {e}")
            return []
    
class FaturamentoPortal():
    def __init__(self):
        self.db = conection.DatabasePortal()

    def formatar_moeda(self, valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def cadastrar(self, dados, usuario):
        try:
            data = dados['data_faturamento']
            mes = data[5:7]
            ano = data[:4]
            pecas_str = dados['pecas']
            pecas = pecas_str.replace(',', '.')
            servico_str = dados['servicos']
            servico = servico_str.replace(',', '.')
            revitalizacao_str = dados['revitalizacao']
            revitalizacao = revitalizacao_str.replace(',', '.')
            if 'aditivo' in dados:
                aditivo_str = dados['aditivo']
                lts = int(dados['quantidade_aditivo'])
            if 'ar_condicionado' in dados:
                aditivo_str = dados['ar_condicionado']
                lts = 0
            aditivo = aditivo_str.replace(',', '.')
            fluido_sangria_str = dados['fluido_sangria']
            fluido_sangria = fluido_sangria_str.replace(',', '.')
            palheta_str = dados['palheta']
            palheta = palheta_str.replace(',', '.')
            if 'limpeza_freios' in dados:
                limpeza_freios_str = dados['limpeza_freios']
            if 'funilaria' in dados:
                limpeza_freios_str = dados['funilaria']
            limpeza_freios = limpeza_freios_str.replace(',', '.')
            detergente_parabrisa_str = dados['detergente_parabrisa']
            detergente_parabrisa = detergente_parabrisa_str.replace(',', '.')
            filtro_str = dados['filtro']
            filtro = filtro_str.replace(',', '.')
            pneus_str = dados['pneus']
            pneus = pneus_str.replace(',', '.')
            bateria_str = dados['bateria']
            bateria = bateria_str.replace(',', '.')
            oleo_str = dados['valor_oleo']
            oleo = oleo_str.replace(',', '.')
            valor_dinheiro_str = dados['valor_dinheiro']
            valor_dinheiro = valor_dinheiro_str.replace(',', '.')
            freios_str = dados['freios']
            freios = freios_str.replace(',', '.')
            suspensao_str = dados['suspensao']
            suspensao = suspensao_str.replace(',', '.')
            injecao_str = dados['injecao_ignicao']
            injecao = injecao_str.replace(',', '.')
            motor_str = dados['cabeote_motor_arrefecimento']
            motor = motor_str.replace(',', '.')
            outros_str = dados['outros']
            outros = outros_str.replace(',', '.')
            lubrificantes_str = dados['oleos']
            lubrificantes = lubrificantes_str.replace(',', '.')
            transmissao_str = dados['transmissao']
            transissao = transmissao_str.replace(',', '.')
            ordem_servico = {
                'placa': dados['placa'],
                'modelo_veiculo': dados['modelo_veiculo'],
                'data_orcamento': dados['data_orcamento'],
                'data_faturamento': dados['data_faturamento'],
                'mes_faturamento': mes,
                'ano_faturamento': ano,
                'dias_servico': int(dados['dias']),
                'numero_os': int(dados['num_os']),
                'companhia': dados['cia'],
                'conversao_ps': dados['conversao_pneustore'],
                'valor_pecas': float(pecas),
                'valor_servicos': float(servico),
                'total_os': float(dados['valor_total']),
                'valor_revitalizacao': float(revitalizacao),
                'valor_aditivo': float(aditivo),
                'quantidade_litros': lts,
                'valor_fluido_sangria': float(fluido_sangria),
                'valor_palheta': float(palheta),
                'valor_limpeza_freios': float(limpeza_freios),
                'valor_pastilha_parabrisa': float(detergente_parabrisa),
                'valor_filtro': float(filtro),
                'valor_pneu': float(pneus),
                'valor_bateria': float(bateria),
                'modelo_bateria': dados['modelo_bateria'],
                'lts_oleo_motor': int(dados['quantidade_oleo']),
                'valor_lt_oleo': float(oleo),
                'marca_e_tipo_oleo': dados['tipo_marca_oleo'],
                'mecanico_servico': dados['mecanico'],
                'servico_filtro': dados['filtro_mecanico'],
                'valor_p_meta': float(dados['valor_meta']),
                'valor_em_dinheiro': float(valor_dinheiro),
                'valor_servico_freios': float(freios),
                'valor_servico_suspensao': float(suspensao),
                'valor_servico_injecao_ignicao': float(injecao),
                'valor_servico_cabecote_motor_arr': float(motor),
                'valor_outros_servicos': float(outros),
                'valor_servicos_oleos': float(lubrificantes),
                'valor_servico_transmissao': float(transissao),
                'usuario': usuario,
                'obs':dados['obs']
            }
            buscar_os = self.db.buscar_os_by_number(int(dados['num_os']))
            if buscar_os:
                return True
            else:
                # Cadastra a ordem de serviço no banco de dados
                self.db.cadastrar_faturamento(ordem_servico)
                return False

        except Exception as e:
            print(e)

    def faturamento_total_mes(self, mes, ano):
        try:
            dados = self.db.faturamento_mes(mes, ano)
            valores = [dado[0] for dado in dados]

            valor_soma = sum(valores)
            valor_total = self.formatar_moeda(valor_soma)
            return valor_total
        except Exception as e:
            print(f"Erro ao calcular faturamento total do mês: {e}")
            raise e

    def faturamento_meta_mes(self, mes, ano):
        try:
            dados = self.db.faturamento_mes_meta(mes, ano)

            valores = [dado[0] for dado in dados]
            valor_soma = sum(valores)
            valor_total = self.formatar_moeda(valor_soma)
            return valor_total
        except Exception as e:
            print(f"Erro ao calcular faturamento total da meta do mês: {e}")
            raise e

    def faturamento_mecanico(self, mes, ano):
        try:
            faturamentos = []
            mecanicos = self.db.get_mecanicos()
            
            for mecanico in mecanicos:
                #print(f'mecanico : {mecanico}')
                # Faturamento de serviço por mecânico
                dados = self.db.faturamento_por_mecanico(mecanico[0], mes, ano) or []
                #print(f'Dados Mecanico: {dados}')
                valores = [dado[0] for dado in dados]
                valor_soma = sum(valores)
                valor_total = self.formatar_moeda(valor_soma)

                # Faturamento de peças por mecanico
                dados_pecas = self.db.faturamento_por_mecanico_peças(mecanico[0], mes, ano) or []
                #print(f' Peças {dados_pecas}')
                pecas = [dado[0] for dado in dados_pecas]
                valor_soma_peças = sum(pecas)
                valor_pecas = self.formatar_moeda(valor_soma_peças)

                # Dados de filtros
                dados_filtro = self.db.get_qntd_filtros_mec(mecanico[0], mes, ano) or []
                #print(f' filtro : {dados_filtro}')
                #print(f'mes fat: {mes}')
                qntd_filtro = [qntd[0] for qntd in dados_filtro]
                filtro_valor = self.db.valor_filtro(mes, ano, mecanico[0])
                if not filtro_valor:
                    filtro_valor = 0
                # Se filtro_valor for um float, soma diretamente, senão soma a lista
                filtro_count = len(qntd_filtro)

                # Dados de revitalização
                dados_revitalizacao = self.db.get_revitalizacao_mecanico(mecanico[0], mes, ano) or []
                #print(f'REv: {dados_revitalizacao}')
                valores_revi = [valor[0] for valor in dados_revitalizacao if valor[0] > 0.00]
                qntd_revi = len(valores_revi)
                valor_soma_revi = sum(valores_revi)
                valor_total_revi = self.formatar_moeda(valor_soma_revi)

                # Adicionando ao faturamento
                faturamentos.append((
                    mecanico[0],         # Nome do mecânico ou identificador
                    valor_total,         # Valor total faturado (formatado)
                    valor_pecas,
                    len(valores),        # Quantidade de serviços
                    filtro_count,        # Quantidade de filtros
                    filtro_valor,
                    qntd_revi,           # Quantidade de revitalizações
                    valor_total_revi,    # Valor total de revitalizações (formatado)
                             # Soma dos valores de filtros
                ))
            #print(f'infos: {faturamentos}')
            return faturamentos

        except Exception as e:
            print(f"Erro ao calcular faturamento dos mecânicos: {e}")
            raise e
    def faturamento_companhia(self, mes, ano):
        try:
            faturamentos = []
            cias = self.db.get_cias()
            for cia in cias:
                dados = self.db.faturamento_cia(cia[1], mes, ano)
                valores = [dado[0] for dado in dados]
                valor_soma = sum(valores)
                valor_total = self.formatar_moeda(valor_soma)
                faturamentos.append((cia[1], valor_total, len(valores)))
            return faturamentos
        except Exception as e:
            raise e

    def faturamento_servico(self, mes, ano):
        try:
            faturamento = []
            servicos = self.db.buscar_serv()
            for servico in servicos:
                dados = self.db.faturamento_serv(servico[1], mes, ano)
                valores = []
                for valor in dados:
                    if valor[0] > 0.00:
                        valores.append(valor[0])
                valor_soma = sum(valores)
                valor_total = self.formatar_moeda(valor_soma)
                faturamento.append((servico[1], valor_total, len(valores)))
            return faturamento
        except Exception as e:
            raise e

    def faturamentos_gerais(self):
        try:
            faturamentos = []
            faturamento = self.db.faturamento_geral()
            for ordem_servico in faturamento:
                data_objeto_orcamento = datetime.strptime(
                    ordem_servico[3], "%Y-%m-%d")
                data_orcamento = data_objeto_orcamento.strftime("%d/%m/%Y")
                data_objeto_faturamento = datetime.strptime(
                    ordem_servico[4], "%Y-%m-%d")
                data_faturamento = data_objeto_faturamento.strftime("%d/%m/%Y")
                os = {
                    'placa': ordem_servico[1],
                    'modelo_veiculo': ordem_servico[2],
                    'data_orcamento': data_orcamento,
                    'data_faturamento': data_faturamento,
                    'dias_servico': ordem_servico[7],
                    'numero_os': ordem_servico[8],
                    'companhia': ordem_servico[9],
                    'valor_pecas': self.formatar_moeda(ordem_servico[11]),
                    'valor_servicos': self.formatar_moeda(ordem_servico[12]),
                    'total_os': self.formatar_moeda(ordem_servico[13]),
                    'valor_revitalizacao': self.formatar_moeda(ordem_servico[14]),
                    'valor_aditivo': self.formatar_moeda(ordem_servico[15]),
                    'quantidade_litros': ordem_servico[16],
                    'valor_fluido_sangria': self.formatar_moeda(ordem_servico[17]),
                    'valor_palheta': self.formatar_moeda(ordem_servico[18]),
                    'valor_limpeza_freios': self.formatar_moeda(ordem_servico[19]),
                    'valor_pastilha_parabrisa': self.formatar_moeda(ordem_servico[20]),
                    'valor_filtro': self.formatar_moeda(ordem_servico[21]),
                    'valor_pneu': self.formatar_moeda(ordem_servico[22]),
                    'valor_bateria': self.formatar_moeda(ordem_servico[23]),
                    'modelo_bateria': ordem_servico[24],
                    'lts_oleo_motor': ordem_servico[25],
                    'valor_lt_oleo': self.formatar_moeda(ordem_servico[26]),
                    'marca_e_tipo_oleo': ordem_servico[27],
                    'mecanico_servico': ordem_servico[29],
                    'servico_filtro': ordem_servico[30],
                    'valor_p_meta': self.formatar_moeda(ordem_servico[28]),
                    'valor_em_dinheiro': self.formatar_moeda(ordem_servico[31]),
                    'valor_servico_freios': self.formatar_moeda(ordem_servico[32]),
                    'valor_servico_suspensao': self.formatar_moeda(ordem_servico[33]),
                    'valor_servico_injecao_ignicao': self.formatar_moeda(ordem_servico[34]),
                    'valor_servico_cabecote_motor_arr': self.formatar_moeda(ordem_servico[35]),
                    'valor_outros_servicos': self.formatar_moeda(ordem_servico[36]),
                    'valor_servicos_oleos': self.formatar_moeda(ordem_servico[37]),
                    'valor_servico_transmissao': self.formatar_moeda(ordem_servico[38]),
                    'obs':ordem_servico[40]
                }
                faturamentos.append(os)
            return faturamentos
        except Exception as e:
            print(f"Erro ao obter faturamentos: {e}")
            return []

        except Exception as e:
            pass

    def filtrar_os(self, data_inicio=None, data_fim=None, placa=None, mecanico=None, num_os=None, cia=None):
        try:
            print(num_os)
            # Obtém as ordens de serviço filtradas do banco de dados
            faturamento = self.db.obter_ordens_filtradas(
                data_inicio, data_fim, placa, mecanico, num_os, cia)
            faturamentos = []

            for ordem_servico in faturamento:
                # Formata as datas
                data_objeto_orcamento = datetime.strptime(
                    ordem_servico[3], "%Y-%m-%d")
                data_orcamento = data_objeto_orcamento.strftime("%d/%m/%Y")
                data_objeto_faturamento = datetime.strptime(
                    ordem_servico[4], "%Y-%m-%d")
                data_faturamento = data_objeto_faturamento.strftime("%d/%m/%Y")

                # Cria um dicionário com as informações formatadas
                os = {
                    'placa': ordem_servico[1],
                    'modelo_veiculo': ordem_servico[2],
                    'data_orcamento': data_orcamento,
                    'data_faturamento': data_faturamento,
                    'dias_servico': ordem_servico[7],
                    'numero_os': ordem_servico[8],
                    'companhia': ordem_servico[9],
                    'valor_pecas': self.formatar_moeda(ordem_servico[11]),
                    'valor_servicos': self.formatar_moeda(ordem_servico[12]),
                    'total_os': self.formatar_moeda(ordem_servico[13]),
                    'valor_revitalizacao': self.formatar_moeda(ordem_servico[14]),
                    'valor_aditivo': self.formatar_moeda(ordem_servico[15]),
                    'quantidade_litros': ordem_servico[16],
                    'valor_fluido_sangria': self.formatar_moeda(ordem_servico[17]),
                    'valor_palheta': self.formatar_moeda(ordem_servico[18]),
                    'valor_limpeza_freios': self.formatar_moeda(ordem_servico[19]),
                    'valor_pastilha_parabrisa': self.formatar_moeda(ordem_servico[20]),
                    'valor_filtro': self.formatar_moeda(ordem_servico[21]),
                    'valor_pneu': self.formatar_moeda(ordem_servico[22]),
                    'valor_bateria': self.formatar_moeda(ordem_servico[23]),
                    'modelo_bateria': ordem_servico[24],
                    'lts_oleo_motor': ordem_servico[25],
                    'valor_lt_oleo': self.formatar_moeda(ordem_servico[26]),
                    'marca_e_tipo_oleo': ordem_servico[27],
                    'mecanico_servico': ordem_servico[30],
                    'servico_filtro': ordem_servico[31],
                    'valor_p_meta': self.formatar_moeda(ordem_servico[28]),
                    'valor_em_dinheiro': self.formatar_moeda(ordem_servico[31]),
                    'valor_servico_freios': self.formatar_moeda(ordem_servico[32]),
                    'valor_servico_suspensao': self.formatar_moeda(ordem_servico[33]),
                    'valor_servico_injecao_ignicao': self.formatar_moeda(ordem_servico[34]),
                    'valor_servico_cabecote_motor_arr': self.formatar_moeda(ordem_servico[35]),
                    'valor_outros_servicos': self.formatar_moeda(ordem_servico[36]),
                    'valor_servicos_oleos': self.formatar_moeda(ordem_servico[37]),
                    'valor_servico_transmissao': self.formatar_moeda(ordem_servico[38]),
                    'obs':ordem_servico[40]
                }
                faturamentos.append(os)
                
            return faturamentos
        except Exception as e:
            print(f"Erro ao obter faturamentos: {e}")
            return []
    def companhias(self):
        try:
            cias = []
            dados = self.db.get_cias()
            for cia in dados:
                cias.append(cia[1])

            return cias

        except Exception as e:
            print(e)

    def funcionarios(self):
        try:
            mecanicos = []
            dados = self.db.get_mecanicos()
            for mecanico in dados:
                mecanicos.append(mecanico[0])

            return mecanicos

        except Exception as e:
            print(e)

    def faturamento_dinheiro(self, mes, ano):
        try:
            dados = self.db.faturamento_dinheiro(mes, ano)
            valores = [dado[0] for dado in dados]
            soma = sum(valores)
            result = f'R$ {soma:.2f}'
            return result
        except Exception as e:
            print(e)
    
    def faturamento_meta_mes_int(self, mes, ano):
        try:
            dados = self.db.faturamento_mes_meta(mes, ano)
            valores = [dado[0] for dado in dados]
            valor_soma = sum(valores)
            valor_total = valor_soma
            return valor_total
        except Exception as e:
            print(f"Erro ao calcular faturamento total da meta do mês: {e}")
            raise e
    
    def filtrar_os_valor(self, data_inicio=None, data_fim=None, placa=None, mecanico=None, num_os=None, cia=None):
        try:
            # Obtém as ordens de serviço filtradas do banco de dados
            faturamento = self.db.obter_ordens_filtradas(
                data_inicio, data_fim, placa, mecanico, num_os, cia)
            valores = [dados[13] for dados in faturamento]
            soma = sum(valores)
            result = self.formatar_moeda(soma)
            return result
        except Exception as e:
            print(e)
    def faturamentos_gerais_valor(self):
        try:
            faturamento = self.db.faturamento_geral()
            faturamentos = [dados[13] for dados in faturamento]
            soma = sum(faturamentos)
            result = self.formatar_moeda(soma)
            return result
        except Exception as e:
            print(e)
    def filtrar_os_valor_meta(self, data_inicio=None, data_fim=None, placa=None, mecanico=None, num_os=None, cia=None):
        try:
            # Obtém as ordens de serviço filtradas do banco de dados
            faturamento = self.db.obter_ordens_filtradas(
                data_inicio, data_fim, placa, mecanico, num_os, cia)
            valores = [dados[28] for dados in faturamento]
            soma = sum(valores)
            result = self.formatar_moeda(soma)
            return result
        except Exception as e:
            print(e)
    def faturamentos_gerais_valor_meta(self):
        try:
            faturamento = self.db.faturamento_geral()
            faturamentos = [dados[28] for dados in faturamento]
            soma = sum(faturamentos)
            result = self.formatar_moeda(soma)
            return result
        except Exception as e:
            print(e)
    
    def faturamento_dinheiro_ordens(self, mes, ano):
        try:
            dados = self.db.faturamento_dinheiro_ordens(mes, ano)
            faturamentos = []
            for ordem_servico in dados:
                data_objeto_orcamento = datetime.strptime(
                    ordem_servico[3], "%Y-%m-%d")
                data_orcamento = data_objeto_orcamento.strftime("%d/%m/%Y")
                data_objeto_faturamento = datetime.strptime(
                    ordem_servico[4], "%Y-%m-%d")
                data_faturamento = data_objeto_faturamento.strftime("%d/%m/%Y")
                if ordem_servico[31] > 0:
                    os = {
                    'placa': ordem_servico[1],
                    'modelo_veiculo': ordem_servico[2],
                    'data_orcamento': data_orcamento,
                    'data_faturamento': data_faturamento,
                    'dias_servico': ordem_servico[7],
                    'numero_os': ordem_servico[8],
                    'companhia': ordem_servico[9],
                    'valor_pecas': self.formatar_moeda(ordem_servico[11]),
                    'valor_servicos': self.formatar_moeda(ordem_servico[12]),
                    'total_os': self.formatar_moeda(ordem_servico[13]),
                    'valor_revitalizacao': self.formatar_moeda(ordem_servico[14]),
                    'valor_aditivo': self.formatar_moeda(ordem_servico[15]),
                    'quantidade_litros': ordem_servico[16],
                    'valor_fluido_sangria': self.formatar_moeda(ordem_servico[17]),
                    'valor_palheta': self.formatar_moeda(ordem_servico[18]),
                    'valor_limpeza_freios': self.formatar_moeda(ordem_servico[19]),
                    'valor_pastilha_parabrisa': self.formatar_moeda(ordem_servico[20]),
                    'valor_filtro': self.formatar_moeda(ordem_servico[21]),
                    'valor_pneu': self.formatar_moeda(ordem_servico[22]),
                    'valor_bateria': self.formatar_moeda(ordem_servico[23]),
                    'modelo_bateria': ordem_servico[24],
                    'lts_oleo_motor': ordem_servico[25],
                    'valor_lt_oleo': self.formatar_moeda(ordem_servico[26]),
                    'marca_e_tipo_oleo': ordem_servico[27],
                    'mecanico_servico': ordem_servico[29],
                    'servico_filtro': ordem_servico[30],
                    'valor_p_meta': self.formatar_moeda(ordem_servico[28]),
                    'valor_em_dinheiro': self.formatar_moeda(ordem_servico[31]),
                    'valor_servico_freios': self.formatar_moeda(ordem_servico[32]),
                    'valor_servico_suspensao': self.formatar_moeda(ordem_servico[33]),
                    'valor_servico_injecao_ignicao': self.formatar_moeda(ordem_servico[34]),
                    'valor_servico_cabecote_motor_arr': self.formatar_moeda(ordem_servico[35]),
                    'valor_outros_servicos': self.formatar_moeda(ordem_servico[36]),
                    'valor_servicos_oleos': self.formatar_moeda(ordem_servico[37]),
                    'valor_servico_transmissao': self.formatar_moeda(ordem_servico[38]),
                    'obs':ordem_servico[40]
                }
                    faturamentos.append(os)
            return faturamentos
        except Exception as e:
            print(e)

    def revitalizacao_mecanico(self, mes, ano):
        try: 
            mecanicos = self.db.get_mecanicos()  # Obtém a lista de mecânicos
            dados = []
            
            for mecanico in mecanicos:
                if mecanico[0] == 'BATERIA_DOMICILIO':
                    continue  # Ignora o mecânico 'BATERIA_DOMICILIO'
                if mecanico[0] == 'OUTROS':
                    continue  # Ignora o mecânico 'BATERIA_DOMICILIO'

                revitalizacoes = self.db.relatorio_revitalizacao(mes, ano, mecanico[0])
               
                # Filtra apenas valores numéricos
                revitalizacao_valores = []
                for info in revitalizacoes:
                    if info[0] != 0.0:
                        revitalizacao_valores.append(info[0])

                valor = sum(revitalizacao_valores)  # Soma os valores
                quantidade = len(revitalizacao_valores)  # Conta as entradas

                dados.append({
                    'mecanico': mecanico[0],
                    'valor': valor,
                    'quantidade': quantidade
                })

            print(dados)  # Mostra os resultados finais
            return dados  # Retorna os dados processados

        except Exception as e:
            print(f"Erro ao processar revitalizacao: {e}")  # Mensagem detalhada do erro
            return []  # Retorna uma lista vazia em caso de erro
        

    def filtros_mecanico(self, mes, ano):
        try: 
            mecanicos = self.db.get_mecanicos()  # Obtém a lista de mecânicos
            dados = []
            
            for mecanico in mecanicos:
                if mecanico[0] == 'BATERIA_DOMICILIO':
                    continue  # Ignora o mecânico 'BATERIA_DOMICILIO'
                if mecanico[0] == 'OUTROS':
                    continue  # Ignora o mecânico 'BATERIA_DOMICILIO'

                filtros = self.db.relatorio_filtro(mes, ano, mecanico[0])
               
                # Filtra apenas valores numéricos
                filtro_valores = [info[0] for info in filtros]
                valor = sum(filtro_valores)  # Soma os valores
                quantidade = len(filtro_valores)  # Conta as entradas

                dados.append({
                    'mecanico': mecanico[0],
                    'valor': valor,
                    'quantidade': quantidade
                })

            print(dados)  # Mostra os resultados finais
            return dados  # Retorna os dados processados

        except Exception as e:
            print(f"Erro ao processar filtros: {e}")  # Mensagem detalhada do erro
            return []  # Retorna uma lista vazia em caso de erro
        
    
    def ordens_filtro_e_higienizacao(self, mes, ano, mecanico):
        try:
            # Adicionando print para verificar os parâmetros recebidos
            print(f"Mes: {mes}, Ano: {ano}, Mecânico: {mecanico}")
            
            dados = self.db.detalhes_filtros(mes, ano, mecanico)
            
            # Verificando os dados obtidos de detalhes_filtros
            print(f"Dados recebidos de detalhes_filtros: {dados}")
            
            faturamentos = []
            
            for ordem_servico in dados:
                # Verificando os dados de cada ordem de serviço
                print(f"Processando ordem de serviço: {ordem_servico}")
                
                data_objeto_orcamento = datetime.strptime(ordem_servico[3], "%Y-%m-%d")
                
                data_objeto_faturamento = datetime.strptime(ordem_servico[4], "%Y-%m-%d")
                data_faturamento = data_objeto_faturamento.strftime("%d/%m/%Y")
                
                # Verificando a condição do valor na posição 30
                os = {
                        'placa': ordem_servico[1],
                        'data_faturamento': data_faturamento,
                        'numero_os': ordem_servico[8],
                        'companhia': ordem_servico[9],
                        'valor_pecas': self.formatar_moeda(ordem_servico[11]),
                        'valor_servicos': self.formatar_moeda(ordem_servico[12]),
                        'total_os': self.formatar_moeda(ordem_servico[13]),
                        'valor_revitalizacao': self.formatar_moeda(ordem_servico[14]),
                        'valor_aditivo': self.formatar_moeda(ordem_servico[15]),
                        'quantidade_litros': ordem_servico[16],
                        'valor_fluido_sangria': self.formatar_moeda(ordem_servico[17]),
                        'valor_limpeza_freios': self.formatar_moeda(ordem_servico[19]),
                        'valor_filtro': self.formatar_moeda(ordem_servico[21]),
                        'valor_pneu': self.formatar_moeda(ordem_servico[22]),
                        'valor_bateria': self.formatar_moeda(ordem_servico[23]),
                        'lts_oleo_motor': ordem_servico[25],
                        'valor_lt_oleo': self.formatar_moeda(ordem_servico[26]),
                        'mecanico_servico': ordem_servico[29],
                        'servico_filtro': ordem_servico[30],
                        'valor_p_meta': self.formatar_moeda(ordem_servico[28]),
                        'obs': ordem_servico[40]
                    }
                    
                    # Verificando o objeto os antes de adicionar
                print(f"Ordem de serviço preparada para adicionar: {os}")
                    
                faturamentos.append(os)
            
            # Verificando o resultado final
            print(f"Faturamentos preparados: {faturamentos}")
            
            return faturamentos
        except Exception as e:
            # Verificando erros
            print(f"Erro ao processar ordens de serviço: {e}")

    def ordens_revitalizacao(self, mes, ano, mecanico):
        try:
            # Adicionando print para verificar os parâmetros recebidos
            print(f"Mes: {mes}, Ano: {ano}, Mecânico: {mecanico}")
            
            dados = self.db.detalhes_revitalizacao(mes, ano, mecanico)
            
            # Verificando os dados obtidos de detalhes_filtros
            print(f"Dados recebidos de detalhes_filtros: {dados}")
            
            faturamentos = []
            
            for ordem_servico in dados:
                if ordem_servico[14] > 0:
                    # Verificando os dados de cada ordem de serviço
                    print(f"Processando ordem de serviço: {ordem_servico}")
                    
                    data_objeto_orcamento = datetime.strptime(ordem_servico[3], "%Y-%m-%d")
                    
                    data_objeto_faturamento = datetime.strptime(ordem_servico[4], "%Y-%m-%d")
                    data_faturamento = data_objeto_faturamento.strftime("%d/%m/%Y")
                    
                    # Verificando a condição do valor na posição 30
                    os = {
                            'placa': ordem_servico[1],
                            'data_faturamento': data_faturamento,
                            'numero_os': ordem_servico[8],
                            'companhia': ordem_servico[9],
                            'valor_pecas': self.formatar_moeda(ordem_servico[11]),
                            'valor_servicos': self.formatar_moeda(ordem_servico[12]),
                            'total_os': self.formatar_moeda(ordem_servico[13]),
                            'valor_revitalizacao': self.formatar_moeda(ordem_servico[14]),
                            'valor_aditivo': self.formatar_moeda(ordem_servico[15]),
                            'quantidade_litros': ordem_servico[16],
                            'valor_fluido_sangria': self.formatar_moeda(ordem_servico[17]),
                            'valor_limpeza_freios': self.formatar_moeda(ordem_servico[19]),
                            'valor_filtro': self.formatar_moeda(ordem_servico[21]),
                            'valor_pneu': self.formatar_moeda(ordem_servico[22]),
                            'valor_bateria': self.formatar_moeda(ordem_servico[23]),
                            'lts_oleo_motor': ordem_servico[25],
                            'valor_lt_oleo': self.formatar_moeda(ordem_servico[26]),
                            'mecanico_servico': ordem_servico[29],
                            'servico_filtro': ordem_servico[30],
                            'valor_p_meta': self.formatar_moeda(ordem_servico[28]),
                            'obs': ordem_servico[40]
                        }
                        
                        # Verificando o objeto os antes de adicionar
                    print(f"Ordem de serviço preparada para adicionar: {os}")
                        
                    faturamentos.append(os)
                
            # Verificando o resultado final
            print(f"Faturamentos preparados: {faturamentos}")
            
            return faturamentos
        except Exception as e:
            # Verificando erros
            print(f"Erro ao processar ordens de serviço: {e}")

    
    def ordens_dinheiro_relat(self, mes, ano):
        try:
            # Adicionando print para verificar os parâmetros recebidos
            print(f"Mes: {mes}, Ano: {ano}")
            
            dados = self.db.ordens(mes, ano)
            
            # Verificando os dados obtidos de detalhes_filtros
            print(f"Dados recebidos de detalhes_filtros: {dados}")
            
            faturamentos = []
            
            for ordem_servico in dados:
                if ordem_servico[31] > 0:
                    # Verificando os dados de cada ordem de serviço
                    print(f"Processando ordem de serviço: {ordem_servico}")
                    
                    data_objeto_orcamento = datetime.strptime(ordem_servico[3], "%Y-%m-%d")
                    
                    data_objeto_faturamento = datetime.strptime(ordem_servico[4], "%Y-%m-%d")
                    data_faturamento = data_objeto_faturamento.strftime("%d/%m/%Y")
                    
                    # Verificando a condição do valor na posição 30
                    os = {
                            'placa': ordem_servico[1],
                            'data_faturamento': data_faturamento,
                            'numero_os': ordem_servico[8],
                            'companhia': ordem_servico[9],
                            'valor_pecas': self.formatar_moeda(ordem_servico[11]),
                            'valor_servicos': self.formatar_moeda(ordem_servico[12]),
                            'total_os': self.formatar_moeda(ordem_servico[13]),
                            'valor_revitalizacao': self.formatar_moeda(ordem_servico[14]),
                            'valor_aditivo': self.formatar_moeda(ordem_servico[15]),
                            'quantidade_litros': ordem_servico[16],
                            'valor_fluido_sangria': self.formatar_moeda(ordem_servico[17]),
                            'valor_limpeza_freios': self.formatar_moeda(ordem_servico[19]),
                            'valor_filtro': self.formatar_moeda(ordem_servico[21]),
                            'valor_pneu': self.formatar_moeda(ordem_servico[22]),
                            'valor_bateria': self.formatar_moeda(ordem_servico[23]),
                            'lts_oleo_motor': ordem_servico[25],
                            'valor_lt_oleo': self.formatar_moeda(ordem_servico[24]),
                            'mecanico_servico': ordem_servico[29],
                            'servico_filtro': ordem_servico[30],
                            'valor_p_meta': self.formatar_moeda(ordem_servico[28]),
                            'valor_em_dinheiro': self.formatar_moeda(ordem_servico[31]),
                            'obs': ordem_servico[40]
                        }
                        
                        # Verificando o objeto os antes de adicionar
                    print(f"Ordem de serviço preparada para adicionar: {os}")
                        
                    faturamentos.append(os)
                
            # Verificando o resultado final
            print(f"Faturamentos preparados: {faturamentos}")
            
            return faturamentos
        except Exception as e:
            # Verificando erros
            print(f"Erro ao processar ordens de serviço: {e}")

    def faturamentos_ordens(self, mes, ano):
        try:
            faturamentos = []
            faturamento = self.db.faturamento_ordens(mes, ano)
            for ordem_servico in faturamento:
                data_objeto_orcamento = datetime.strptime(
                    ordem_servico[3], "%Y-%m-%d")
                data_orcamento = data_objeto_orcamento.strftime("%d/%m/%Y")
                data_objeto_faturamento = datetime.strptime(
                    ordem_servico[4], "%Y-%m-%d")
                data_faturamento = data_objeto_faturamento.strftime("%d/%m/%Y")
                os = {
                    'placa': ordem_servico[1],
                    'modelo_veiculo': ordem_servico[2],
                    'data_orcamento': data_orcamento,
                    'data_faturamento': data_faturamento,
                    'dias_servico': ordem_servico[7],
                    'numero_os': ordem_servico[8],
                    'companhia': ordem_servico[9],
                    'valor_pecas': self.formatar_moeda(ordem_servico[11]),
                    'valor_servicos': self.formatar_moeda(ordem_servico[12]),
                    'total_os': self.formatar_moeda(ordem_servico[13]),
                    'valor_revitalizacao': self.formatar_moeda(ordem_servico[14]),
                    'valor_aditivo': self.formatar_moeda(ordem_servico[15]),
                    'quantidade_litros': ordem_servico[16],
                    'valor_fluido_sangria': self.formatar_moeda(ordem_servico[17]),
                    'valor_palheta': self.formatar_moeda(ordem_servico[18]),
                    'valor_limpeza_freios': self.formatar_moeda(ordem_servico[19]),
                    'valor_pastilha_parabrisa': self.formatar_moeda(ordem_servico[20]),
                    'valor_filtro': self.formatar_moeda(ordem_servico[21]),
                    'valor_pneu': self.formatar_moeda(ordem_servico[22]),
                    'valor_bateria': self.formatar_moeda(ordem_servico[23]),
                    'modelo_bateria': ordem_servico[24],
                    'lts_oleo_motor': ordem_servico[25],
                    'valor_lt_oleo': self.formatar_moeda(ordem_servico[26]),
                    'marca_e_tipo_oleo': ordem_servico[27],
                    'mecanico_servico': ordem_servico[29],
                    'servico_filtro': ordem_servico[30],
                    'valor_p_meta': self.formatar_moeda(ordem_servico[28]),
                    'valor_em_dinheiro': self.formatar_moeda(ordem_servico[31]),
                    'valor_servico_freios': self.formatar_moeda(ordem_servico[32]),
                    'valor_servico_suspensao': self.formatar_moeda(ordem_servico[33]),
                    'valor_servico_injecao_ignicao': self.formatar_moeda(ordem_servico[34]),
                    'valor_servico_cabecote_motor_arr': self.formatar_moeda(ordem_servico[35]),
                    'valor_outros_servicos': self.formatar_moeda(ordem_servico[36]),
                    'valor_servicos_oleos': self.formatar_moeda(ordem_servico[37]),
                    'valor_servico_transmissao': self.formatar_moeda(ordem_servico[38]),
                    'obs':ordem_servico[40]
                }
                faturamentos.append(os)
            return faturamentos
        except Exception as e:
            print(f"Erro ao obter faturamentos: {e}")
            return []