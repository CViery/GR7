import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()
    

    def cadastrar_faturamento(self, dados):
        try:
            query = 'INSERT INTO faturamento VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
            self.cursor.execute(query, (dados['placa'], dados['modelo_veiculo'], dados['data_orcamento'], dados['data_faturamento'], dados['mes_faturamento'], dados['ano_faturamento'], dados['dias_servico'], dados['numero_os'], dados['companhia'],dados['conversao_ps'],dados['valor_pecas'], dados['valor_servicos'], dados['total_os'], dados['valor_revitalizacao'], dados['valor_aditivo'],dados['quantidade_litros'], dados['valor_fluido_sangria'], dados['valor_palheta'], dados['valor_limpeza_freios'], dados['valor_pastilha_parabrisa'],dados['valor_filtro'],dados['valor_pneu'], dados['valor_bateria'], dados['modelo_bateria'], dados['lts_oleo_motor'],dados['valor_lt_oleo'], dados['marca_e_tipo_oleo'], dados['mecanico_servico'], dados['servico_filtro'], dados['valor_p_meta'], dados['valor_em_dinheiro'], dados['valor_servico_freios'], dados['valor_servico_suspensao'], dados['valor_servico_injecao_ignicao'], dados['valor_servico_cabecote_motor_arr'], dados['valor_outros_servicos'],dados['valor_servicos_oleos'], dados['valor_servico_transmissao']))
            self.conn.commit()
        except Exception as e:
            print(e)
    def faturamento_mes(self, mes, ano):
        try:
            query = 'SELECT valor_os FROM faturamento WHERE mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)
    def faturamento_mes_meta(self, mes, ano):
        try:
            query = 'SELECT valor_meta FROM faturamento WHERE mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)
    
    def get_qntd_filtros_mec(self, mecanico, mes,ano):
        try:
            query = 'SELECT filtro_mecanico FROM faturamento WHERE filtro_mecanico = ? AND mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query,(mecanico,mes, ano))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)
            raise e

    def faturamento_por_mecanico(self, mecanico, mes, ano):
        try:
            print(f'Mecânico: {mecanico}')
            print(f'Mês: {mes}, Tipo: {type(mes)}')
            print(f'Ano: {ano}')

            query = '''
            SELECT servicos 
            FROM faturamento 
            WHERE mecanico = ? AND mes_faturamento = ? AND ano_faturamento = ?
            '''
            self.cursor.execute(query, (mecanico, mes, ano))
            result = self.cursor.fetchall()
            return result

        except Exception as e:
            print(f'Erro ao buscar faturamento por mecânico: {str(e)}')
            raise
    def get_mecanicos(self):
        try:
            query = 'SELECT nome FROM funcionarios '
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(f'Erro ao buscar mecânico: {str(e)}')
            raise
    
    def get_revitalizacao_mecanico(self,mecanico, mes, ano):
        try:
            query = 'SELECT revitalizacao FROM faturamento WHERE mecanico = ? AND mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mecanico, mes, ano))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            print(e)
    def get_cias(self):
        try:
            query = 'SELECT * FROM companhias'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            raise e
    
    def faturamento_cia(self, cia, mes, ano):
        try:
            query = 'SELECT valor_os FROM faturamento WHERE cia = ? AND mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (cia, mes, ano))
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            raise e

    def faturamento_serv(self, serv, mes, ano):
        try:
            query = f'SELECT {serv} FROM faturamento WHERE mes_faturamento = ? AND ano_faturamento = ?'
            self.cursor.execute(query, (mes, ano))
            result = self.cursor.fetchall()
            print(result)
            return result
        except Exception as e:
            print(e) 

    def buscar_serv(self):
        try:
            query = 'SELECT * FROM servicos'
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            print(result)
            return result
        except Exception as e:
            raise e  
class DatabaseGastos:
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()
    

    def set_boleto(self, boleto):
        pass

    def set_notas(self, nota):
        pass
    def verGastos(self):
        pass

    def gastos_por_tipo(self,tipo, mes, ano):
        try:
            pass
        except Exception as e:
            pass



