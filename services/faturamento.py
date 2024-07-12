from database import conection
import locale
from datetime import datetime

class Faturamento:
    def __init__(self):
        self.db = conection.Database()
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    def cadastrar(self, dados):
        try:
            data = dados['data_faturamento']
            mes = data[5:7]
            ano = data[:4]
            ordem_servico ={
                'placa' : dados['placa'],
                'modelo_veiculo' : dados['modelo_veiculo'],
                'data_orcamento' : dados['data_orcamento'],
                'data_faturamento' : dados['data_faturamento'],
                'mes_faturamento' : mes,
                'ano_faturamento': ano,
                'dias_servico' : int(dados['dias']),
                'numero_os' : int(dados['num_os']),
                'companhia' : dados['cia'],
                'conversao_ps': dados['conversao_pneustore'],
                'valor_pecas' : float(dados['pecas']),
                'valor_servicos' : float(dados['servicos']),
                'total_os' : float(dados['valor_total']),
                'valor_revitalizacao' : float(dados['revitalizacao']),
                'valor_aditivo' : float(dados['aditivo']),
                'quantidade_litros' : int(dados['quantidade_aditivo']),
                'valor_fluido_sangria': float(dados['fluido_sangria']),
                'valor_palheta' : float(dados['palheta']),
                'valor_limpeza_freios': float(dados['limpeza_freios']),
                'valor_pastilha_parabrisa' : float(dados['detergente_parabrisa']),
                'valor_filtro': float(dados['filtro']),
                'valor_pneu': float(dados['pneus']),
                'valor_bateria' : float(dados['bateria']),
                'modelo_bateria': dados['modelo_bateria'],
                'lts_oleo_motor': int(dados['quantidade_oleo']),
                'valor_lt_oleo': float(dados['valor_oleo']),
                'marca_e_tipo_oleo': dados['tipo_marca_oleo'],
                'mecanico_servico': dados['mecanico'],
                'servico_filtro' : dados['filtro_mecanico'],
                'valor_p_meta': float(dados['valor_meta']),
                'valor_em_dinheiro': float(dados['valor_dinheiro']),
                'valor_servico_freios': float(dados['freios']),
                'valor_servico_suspensao': float(dados['suspensao']),
                'valor_servico_injecao_ignicao': float(dados['injecao_ignicao']),
                'valor_servico_cabecote_motor_arr': float(dados['cabeote_motor_arrefecimento']),
                'valor_outros_servicos': float(dados['outros']),
                'valor_servicos_oleos': float(dados['oleos']),
                'valor_servico_transmissao' : float(dados['transmissao'])
            }
            self.db.cadastrar_faturamento(ordem_servico)
            
        except Exception as e:
            print(e)
    
    def faturamento_total_mes(self, mes, ano):
        try:
            dados = self.db.faturamento_mes(mes, ano)
            valores = [dado[0] for dado in dados]

            valor_soma = sum(valores)
            valor_total = locale.currency(valor_soma, grouping=True)
            return valor_total
        except Exception as e:
            print(f"Erro ao calcular faturamento total do mês: {e}")
            raise e

    def faturamento_meta_mes(self, mes, ano):
        try:
            dados = self.db.faturamento_mes_meta(mes, ano)
            valores = [dado[0] for dado in dados]
            valor_soma = sum(valores)
            valor_total = locale.currency(valor_soma, grouping=True)
            return valor_total
        except Exception as e:
            print(f"Erro ao calcular faturamento total da meta do mês: {e}")
            raise e
    def faturamento_mecanico(self, mes, ano):
        try:
            faturamentos = []
            mecanicos = self.db.get_mecanicos()
            for mecanico in mecanicos:
                dados = self.db.faturamento_por_mecanico(mecanico[0], mes, ano)
                valores = [dado[0] for dado in dados]
                valor_soma = sum(valores)
                valor_total = locale.currency(valor_soma, grouping=True)
                dados_filtro = self.db.get_qntd_filtros_mec(mecanico[0], mes, ano)
                qntd_filtro = [qntd[0] for qntd in dados_filtro]
                filtro = len(qntd_filtro)
                dados_revitalizacao = self.db.get_revitalizacao_mecanico(mecanico[0], mes, ano)
                valores_revi = []
    
                for valor in dados_revitalizacao:
                    if valor[0] > 0.00:
                        valores_revi.append(valor[0])
                qnd_revi = len(valores_revi)
                valor_soma_revi = sum(valores_revi)
                valor_total_revi = locale.currency(valor_soma_revi, grouping=True)
                faturamentos.append((mecanico[0], valor_total, len(valores), filtro, qnd_revi, valor_total_revi))
            print(faturamentos)
            return faturamentos
        except Exception as e:
            raise e

    def faturamento_companhia(self, mes, ano):
        try:
            faturamentos = []
            cias = self.db.get_cias()
            for cia in cias:
                dados = self.db.faturamento_cia(cia[0], mes, ano)
                valores = [dado[0] for dado in dados]
                valor_soma = sum(valores)
                valor_total = locale.currency(valor_soma, grouping=True)
                faturamentos.append((cia[0], valor_total, len(valores)))
            return faturamentos
        except Exception as e:
            raise e
    
    def faturamento_servico(self, mes, ano):
        try:
            faturamento = []
            servicos = self.db.buscar_serv()
            for servico in servicos:
                dados = self.db.faturamento_serv(servico[0], mes, ano)
                valores = []
                for valor in dados:
                    if valor[0] > 0.00:
                        valores.append(valor[0])
                valor_soma = sum(valores)
                valor_total = locale.currency(valor_soma, grouping=True)
                faturamento.append((servico[0], valor_total, len(valores)))
            return faturamento   
        except Exception as e:
            raise e
    
    def faturamentos_gerais(self):
        try:
            faturamentos = []
            faturamento = self.db.faturamento_geral()
            for ordem_servico in faturamento:
                data_objeto_orcamento = datetime.strptime(ordem_servico[2], "%Y-%m-%d")
                data_orcamento = data_objeto_orcamento.strftime("%d/%m/%Y")
                data_objeto_faturamento = datetime.strptime(ordem_servico[3], "%Y-%m-%d")
                data_faturamento = data_objeto_faturamento.strftime("%d/%m/%Y") 
                os = {
                        'placa' : ordem_servico[0],
                        'modelo_veiculo' : ordem_servico[1],
                        'data_orcamento' : data_orcamento,
                        'data_faturamento' : data_faturamento,
                        'dias_servico' : ordem_servico[6],
                        'numero_os' : ordem_servico[7],
                        'companhia' : ordem_servico[8],
                        'valor_pecas' : locale.currency(ordem_servico[10], grouping=True),
                        'valor_servicos' : locale.currency(ordem_servico[11], grouping=True),
                        'total_os' : locale.currency(ordem_servico[12], grouping=True),
                        'valor_revitalizacao' : locale.currency(ordem_servico[13], grouping=True),
                        'valor_aditivo' : locale.currency(ordem_servico[14], grouping=True),
                        'quantidade_litros' : ordem_servico[15],
                        'valor_fluido_sangria': locale.currency(ordem_servico[16], grouping=True),
                        'valor_palheta' : locale.currency(ordem_servico[17], grouping=True),
                        'valor_limpeza_freios': locale.currency(ordem_servico[18], grouping=True),
                        'valor_pastilha_parabrisa' : locale.currency(ordem_servico[19], grouping=True),
                        'valor_filtro': locale.currency(ordem_servico[20], grouping=True),
                        'valor_pneu': locale.currency(ordem_servico[21], grouping=True),
                        'valor_bateria' : locale.currency(ordem_servico[22], grouping=True),
                        'modelo_bateria': ordem_servico[23],
                        'lts_oleo_motor': ordem_servico[24],
                        'valor_lt_oleo': locale.currency(ordem_servico[25], grouping=True),
                        'marca_e_tipo_oleo': ordem_servico[26],
                        'mecanico_servico': ordem_servico[29],
                        'servico_filtro' : ordem_servico[30],
                        'valor_p_meta': locale.currency(ordem_servico[27], grouping=True),
                        'valor_em_dinheiro': locale.currency(ordem_servico[30], grouping=True),
                        'valor_servico_freios': locale.currency(ordem_servico[31], grouping=True),
                        'valor_servico_suspensao': locale.currency(ordem_servico[32], grouping=True),
                        'valor_servico_injecao_ignicao': locale.currency(ordem_servico[33], grouping=True),
                        'valor_servico_cabecote_motor_arr': locale.currency(ordem_servico[34], grouping=True),
                        'valor_outros_servicos': locale.currency(ordem_servico[35], grouping=True),
                        'valor_servicos_oleos': locale.currency(ordem_servico[36], grouping=True),
                        'valor_servico_transmissao' : locale.currency(ordem_servico[37], grouping=True)
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
                cias.append(cia[0])
            
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