from database import conection
import json
import pyodbc
from flask import session
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
            def moeda(valor):
                if valor is None or valor == '':
                    return 0.0

                valor = str(valor).strip()
                valor = valor.replace('R$', '').replace(' ', '')

                # Ex: 1.000,50 -> 1000.50
                if ',' in valor:
                    valor = valor.replace('.', '').replace(',', '.')

                return float(valor)

            def inteiro(valor):
                if valor is None or valor == '':
                    return 0

                return int(float(str(valor).replace(',', '.')))

            data = dados.get('data_faturamento', '')
            mes = data[5:7]
            ano = data[:4]

            valor_aditivo = dados.get('aditivo') or dados.get('ar_condicionado') or 0
            quantidade_litros = dados.get('quantidade_aditivo') or 0

            valor_limpeza_freios = dados.get('limpeza_freios') or dados.get('funilaria') or 0

            ordem_servico = {
                'placa': dados.get('placa', ''),
                'modelo_veiculo': dados.get('modelo_veiculo', ''),
                'data_orcamento': dados.get('data_orcamento', ''),
                'data_faturamento': dados.get('data_faturamento', ''),
                'mes_faturamento': mes,
                'ano_faturamento': ano,
                'dias_servico': inteiro(dados.get('dias')),
                'numero_os': inteiro(dados.get('num_os')),
                'companhia': dados.get('cia', ''),
                'conversao_ps': dados.get('conversao_pneustore', ''),

                'valor_pecas': moeda(dados.get('pecas')),
                'valor_servicos': moeda(dados.get('servicos')),
                'total_os': moeda(dados.get('valor_total')),

                'valor_revitalizacao': moeda(dados.get('revitalizacao')),
                'valor_aditivo': moeda(valor_aditivo),
                'quantidade_litros': inteiro(quantidade_litros),
                'valor_fluido_sangria': moeda(dados.get('fluido_sangria')),
                'valor_palheta': moeda(dados.get('palheta')),
                'valor_limpeza_freios': moeda(valor_limpeza_freios),
                'valor_pastilha_parabrisa': moeda(dados.get('detergente_parabrisa')),
                'valor_filtro': moeda(dados.get('filtro')),
                'valor_pneu': moeda(dados.get('pneus')),
                'valor_bateria': moeda(dados.get('bateria')),
                'modelo_bateria': dados.get('modelo_bateria', ''),
                'terceiros': moeda(dados.get('terceiros', '')),
                'lts_oleo_motor': inteiro(dados.get('quantidade_oleo')),
                'valor_lt_oleo': moeda(dados.get('valor_oleo')),
                'marca_e_tipo_oleo': dados.get('tipo_marca_oleo', ''),

                'mecanico_servico': dados.get('mecanico', ''),
                'servico_filtro': dados.get('filtro_mecanico', ''),

                'valor_p_meta': moeda(dados.get('valor_meta')),
                'valor_em_dinheiro': moeda(dados.get('valor_dinheiro')),

                'valor_servico_freios': moeda(dados.get('freios')),
                'valor_servico_suspensao': moeda(dados.get('suspensao')),
                'valor_servico_injecao_ignicao': moeda(dados.get('injecao_ignicao')),
                'valor_servico_cabecote_motor_arr': moeda(dados.get('cabeote_motor_arrefecimento')),
                'valor_outros_servicos': moeda(dados.get('outros')),
                'valor_servicos_oleos': moeda(dados.get('oleos')),
                'valor_servico_transmissao': moeda(dados.get('transmissao')),

                'usuario': usuario,
                'obs': dados.get('obs', '')
            }

            buscar_os = self.db.buscar_os_by_number(ordem_servico['numero_os'])

            if buscar_os:
                return True
            else:
                self.db.cadastrar_faturamento(ordem_servico)
                return False

        except Exception as e:
            print(f"Erro ao cadastrar faturamento: {e}")
            return None

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
            empresa = session['empresa']
            mecanicos = self.db.get_mecanicos(empresa)
            
            for mecanico in mecanicos:
                
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

    def faturamento_diario_mes(self, mes, ano):
        try:
            query = """
                SELECT
                    DAY(data_faturamento) AS dia,
                    SUM(total_os) AS bruto,
                    SUM(valor_meta) AS liquido
                FROM faturamento
                WHERE MONTH(data_faturamento) = ?
                AND YEAR(data_faturamento) = ?
                GROUP BY DAY(data_faturamento)
                ORDER BY DAY(data_faturamento)
            """

            self.cursor.execute(query, (int(mes), int(ano)))
            return self.cursor.fetchall()

        except Exception as e:
            print(e)
            return []
    
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

    def companhias(self):
        try:
            cias = []
            dados = self.db.get_cias()
            for cia in dados:
                cias.append(cia[1])

            return cias

        except Exception as e:
            print(e)

    def funcionarios(self, empresa):
        try:
            mecanicos = []
            dados = self.db.get_mecanicos(empresa)
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
            empresa = session['empresa']
            mecanicos = self.db.get_mecanicos(empresa)  # Obtém a lista de mecânicos
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
            empresa = session['empresa']
            mecanicos = self.db.get_mecanicos(empresa)  # Obtém a lista de mecânicos
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
           
            
            dados = self.db.detalhes_filtros(mes, ano, mecanico)
            
            # Verificando os dados obtidos de detalhes_filtros
            
            
            faturamentos = []
            
            for ordem_servico in dados:
                # Verificando os dados de cada ordem de serviço
                
                
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
                

                    
                faturamentos.append(os)
            
            # Verificando o resultado final
            
            
            return faturamentos
        except Exception as e:
            # Verificando erros
            print(f"Erro ao processar ordens de serviço: {e}")

    def ordens_revitalizacao(self, mes, ano, mecanico):
        try:
            # Adicionando print para verificar os parâmetros recebidos
            
            
            dados = self.db.detalhes_revitalizacao(mes, ano, mecanico)
            
            # Verificando os dados obtidos de detalhes_filtros
            
            
            faturamentos = []
            
            for ordem_servico in dados:
                if ordem_servico[14] > 0:
                    # Verificando os dados de cada ordem de serviço
                    
                    
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
                   
                        
                    faturamentos.append(os)
                
            # Verificando o resultado final
            
            
            return faturamentos
        except Exception as e:
            # Verificando erros
            print(f"Erro ao processar ordens de serviço: {e}")
    
    def ordens_dinheiro_relat(self, mes, ano):
        try:
            # Adicionando print para verificar os parâmetros recebidos
            
            
            dados = self.db.ordens(mes, ano)
            
            # Verificando os dados obtidos de detalhes_filtros
            
            
            faturamentos = []
            
            for ordem_servico in dados:
                if ordem_servico[31] > 0:
                    # Verificando os dados de cada ordem de serviço
                    
                    
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
                   
                        
                    faturamentos.append(os)
                
            # Verificando o resultado final
            
            
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
    