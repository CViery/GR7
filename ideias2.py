utils = utills.Utills()
                db = faturamento.Faturamento()
                now = datetime.now()
                mes_dados = now.strftime('%m')
                ano_dados = now.strftime('%Y')
                valor_faturamento_total = db.faturamento_total_mes(mes_dados, ano_dados)
                valor_faturamento_meta = db.faturamento_meta_mes(mes_dados, ano_dados)
                valor_faturamento_pecas = utils.faturamento_pecas(mes_dados, ano_dados)
                valor_faturamento_servico = utils.faturamento_servicos(mes_dados,ano_dados)
                valor_primeira_meta = utils.primeira_meta(mes_dados, ano_dados)
                valor_segunda_meta = utils.segunda_meta(mes_dados, ano_dados)
                valor_gastos = utils.gastos(mes_dados, ano_dados)
                porcentagem_faturamento = utils.porcentagem_faturamento(mes_dados, ano_dados)
                gastos_pecas = utils.gastos_pecas(mes_dados, ano_dados)
                porcentagem_pecas = utils.porcentagem_gastos_pecas(mes_dados, ano_dados)