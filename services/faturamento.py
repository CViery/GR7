from database import conection

from datetime import datetime

class Faturamento:
    def __init__(self):
        self.db = conection.Database()
        

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
            valor_total = f'R$ {valor_soma:,.2f}'
            return valor_total
        except Exception as e:
            print(f"Erro ao calcular faturamento total do mês: {e}")
            raise e

    def faturamento_meta_mes(self, mes, ano):
        try:
            dados = self.db.faturamento_mes_meta(mes, ano)
            valores = [dado[0] for dado in dados]
            valor_soma = sum(valores)
            valor_total = f'R$ {valor_soma:,.2f}'
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
                valor_total = f'R$ {valor_soma:,.2f}'
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
                valor_total_revi = f'R$ {valor_soma_revi:,.2f}'
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
                valor_total = f'R$ {valor_soma:,.2f}'
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
                valor_total = f'R$ {valor_soma:,.2f}'
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
                        'valor_pecas' : f'R$ {ordem_servico[10]:,.2f}',
                        'valor_servicos' : f"R$ {ordem_servico[11]:,.2f}",
                        'total_os' : f'R$ {ordem_servico[12]:,.2f}',
                        'valor_revitalizacao' : f'R$ {ordem_servico[13]:,.2f}',
                        'valor_aditivo' : f'R$ {ordem_servico[14]:,.2f}',
                        'quantidade_litros' : ordem_servico[15],
                        'valor_fluido_sangria': f'R$ {ordem_servico[16]:,.2f}',
                        'valor_palheta' : f'R$ {ordem_servico[17]:,.2f}',
                        'valor_limpeza_freios':f'R$ {ordem_servico[18]:,.2f}',
                        'valor_pastilha_parabrisa' :f'R$ {ordem_servico[19]:,.2f}',
                        'valor_filtro': f'R$ {ordem_servico[20]:,.2f}',
                        'valor_pneu': f'R$ {ordem_servico[21]:,.2f}',
                        'valor_bateria' : f'R$ {ordem_servico[22]:,.2f}',
                        'modelo_bateria': ordem_servico[23],
                        'lts_oleo_motor': ordem_servico[24],
                        'valor_lt_oleo': f'R$ {ordem_servico[25]:,.2f}',
                        'marca_e_tipo_oleo': ordem_servico[26],
                        'mecanico_servico': ordem_servico[29],
                        'servico_filtro' : ordem_servico[30],
                        'valor_p_meta': f'R$ {ordem_servico[27]:,.2f}',
                        'valor_em_dinheiro': f'R$ {ordem_servico[30]:,.2f}',
                        'valor_servico_freios': f'R$ {ordem_servico[31]:,.2f}',
                        'valor_servico_suspensao': f'R$ {ordem_servico[32]:,.2f}',
                        'valor_servico_injecao_ignicao': f'R$ {ordem_servico[33]:,.2f}',
                        'valor_servico_cabecote_motor_arr': f'R$ {ordem_servico[34]:,.2f}',
                        'valor_outros_servicos': f'R$ {ordem_servico[35]:,.2f}',
                        'valor_servicos_oleos': f'R$ {ordem_servico[36]:,.2f}',
                        'valor_servico_transmissao' : f'R$ {ordem_servico[37]:,.2f}'
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