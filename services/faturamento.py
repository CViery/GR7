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
                'dias_servico' : dados['dias'],
                'numero_os' : dados['num_os'],
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
                qntd_filtro = [qntd[0] for filtro in dados_filtro]
                filtro = len(qntd_filtro)
                dados_revitalizacao = self.db.get_revitalizacao_mecanico(mecanico[0], mes, ano)
                valores_revi = []
                for valor in dados_revitalizacao:
                    if valor[0] > 0.00:
                        valores_revi.append(valor[0])
                qnd_revi = len(valores_revi)
                valor_soma_revi = sum(valores_revi)
                valor_total_revi = locale.currency(valor_soma_revi, grouping=True)
                faturamentos.append((mecanico[0], valor_total, filtro, qnd_revi, valor_total_revi))
            return faturamentos
        except Exception as e:
            raise e



app = Faturamento()

app.faturamento_mecanico( '06', '2024')