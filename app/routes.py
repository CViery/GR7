from app import app
from flask import request, redirect, render_template, flash, session, jsonify
from services import login, cadastrar_notas, cadastrar_duplicata, dados_notas, faturamento, utills
from datetime import datetime
from flask_paginate import Pagination, get_page_parameter
from database import gastos_db


class Routes:
    def __init__(self):
        pass

    @app.route('/')
    def show_login():
        return render_template('login.html')

    @app.route('/autenticar', methods=['POST'])
    def autenticar():
        try:
            usuario = request.form['usuario']
            senha = request.form['senha']
            empresa = request.form['empresa']
            db = login.Login()
            auten = db.login(usuario.upper(), senha)
            if auten == 'ADMIN':
                session['usuario'] = usuario
                session['empresa'] = empresa
                if empresa == 'gr7':
                    if session['permission_empresa'] == 0 or session['permission_empresa'] == 1:
                        return redirect('/home')
                    else:
                        flash('Desculpe seu acesso não permite acessar.')
                        return redirect('/')
                elif empresa == 'portal':
                    if session['permission_empresa'] == 0 or session['permission_empresa'] == 2:
                        return redirect('/home')
                    else:
                        flash('Desculpe empresa invalida.')
                        return redirect('/')
            elif auten == 'NORMAL':
                session['usuario'] = usuario
                session['empresa'] = empresa
                if empresa == 'gr7':
                    if session['permission_empresa'] == 0 or session['permission_empresa'] == 1:
                        return redirect('/home')
                    else:
                        flash('Desculpe empresa invalida.')
                        return redirect('/')
                elif empresa == 'portal':
                    if session['permission_empresa'] == 0 or session['permission_empresa'] == 2:
                        return redirect('/home')
                    else:
                        flash('Desculpe empresa invalida.')
                        return redirect('/')
                return 'Usuario Normal'
            else:
                flash('Usuário ou senha incorretos.')
                return redirect('/')
        except Exception as e:
            print(f"Erro durante autenticação: {e}")
            flash(f'Ocorreu um erro. Tente novamente.{e}')
            return redirect('/')

    @app.route('/logout')
    def logout():
        session.pop('usuario', None)
        session.pop('empresa', None)
        flash('Você saiu da sessão com sucesso.')
        return redirect('/')

    @app.route('/home')
    def home():
        if 'usuario' in session and session['empresa'] == 'gr7':
            if session['permission'] == 'ADMIN':
                empresa = session['empresa']
                usuario = session['usuario']
                utils = utills.Utills()
                db = faturamento.Faturamento()

                now = datetime.now()
                mes_dados = now.strftime('%m')
                ano_dados = now.strftime('%Y')
                valor_faturamento_total = db.faturamento_total_mes(
                    mes_dados, ano_dados)
                valor_faturamento_meta = db.faturamento_meta_mes(
                    mes_dados, ano_dados)
                valor_faturamento_pecas = utils.faturamento_pecas(
                    mes_dados, ano_dados)
                valor_faturamento_servico = utils.faturamento_servicos(
                    mes_dados, ano_dados)
                valor_primeira_meta = utils.primeira_meta(mes_dados, ano_dados)
                valor_segunda_meta = utils.segunda_meta(mes_dados, ano_dados)
                valor_gastos = utils.gastos(mes_dados, ano_dados)
                porcentagem_faturamento = utils.porcentagem_faturamento(
                    mes_dados, ano_dados)
                gastos_pecas = utils.gastos_pecas(mes_dados, ano_dados)
                porcentagem_pecas = utils.porcentagem_gastos_pecas(
                    mes_dados, ano_dados)
                return render_template('index.html', empresa=empresa, user=usuario, faturamento=valor_faturamento_total, faturamento_meta=valor_faturamento_meta, faturamento_pecas=valor_faturamento_pecas, faturamento_servicos=valor_faturamento_servico, primeira_meta=valor_primeira_meta, segunda_meta=valor_segunda_meta, valor_gastos=valor_gastos, porcentagem_faturamento=porcentagem_faturamento, gastos_pecas=gastos_pecas, porcentagem_pecas=porcentagem_pecas)
            else:
                flash('Você não tem permissão para acessar essa pagina')
                return redirect('/')
        elif 'usuario' in session and session['empresa'] == 'portal':
            if session['permission'] == 'ADMIN':
                # mudar dados para receber os dados da portal
                empresa = session['empresa']
                usuario = session['usuario']
                utils = utills.Utills_portal()
                db = faturamento.FaturamentoPortal()
                now = datetime.now()
                mes_dados = now.strftime('%m')
                ano_dados = now.strftime('%Y')
                valor_faturamento_total = db.faturamento_total_mes(
                    mes_dados, ano_dados)
                valor_faturamento_meta = db.faturamento_meta_mes(
                    mes_dados, ano_dados)
                valor_faturamento_pecas = utils.faturamento_pecas(
                    mes_dados, ano_dados)
                valor_faturamento_servico = utils.faturamento_servicos(
                    mes_dados, ano_dados)
                valor_primeira_meta = utils.primeira_meta(mes_dados, ano_dados)
                valor_segunda_meta = utils.segunda_meta(mes_dados, ano_dados)
                valor_gastos = utils.gastos(mes_dados, ano_dados)
                porcentagem_faturamento = utils.porcentagem_faturamento(
                    mes_dados, ano_dados)
                gastos_pecas = utils.gastos_pecas(mes_dados, ano_dados)
                porcentagem_pecas = utils.porcentagem_gastos_pecas(
                    mes_dados, ano_dados)
                return render_template('index_portal_admin.html', empresa=empresa, user=usuario, faturamento=valor_faturamento_total, faturamento_meta=valor_faturamento_meta, faturamento_pecas=valor_faturamento_pecas, faturamento_servicos=valor_faturamento_servico, primeira_meta=valor_primeira_meta, segunda_meta=valor_segunda_meta, valor_gastos=valor_gastos, porcentagem_faturamento=porcentagem_faturamento, gastos_pecas=gastos_pecas, porcentagem_pecas=porcentagem_pecas)
            elif session['permission'] == 'NORMAL':
                empresa = session['empresa']
                usuario = session['usuario']
                utils = utills.Utills_portal()
                db = faturamento.FaturamentoPortal()
                now = datetime.now()
                mes_dados = now.strftime('%m')
                ano_dados = now.strftime('%Y')
                valor_faturamento_total = db.faturamento_total_mes(
                    mes_dados, ano_dados)
                valor_faturamento_meta = db.faturamento_meta_mes(
                    mes_dados, ano_dados)
                # valor_faturamento_pecas = utils.faturamento_pecas(mes_dados, ano_dados)
                # valor_faturamento_servico = utils.faturamento_servicos(mes_dados,ano_dados)
                valor_primeira_meta = utils.primeira_meta(mes_dados, ano_dados)
                valor_segunda_meta = utils.segunda_meta(mes_dados, ano_dados)
                # valor_gastos = utils.gastos(mes_dados, ano_dados)
                # porcentagem_faturamento = utils.porcentagem_faturamento(mes_dados, ano_dados)
                # gastos_pecas = utils.gastos_pecas(mes_dados, ano_dados)
                # porcentagem_pecas = utils.porcentagem_gastos_pecas(mes_dados, ano_dados)
                return render_template('index_portal_normal.html', empresa=empresa, user=usuario, faturamento=valor_faturamento_total, faturamento_meta=valor_faturamento_meta,  primeira_meta=valor_primeira_meta, segunda_meta=valor_segunda_meta)
        else:
            flash('usario não está logado')
            return redirect('/')

    @app.route('/gastos/cadastros/notas')
    def tela_cadastro_notas():
        if 'usuario' in session:
            db_portal = utills.Utills_portal()
            db = utills.Utills()
            if session['empresa'] == 'gr7':
                fornecedores = db.fornecedores()
                despesas = db.despesas()
                empresa = session['empresa']
                emitido_para = db.emitido_para()
                return render_template('cadastrar_notas.html', empresa=empresa, fornecedores=fornecedores, despesas=despesas, emitido_para=emitido_para)
            elif session['empresa'] == 'portal':
                fornecedores = db_portal.fornecedores()
                despesas = db_portal.despesas()
                empresa = session['empresa']
                emitido_para = db_portal.emitido_para()
                return render_template('cadastrar_notas.html', empresa=empresa, fornecedores=fornecedores, despesas=despesas, emitido_para=emitido_para)
        else:
            flash('usario não está logado')
            return redirect('/')

    @app.route('/gastos/cadastros/notas-cadastrar-nota', methods=['POST'])
    def cadastrar_nota():
        if session['empresa'] == 'gr7':
            enviar = cadastrar_notas.Notas()
            dados = {
                'empresa': session['empresa'],
                'emitido_para': request.form['emitido-para'],
                'status': request.form['status'],
                'boleto': request.form['boleto'],
                'nota': request.form['nota'],
                'duplicata': request.form['duplicata'],
                'fornecedor': request.form['fornecedor'],
                'emissao': request.form['emissao'],
                'valor': request.form['valor'],
                'despesa': request.form['despesa']
            }
            enviar.cadastrar(dados)
            if dados['boleto'] == 'Sim':
                return render_template('cadastrar_boleto.html', empresa=session['empresa'], num_nota=dados['nota'], fornecedor=dados['fornecedor'])
        elif session['empresa'] == 'portal':
            # alterar dados para banco portal
            enviar = cadastrar_notas.NotasPortal()
            dados = {
                'empresa': session['empresa'],
                'emitido_para': request.form['emitido-para'],
                'status': request.form['status'],
                'boleto': request.form['boleto'],
                'nota': request.form['nota'],
                'duplicata': request.form['duplicata'],
                'fornecedor': request.form['fornecedor'],
                'emissao': request.form['emissao'],
                'valor': request.form['valor'],
                'despesa': request.form['despesa']
            }
            enviar.cadastrar(dados)
            if dados['boleto'] == 'Sim':
                return render_template('cadastrar_boleto.html', empresa=session['empresa'], num_nota=dados['nota'], fornecedor=dados['fornecedor'])
        else:
            flash('Nota cadastrada')
            return redirect('/gastos/cadastros/notas')

    @app.route('/gastos/cadatro/duplicata')
    def duplicata():
        if 'usuario' in session:
            if session['empresa'] == 'gr7':
                empresa = session['empresa']
                return render_template('cadastrar_duplicatas.html', empresa=empresa)
            elif session['empresa'] == 'portal':
                empresa = session['empresa']
                return render_template('cadastrar_duplicatas.html', empresa=empresa)
        else:
            print('usario não está logado')
            return redirect('/')

    @app.route('/cadastrar_boletos', methods=['POST'])
    def cadastrar_boletos():
        if session['empresa'] == 'gr7':
            try:
                numero_nota = request.form['num_nota']
                fornecedor = request.form['fornecedor']
                num_parcelas = int(request.form['numParcelas'])
                parcelas = []
                for i in range(1, num_parcelas + 1):
                    valor = request.form[f'valorParcela{i}']
                    data_vencimento = request.form[f'dataVencimento{i}']
                    parcelas.append(
                        {'valor': valor, 'data_vencimento': data_vencimento})

                for parcela in parcelas:
                    boleto = {
                        'num_nota': numero_nota,
                        'notas': '',
                        'fornecedor': fornecedor,
                        'vencimento': parcela['data_vencimento'],
                        'valor': parcela['valor']
                    }
                    db = cadastrar_notas.Boletos()
                    db.cadastrar(boleto)

                    flash('Boleto Cadastrado')
                    return redirect('/gastos/cadastros/notas')
            except Exception as e:
                print(f'Erro: {e}')
                return "Erro no processamento dos dados", 400
        elif session['empresa'] == 'portal':
            try:
                # mudar dadops para banco portal
                numero_nota = request.form['num_nota']
                fornecedor = request.form['fornecedor']
                num_parcelas = int(request.form['numParcelas'])
                parcelas = []
                for i in range(1, num_parcelas + 1):
                    valor = request.form[f'valorParcela{i}']
                    data_vencimento = request.form[f'dataVencimento{i}']
                    parcelas.append(
                        {'valor': valor, 'data_vencimento': data_vencimento})

                for parcela in parcelas:
                    boleto = {
                        'num_nota': numero_nota,
                        'notas': '',
                        'fornecedor': fornecedor,
                        'vencimento': parcela['data_vencimento'],
                        'valor': parcela['valor']
                    }
                    db = cadastrar_notas.BoletosPortal()
                    db.cadastrar(boleto)

                    flash('Boleto Cadastrado')
                    return redirect('/gastos/cadastros/notas')
            except Exception as e:
                print(f'Erro: {e}')
                return "Erro no processamento dos dados", 400

    @app.route('/api/nota/<numero_nota>', methods=['GET'])
    def get_nota(numero_nota):
        if session['empresa'] == 'gr7':
            db = dados_notas.DadosGastos()
            nota = db.nota_por_numero(numero_nota)
            if nota:
                return jsonify(nota)
            else:
                return jsonify({'error': 'Nota não encontrada'}), 404
        elif session['empresa'] == 'portal':
            db = dados_notas.DadosGastosPortal()
            nota = db.nota_por_numero(numero_nota)
            if nota:
                return jsonify(nota)
            else:
                return jsonify({'error': 'Nota não encontrada'}), 404

    @app.route('/cadastrar_duplicata', methods=['POST'])
    def cadastrar_duplicata():
        if session['empresa'] == 'gr7':
            numero_duplicata = request.form['numeroDuplicata']
            notas_cadastradas = []
            parcelas_cadastradas = []

            numero_notas = request.form.getlist('numeroNota[]')
            fornecedor_notas = request.form.getlist('fornecedorNota[]')
            data_emissao_notas = request.form.getlist('dataEmissaoNota[]')
            valor_notas = request.form.getlist('valorNota[]')

            for i in range(len(numero_notas)):
                nota = {
                    'numero': numero_notas[i],
                    'fornecedor': fornecedor_notas[i],
                    'data_emissao': data_emissao_notas[i],
                    'valor': valor_notas[i]
                }
                notas_cadastradas.append(nota)

            quantidade_parcelas = int(request.form['quantidadeParcelas'])

            for i in range(1, quantidade_parcelas + 1):
                parcela = {
                    'valor': request.form[f'valorParcela{i}'],
                    'vencimento': request.form[f'vencimentoParcela{i}']
                }
                parcelas_cadastradas.append(parcela)

            duplicata = {
                'numero_duplicata': numero_duplicata,
                'notas': notas_cadastradas,
                'parcelas': parcelas_cadastradas
            }
            db = cadastrar_duplicata.Boletos()
            db.cadastrar_duplicatas(duplicata)

            # Aqui você pode salvar a duplicata no banco de dados
            # Colocar para retornar na tela de cadastos

            return render_template('respota_cadastro.html', rota='/gastos/cadastros/duplicatas')
        elif session['empresa'] == 'portal':
            # alterar banco
            numero_duplicata = request.form['numeroDuplicata']
            notas_cadastradas = []
            parcelas_cadastradas = []

            numero_notas = request.form.getlist('numeroNota[]')
            fornecedor_notas = request.form.getlist('fornecedorNota[]')
            data_emissao_notas = request.form.getlist('dataEmissaoNota[]')
            valor_notas = request.form.getlist('valorNota[]')

            for i in range(len(numero_notas)):
                nota = {
                    'numero': numero_notas[i],
                    'fornecedor': fornecedor_notas[i],
                    'data_emissao': data_emissao_notas[i],
                    'valor': valor_notas[i]
                }
                notas_cadastradas.append(nota)

            quantidade_parcelas = int(request.form['quantidadeParcelas'])

            for i in range(1, quantidade_parcelas + 1):
                parcela = {
                    'valor': request.form[f'valorParcela{i}'],
                    'vencimento': request.form[f'vencimentoParcela{i}']
                }
                parcelas_cadastradas.append(parcela)

            duplicata = {
                'numero_duplicata': numero_duplicata,
                'notas': notas_cadastradas,
                'parcelas': parcelas_cadastradas
            }
            db = cadastrar_duplicata.BoletosPortal()
            db.cadastrar_duplicatas()

            # Aqui você pode salvar a duplicata no banco de dados
            # ...

            return render_template('respota_cadastro.html', rota='/gastos/cadastros/duplicatas')

    @app.route('/gastos/cadastros/duplicatas')
    def tela_duplicatas():
        if 'usuario' in session:
            empresa = session['empresa']
            return render_template('cadastrar_duplicatas.html', empresa=empresa)
        else:
            print('usario não está logado')
            return redirect('/')

    @app.route('/gastos', methods=['GET', 'POST'])
    def tela_gastos():
        if 'usuario' in session:
            if session['empresa'] == 'gr7':
                empresa = session['empresa']
                db = dados_notas.DadosGastos()
                meses = [
                    ('01', 'Janeiro'),
                    ('02', 'Fevereiro'),
                    ('03', 'Março'),
                    ('04', 'Abril'),
                    ('05', 'Maio'),
                    ('06', 'Junho'),
                    ('07', 'Julho'),
                    ('08', 'Agosto'),
                    ('09', 'Setembro'),
                    ('10', 'Outubro'),
                    ('11', 'Novembro'),
                    ('12', 'Dezembro')
                ]
                anos = ['2024', '2025', '2026', '2027', '2028', '2029', '2030']

                if request.method == 'POST':
                    if 'mes' in request.form and 'ano' in request.form:
                        # Processar formulário de filtro de despesas
                        mes_dados = request.form['mes']
                        print(mes_dados)
                        ano_dados = request.form['ano']
                        print(ano_dados)
                        dados_tipos = db.despesas(mes_dados, ano_dados)
                        valor_gasto = db.valor_gastos(mes_dados, ano_dados)

                    else:
                        # Usar data atual se não houver filtros específicos para despesas
                        now = datetime.now()
                        mes_dados = now.strftime('%m')
                        print(mes_dados)
                        ano_dados = now.strftime('%Y')
                        dados_tipos = db.despesas(mes_dados, ano_dados)
                        valor_gasto = db.valor_gastos(mes_dados, ano_dados)
                        print(valor_gasto)

                    if 'dia' in request.form:
                        # Processar formulário de filtro de boletos
                        data = request.form['dia']
                        dia = data[8:]
                        mes = data[5:7]
                        ano = data[:4]
                        boletos = db.boletos_do_dia(dia, mes, ano)
                        valor_a_pagar = db.valor_a_pagar(dia, mes, ano)
                    else:
                        # Usar data atual se não houver filtro específico para boletos
                        now = datetime.now()
                        dia = now.strftime('%d')
                        mes = now.strftime('%m')
                        ano = now.strftime('%Y')
                        boletos = db.boletos_do_dia(dia, mes, ano)
                        valor_a_pagar = db.valor_a_pagar(dia, mes, ano)

                    return render_template('gastos.html', anos=anos, meses=meses, tipo_despesa=dados_tipos, empresa=empresa, boletos=boletos, valor_gastos=valor_gasto, valor_a_pagar=valor_a_pagar)
                else:
                    # Caso seja uma requisição GET, usar a data atual
                    now = datetime.now()
                    dia = now.strftime('%d')
                    mes = now.strftime('%m')
                    ano = now.strftime('%Y')
                    dados_tipos = db.despesas(mes, ano)
                    boletos = db.boletos_do_dia(dia, mes, ano)
                    valor_gasto = db.valor_gastos(mes, ano)
                    valor_a_pagar = db.valor_a_pagar(dia, mes, ano)
                    return render_template('gastos.html', anos=anos, meses=meses, tipo_despesa=dados_tipos, empresa=empresa, boletos=boletos, valor_gastos=valor_gasto, valor_a_pagar=valor_a_pagar)
            if session['empresa'] == 'portal':
                if session['permission'] == 'ADMIN':
                    empresa = session['empresa']
                    db = dados_notas.DadosGastosPortal()
                    meses = [
                        ('01', 'Janeiro'),
                        ('02', 'Fevereiro'),
                        ('03', 'Março'),
                        ('04', 'Abril'),
                        ('05', 'Maio'),
                        ('06', 'Junho'),
                        ('07', 'Julho'),
                        ('08', 'Agosto'),
                        ('09', 'Setembro'),
                        ('10', 'Outubro'),
                        ('11', 'Novembro'),
                        ('12', 'Dezembro')
                    ]
                    anos = ['2024', '2025', '2026',
                            '2027', '2028', '2029', '2030']

                    if request.method == 'POST':
                        if 'mes' in request.form and 'ano' in request.form:
                            # Processar formulário de filtro de despesas
                            mes_dados = request.form['mes']
                            print(mes_dados)
                            ano_dados = request.form['ano']
                            print(ano_dados)
                            dados_tipos = db.despesas(mes_dados, ano_dados)
                            valor_gasto = db.valor_gastos(mes_dados, ano_dados)

                        else:
                            # Usar data atual se não houver filtros específicos para despesas
                            now = datetime.now()
                            mes_dados = now.strftime('%m')
                            print(mes_dados)
                            ano_dados = now.strftime('%Y')
                            dados_tipos = db.despesas(mes_dados, ano_dados)
                            valor_gasto = db.valor_gastos(mes_dados, ano_dados)
                            print(valor_gasto)

                        if 'dia' in request.form:
                            # Processar formulário de filtro de boletos
                            data = request.form['dia']
                            dia = data[8:]
                            mes = data[5:7]
                            ano = data[:4]
                            boletos = db.boletos_do_dia(dia, mes, ano)
                            valor_a_pagar = db.valor_a_pagar(dia, mes, ano)
                        else:
                            # Usar data atual se não houver filtro específico para boletos
                            now = datetime.now()
                            dia = now.strftime('%d')
                            mes = now.strftime('%m')
                            ano = now.strftime('%Y')
                            boletos = db.boletos_do_dia(dia, mes, ano)
                            valor_a_pagar = db.valor_a_pagar(dia, mes, ano)

                        return render_template('gastos.html', anos=anos, meses=meses, tipo_despesa=dados_tipos, empresa=empresa, boletos=boletos, valor_gastos=valor_gasto, valor_a_pagar=valor_a_pagar)
                    else:
                        # Caso seja uma requisição GET, usar a data atual
                        now = datetime.now()
                        dia = now.strftime('%d')
                        mes = now.strftime('%m')
                        ano = now.strftime('%Y')
                        dados_tipos = db.despesas(mes, ano)
                        boletos = db.boletos_do_dia(dia, mes, ano)
                        valor_gasto = db.valor_gastos(mes, ano)
                        valor_a_pagar = db.valor_a_pagar(dia, mes, ano)
                        return render_template('gastos.html', anos=anos, meses=meses, tipo_despesa=dados_tipos, empresa=empresa, boletos=boletos, valor_gastos=valor_gasto, valor_a_pagar=valor_a_pagar)
                elif session['permission'] == 'NORMAL':
                    empresa = session['empresa']
                    return render_template('resposta_permissao.html', empresa=empresa)
        else:
            print('Usuário não está logado')
            return redirect('/')

    @app.route('/atualizar', methods=['POST'])
    def atualizar_boletos():
        if session['empresa'] == 'gr7':
            if request.method == 'POST':
                dia = request.form['dia']
                # Use a data atual se o campo dia não estiver definido
                if not dia:
                    now = datetime.now()
                    dia = now.strftime('%d')
                mes = request.form['mes']
                ano = request.form['ano']

                # Use a lógica adequada para obter os boletos com base nos parâmetros fornecidos
                db = dados_notas.DadosGastos()
                boletos = db.boletos_do_dia(dia, mes, ano)
                return jsonify({'boletos': boletos})
            else:
                return 'Método não permitido'
        elif session['empresa'] == 'portal':
            if request.method == 'POST':
                dia = request.form['dia']
                # Use a data atual se o campo dia não estiver definido
                if not dia:
                    now = datetime.now()
                    dia = now.strftime('%d')
                mes = request.form['mes']
                ano = request.form['ano']

                # Use a lógica adequada para obter os boletos com base nos parâmetros fornecidos
                db = dados_notas.DadosGastosPortal()
                boletos = db.boletos_do_dia(dia, mes, ano)
                return jsonify({'boletos': boletos})
            else:
                return 'Método não permitido'

    @app.route('/cadastros')
    def tela_cadastro():
        if 'usuario' in session:
            empresa = session['empresa']
            return render_template('cadastros.html', empresa=empresa)
        else:
            print('usario não está logado')
            return redirect('/')

    @app.route('/cadastros/fornecedor')
    def tela_cadastro_fornecedor():
        if 'usuario' in session:
            empresa = session['empresa']
            return render_template('cadastro_fornecedor.html', empresa=empresa)
        else:
            print('usario não está logado')
            return redirect('/')

    @app.route('/fornecedor_cadastrar', methods=['GET', 'POST'])
    def cadastrar_fornecedor():
        db = utills.Utills()
        dados = request.form.to_dict()
        db.cadastrar_fornecedor(dados)
        return redirect('/cadastros/fornecedor')

    @app.route('/cadastros/despesas')
    def tela_cadastro_despesas():
        if 'usuario' in session:
            empresa = session['empresa']
            return render_template('cadastro_despesa.html', empresa=empresa)
        else:
            print('usario não está logado')
            return redirect('/')

    @app.route('/cadastros/despesas-cadastrar', methods=['GET', 'POST'])
    def cadastrar_despesa():
        if session['empresa'] == 'gr7':
            if request.method == 'POST':
                despesa = request.form['despesa']
                db = dados_notas.DadosGastos()
                db.cadastrar_despesa(despesa)
                # Criar tela retorno
                return 'Despesa cadastrada'
            else:
                return 'erro aqui'
        elif session['empresa'] == 'portal':
            if request.method == 'POST':
                despesa = request.form['despesa']
                db = dados_notas.DadosGastosPortal()
                db.cadastrar_despesa(despesa)
                return 'Despesa cadastrada'
            else:
                return 'erro aqui'

    @app.route('/consultar_notas', methods=['GET', 'POST'])
    def consultas():
        if 'usuario' in session:
            if session['empresa'] == 'gr7':
                empresa = session['empresa']
                db = dados_notas.DadosGastos()
                db_utils = utills.Utills()

                fornecedores = db_utils.fornecedores()
                despesas = db_utils.despesas()
                notas = []

                data_inicio = request.args.get('data_inicio')
                data_fim = request.args.get('data_fim')
                fornecedor = request.args.get('fornecedor')
                despesa = request.args.get('despesa')

                if request.method == 'POST':
                    data_inicio = request.form.get('data_inicio')
                    data_fim = request.form.get('data_fim')
                    fornecedor = request.form.get('fornecedor')
                    despesa = request.form.get('despesa')
                    notas = db.filtrar_notas(
                        data_inicio, data_fim, fornecedor, despesa)
                    valor = db.filtrar_notas_valor(
                        data_inicio, data_fim, fornecedor, despesa)
                elif data_inicio or data_fim or fornecedor or despesa:
                    notas = db.filtrar_notas(
                        data_inicio, data_fim, fornecedor, despesa)
                    valor = db.filtrar_notas_valor(
                        data_inicio, data_fim, fornecedor, despesa)
                else:
                    notas = db.todas_as_notas()
                    valor = db.valor_nota()

                # Configuração da paginação
            # page = request.args.get(get_page_parameter(), type=int, default=1)
                # per_page = 10
                # offset = (page - 1) * per_page
                # paginated_notas = notas[offset: offset + per_page]

                # pagination = Pagination(page=page, total=len(notas), per_page=per_page, css_framework='bootstrap4')

                return render_template('consultar_notas.html', empresa=empresa, fornecedores=fornecedores, despesas=despesas, notas=notas,
                                       data_inicio=data_inicio, data_fim=data_fim, fornecedor=fornecedor, despesa=despesa, valor=valor)
            elif session['empresa'] == 'portal':
                empresa = session['empresa']
                db = dados_notas.DadosGastosPortal()
                db_utils = utills.Utills_portal()

                fornecedores = db_utils.fornecedores()
                despesas = db_utils.despesas()
                notas = []

                data_inicio = request.args.get('data_inicio')
                data_fim = request.args.get('data_fim')
                fornecedor = request.args.get('fornecedor')
                despesa = request.args.get('despesa')

                if request.method == 'POST':
                    data_inicio = request.form.get('data_inicio')
                    data_fim = request.form.get('data_fim')
                    fornecedor = request.form.get('fornecedor')
                    despesa = request.form.get('despesa')
                    notas = db.filtrar_notas(
                        data_inicio, data_fim, fornecedor, despesa)
                    valor = db.filtrar_notas_valor(
                        data_inicio, data_fim, fornecedor, despesa)
                elif data_inicio or data_fim or fornecedor or despesa:
                    notas = db.filtrar_notas(
                        data_inicio, data_fim, fornecedor, despesa)
                    valor = db.filtrar_notas_valor(
                        data_inicio, data_fim, fornecedor, despesa)
                else:
                    notas = db.todas_as_notas()
                    valor = db.valor_nota()
                # Configuração da paginação
            # page = request.args.get(get_page_parameter(), type=int, default=1)
                # per_page = 10
                # offset = (page - 1) * per_page
                # paginated_notas = notas[offset: offset + per_page]

                # pagination = Pagination(page=page, total=len(notas), per_page=per_page, css_framework='bootstrap4')

                return render_template('consultar_notas.html', empresa=empresa, fornecedores=fornecedores, despesas=despesas, notas=notas,
                                       data_inicio=data_inicio, data_fim=data_fim, fornecedor=fornecedor, despesa=despesa, valor=valor)
        else:
            print('Usuário não está logado')
            return redirect('/')

    @app.route('/consultar_boletos', methods=['GET', 'POST'])
    def consultar_boletos():
        if 'usuario' in session:
            if session['empresa'] == 'gr7':
                empresa = session['empresa']
                db = dados_notas.DadosGastos()
                db_utils = utills.Utills()
                fornecedores = db_utils.fornecedores()

                boletos = []

                if request.method == 'POST':
                    data_inicio = request.form.get('data_inicio')
                    data_fim = request.form.get('data_fim')
                    fornecedor = request.form.get('fornecedor')

                    # Obter boletos filtrados
                    boletos = db.filtrar_boletos(
                        data_inicio, data_fim, fornecedor)
                    valor = db.filtrar_boletos_valor(
                        data_inicio, data_fim, fornecedor)
                else:
                    # Se não houver filtros, exibir todos os boletos
                    boletos = db.todos_os_boletos()
                    valor = db.valor_boleto()
                # Configuração da paginação

                return render_template('consultar_boletos.html', empresa=empresa, fornecedores=fornecedores, boletos=boletos, valor=valor)
            elif session['empresa'] == 'portal':
                empresa = session['empresa']
                db = dados_notas.DadosGastosPortal()
                db_utils = utills.Utills_portal()
                fornecedores = db_utils.fornecedores()

                boletos = []

                if request.method == 'POST':
                    data_inicio = request.form.get('data_inicio')
                    data_fim = request.form.get('data_fim')
                    fornecedor = request.form.get('fornecedor')

                    # Obter boletos filtrado
                    boletos = db.filtrar_boletos(
                        data_inicio, data_fim, fornecedor)
                    valor = db.filtrar_boletos_valor(
                        data_inicio, data_fim, fornecedor)
                else:
                    # Se não houver filtros, exibir todos os boletos
                    boletos = db.todos_os_boletos()
                    valor = db.valor_boleto()

                return render_template('consultar_boletos.html', empresa=empresa, fornecedores=fornecedores, boletos=boletos, valor=valor)

        else:
            print('Usuário não está logado')
            return redirect('/')

    @app.route('/faturamento', methods=['GET', 'POST'])
    def tela_faturamentos():
        if 'usuario' in session:
            if session['empresa'] == 'gr7':
                if session['permission'] == 'ADMIN':
                    empresa = session['empresa']
                    db = faturamento.Faturamento()
                    services = utills.Utills()
                    # Certifique-se de passar a conexão com o banco de dados

                    meses = [
                        ('01', 'Janeiro'), ('02', 'Fevereiro'), ('03',
                                                                 'Março'), ('04', 'Abril'), ('05', 'Maio'),
                        ('06', 'Junho'), ('07', 'Julho'), ('08',
                                                           'Agosto'), ('09', 'Setembro'), ('10', 'Outubro'),
                        ('11', 'Novembro'), ('12', 'Dezembro')
                    ]

                    anos = ['2024', '2025', '2026',
                            '2027', '2028', '2029', '2030']

                    if request.method == 'POST':
                        try:
                            mes_dados = request.form.get('mes', '')
                            ano_dados = request.form.get('ano', '')

                            # Verificar se os valores estão corretos
                            print(f"Mes selecionado: {
                                  mes_dados}, Ano selecionado: {ano_dados}")

                            if mes_dados and ano_dados:
                                # Processar filtro de faturamentos
                                valor_faturamento_total = db.faturamento_total_mes(
                                    mes_dados, ano_dados)
                                valor_faturamento_meta = db.faturamento_meta_mes(
                                    mes_dados, ano_dados)
                                faturamento_mecanicos = db.faturamento_mecanico(
                                    mes_dados, ano_dados)
                                faturamento_cias = db.faturamento_companhia(
                                    mes_dados, ano_dados)
                                faturamento_servico = db.faturamento_servico(
                                    mes_dados, ano_dados)
                                valor_dinheiro = db.faturamento_dinheiro(
                                    mes_dados, ano_dados)

                            else:
                                # Usar data atual se não houver filtros específicos para faturamentos
                                now = datetime.now()
                                mes_dados = now.strftime('%m')
                                ano_dados = now.strftime('%Y')
                                valor_faturamento_total = db.faturamento_total_mes(
                                    mes_dados, ano_dados)
                                valor_faturamento_meta = db.faturamento_meta_mes(
                                    mes_dados, ano_dados)
                                faturamento_mecanicos = db.faturamento_mecanico(
                                    mes_dados, ano_dados)
                                faturamento_cias = db.faturamento_companhia(
                                    mes_dados, ano_dados)
                                faturamento_servico = db.faturamento_servico(
                                    mes_dados, ano_dados)
                                valor_dinheiro = db.faturamento_dinheiro(
                                    mes_dados, ano_dados)
                            return render_template('faturamentos.html',
                                                   anos=anos,
                                                   meses=meses,
                                                   valor_faturamento_total=valor_faturamento_total,
                                                   valor_faturamento_meta=valor_faturamento_meta,
                                                   faturamento_mecanicos=faturamento_mecanicos,
                                                   faturamento_companhia=faturamento_cias,
                                                   faturamento_servico=faturamento_servico,
                                                   empresa=empresa, valor_dinheiro=valor_dinheiro)
                        except Exception as e:
                            print(
                                f"Ocorreu um erro ao processar o formulário: {e}")
                            return "Ocorreu um erro ao processar o formulário", 500

                    else:
                        # Caso seja uma requisição GET, usar a data atual
                        now = datetime.now()
                        mes_dados = now.strftime('%m')
                        ano_dados = now.strftime('%Y')
                        valor_faturamento_total = db.faturamento_total_mes(
                            mes_dados, ano_dados)
                        valor_faturamento_meta = db.faturamento_meta_mes(
                            mes_dados, ano_dados)
                        faturamento_mecanicos = db.faturamento_mecanico(
                            mes_dados, ano_dados)
                        faturamento_cias = db.faturamento_companhia(
                            mes_dados, ano_dados)
                        faturamento_servico = db.faturamento_servico(
                            mes_dados, ano_dados)
                        valor_dinheiro = db.faturamento_dinheiro(
                            mes_dados, ano_dados)
                        return render_template('faturamentos.html',
                                               anos=anos,
                                               meses=meses,
                                               valor_faturamento_total=valor_faturamento_total,
                                               valor_faturamento_meta=valor_faturamento_meta,
                                               faturamento_mecanicos=faturamento_mecanicos,
                                               faturamento_companhia=faturamento_cias,
                                               faturamento_servico=faturamento_servico,
                                               empresa=empresa, valor_dinheiro=valor_dinheiro)
            elif session['empresa'] == 'portal':
                if session['permission'] == 'ADMIN':
                    empresa = session['empresa']
                    db = faturamento.FaturamentoPortal()
                    services = utills.Utills_portal()
                    # Certifique-se de passar a conexão com o banco de dados

                    meses = [
                        ('01', 'Janeiro'), ('02', 'Fevereiro'), ('03',
                                                                 'Março'), ('04', 'Abril'), ('05', 'Maio'),
                        ('06', 'Junho'), ('07', 'Julho'), ('08',
                                                           'Agosto'), ('09', 'Setembro'), ('10', 'Outubro'),
                        ('11', 'Novembro'), ('12', 'Dezembro')
                    ]

                    anos = ['2024', '2025', '2026',
                            '2027', '2028', '2029', '2030']

                    if request.method == 'POST':
                        try:
                            mes_dados = request.form.get('mes', '')
                            ano_dados = request.form.get('ano', '')

                            # Verificar se os valores estão corretos
                            print(f"Mes selecionado: {
                                  mes_dados}, Ano selecionado: {ano_dados}")

                            if mes_dados and ano_dados:
                                # Processar filtro de faturamentos
                                valor_faturamento_total = db.faturamento_total_mes(
                                    mes_dados, ano_dados)
                                valor_faturamento_meta = db.faturamento_meta_mes(
                                    mes_dados, ano_dados)
                                faturamento_mecanicos = db.faturamento_mecanico(
                                    mes_dados, ano_dados)
                                faturamento_cias = db.faturamento_companhia(
                                    mes_dados, ano_dados)
                                faturamento_servico = db.faturamento_servico(
                                    mes_dados, ano_dados)
                                valor_dinheiro = db.faturamento_dinheiro(
                                    mes_dados, ano_dados)

                            else:
                                # Usar data atual se não houver filtros específicos para faturamentos
                                now = datetime.now()
                                mes_dados = now.strftime('%m')
                                ano_dados = now.strftime('%Y')
                                valor_faturamento_total = db.faturamento_total_mes(
                                    mes_dados, ano_dados)
                                valor_faturamento_meta = db.faturamento_meta_mes(
                                    mes_dados, ano_dados)
                                faturamento_mecanicos = db.faturamento_mecanico(
                                    mes_dados, ano_dados)
                                faturamento_cias = db.faturamento_companhia(
                                    mes_dados, ano_dados)
                                faturamento_servico = db.faturamento_servico(
                                    mes_dados, ano_dados)
                                valor_dinheiro = db.faturamento_dinheiro(
                                    mes_dados, ano_dados)

                            return render_template('faturamentos.html',
                                                   anos=anos,
                                                   meses=meses,
                                                   valor_faturamento_total=valor_faturamento_total,
                                                   valor_faturamento_meta=valor_faturamento_meta,
                                                   faturamento_mecanicos=faturamento_mecanicos,
                                                   faturamento_companhia=faturamento_cias,
                                                   faturamento_servico=faturamento_servico,
                                                   empresa=empresa)
                        except Exception as e:
                            print(
                                f"Ocorreu um erro ao processar o formulário: {e}")
                            return "Ocorreu um erro ao processar o formulário", 500
                    else:
                        # Caso seja uma requisição GET, usar a data atual
                        now = datetime.now()
                        mes_dados = now.strftime('%m')
                        ano_dados = now.strftime('%Y')
                        valor_faturamento_total = db.faturamento_total_mes(
                            mes_dados, ano_dados)
                        valor_faturamento_meta = db.faturamento_meta_mes(
                            mes_dados, ano_dados)
                        faturamento_mecanicos = db.faturamento_mecanico(
                            mes_dados, ano_dados)
                        faturamento_cias = db.faturamento_companhia(
                            mes_dados, ano_dados)
                        faturamento_servico = db.faturamento_servico(
                            mes_dados, ano_dados)
                        valor_dinheiro = db.faturamento_dinheiro(
                            mes_dados, ano_dados)
                        return render_template('faturamentos.html',
                                               anos=anos,
                                               meses=meses,
                                               valor_faturamento_total=valor_faturamento_total,
                                               valor_faturamento_meta=valor_faturamento_meta,
                                               faturamento_mecanicos=faturamento_mecanicos,
                                               faturamento_companhia=faturamento_cias,
                                               faturamento_servico=faturamento_servico,
                                               empresa=empresa)
                elif session['permission'] == 'NORMAL':
                    empresa = session['empresa']
                    db = faturamento.FaturamentoPortal()
                    services = utills.Utills_portal()
                    # Certifique-se de passar a conexão com o banco de dados

                    meses = [
                        ('01', 'Janeiro'), ('02', 'Fevereiro'), ('03',
                                                                 'Março'), ('04', 'Abril'), ('05', 'Maio'),
                        ('06', 'Junho'), ('07', 'Julho'), ('08',
                                                           'Agosto'), ('09', 'Setembro'), ('10', 'Outubro'),
                        ('11', 'Novembro'), ('12', 'Dezembro')
                    ]

                    anos = ['2024', '2025', '2026',
                            '2027', '2028', '2029', '2030']

                    if request.method == 'POST':
                        try:
                            mes_dados = request.form.get('mes', '')
                            ano_dados = request.form.get('ano', '')

                            # Verificar se os valores estão corretos
                            print(f"Mes selecionado: {
                                  mes_dados}, Ano selecionado: {ano_dados}")

                            if mes_dados and ano_dados:
                                # Processar filtro de faturamentos
                                valor_faturamento_total = db.faturamento_total_mes(
                                    mes_dados, ano_dados)
                                valor_faturamento_meta = db.faturamento_meta_mes(
                                    mes_dados, ano_dados)
                                faturamento_mecanicos = db.faturamento_mecanico(
                                    mes_dados, ano_dados)
                                faturamento_cias = db.faturamento_companhia(
                                    mes_dados, ano_dados)
                                faturamento_servico = db.faturamento_servico(
                                    mes_dados, ano_dados)
                                valor_dinheiro = db.faturamento_dinheiro(
                                    mes_dados, ano_dados)

                            else:
                                # Usar data atual se não houver filtros específicos para faturamentos
                                now = datetime.now()
                                mes_dados = now.strftime('%m')
                                ano_dados = now.strftime('%Y')
                                valor_faturamento_total = db.faturamento_total_mes(
                                    mes_dados, ano_dados)
                                valor_faturamento_meta = db.faturamento_meta_mes(
                                    mes_dados, ano_dados)
                                faturamento_mecanicos = db.faturamento_mecanico(
                                    mes_dados, ano_dados)
                                faturamento_cias = db.faturamento_companhia(
                                    mes_dados, ano_dados)
                                faturamento_servico = db.faturamento_servico(
                                    mes_dados, ano_dados)
                                valor_dinheiro = db.faturamento_dinheiro(
                                    mes_dados, ano_dados)

                            return render_template('faturamentos.html',
                                                   anos=anos,
                                                   meses=meses,
                                                   valor_faturamento_total=valor_faturamento_total,
                                                   valor_faturamento_meta=valor_faturamento_meta,
                                                   faturamento_mecanicos=faturamento_mecanicos,
                                                   faturamento_companhia=faturamento_cias,
                                                   faturamento_servico=faturamento_servico,
                                                   empresa=empresa)
                        except Exception as e:
                            print(
                                f"Ocorreu um erro ao processar o formulário: {e}")
                            return "Ocorreu um erro ao processar o formulário", 500
                    else:
                        # Caso seja uma requisição GET, usar a data atual
                        now = datetime.now()
                        mes_dados = now.strftime('%m')
                        ano_dados = now.strftime('%Y')
                        valor_faturamento_total = db.faturamento_total_mes(
                            mes_dados, ano_dados)
                        valor_faturamento_meta = db.faturamento_meta_mes(
                            mes_dados, ano_dados)
                        faturamento_mecanicos = db.faturamento_mecanico(
                            mes_dados, ano_dados)
                        faturamento_cias = db.faturamento_companhia(
                            mes_dados, ano_dados)
                        faturamento_servico = db.faturamento_servico(
                            mes_dados, ano_dados)
                        return render_template('faturamentos.html',
                                               anos=anos,
                                               meses=meses,
                                               valor_faturamento_total=valor_faturamento_total,
                                               valor_faturamento_meta=valor_faturamento_meta,
                                               faturamento_mecanicos=faturamento_mecanicos,
                                               faturamento_companhia=faturamento_cias,
                                               faturamento_servico=faturamento_servico,
                                               empresa=empresa)

        else:
            print('Usuário não está logado')
            return redirect('/')

    @app.route('/faturamentos/cadastrar', methods=['GET', 'POST'])
    def cadastrar_faturamento():
        if 'usuario' in session:
            if session['empresa'] == 'gr7':
                empresa = session['empresa']
                db = faturamento.Faturamento()
                cias = db.companhias()
                print(cias)  # Exemplo, substitua com os valores reais
                mecanicos = db.funcionarios()
                print(mecanicos)
                return render_template('cadastrar_faturamento.html', empresa=empresa, cias=cias, mecanicos=mecanicos)
            elif session['empresa'] == 'portal':
                empresa = session['empresa']
                db = faturamento.FaturamentoPortal()
                cias = db.companhias()
                print(cias)  # Exemplo, substitua com os valores reais
                mecanicos = db.funcionarios()
                print(mecanicos)
                return render_template('cadastrar_faturamento.html', empresa=empresa, cias=cias, mecanicos=mecanicos)
        else:
            print('Usuário não está logado')
            return redirect('/')

    @app.route('/submit_form', methods=['POST'])
    def submit_form():
        if session['empresa'] == 'gr7':
            db = faturamento.Faturamento()
            data = request.form.to_dict()
            print(data)
            db.cadastrar(data)
            return redirect('/faturamentos/cadastrar')
        elif session['empresa'] == 'portal':
            db = faturamento.FaturamentoPortal()
            data = request.form.to_dict()
            print(data)
            db.cadastrar(data)
            return redirect('/faturamentos/cadastrar')

    @app.route('/faturamentos/consultar', methods=['GET', 'POST'])
    def consultar_faturamentos():
        if 'usuario' in session:
            if session['empresa'] == 'gr7':
                empresa = session['empresa']
                # Certifique-se de passar a conexão com o banco de dados
                db = faturamento.Faturamento()

                # Listas para preencher os selects
                cias = db.companhias()
                print(cias)  # Exemplo, substitua com os valores reais
                mecanicos = db.funcionarios()
                print(mecanicos)  # Exemplo, substitua com os valores reais

                if request.method == 'POST':
                    data_inicio = request.form.get('data_inicio')
                    data_fim = request.form.get('data_fim')
                    companhia = request.form.get('companhia')
                    numero_os = request.form.get('numero_os')
                    placa = request.form.get('placa')
                    mecanico_servico = request.form.get('mecanico_servico')

                    # Implementar a lógica para buscar os faturamentos no banco de dados com base nos filtros
                    faturamentos = db.faturamentos_gerais(
                        data_inicio, data_fim, placa, mecanico_servico, numero_os, companhia)
                else:
                    # Se for uma requisição GET, buscar todos os faturamentos ou usar uma lógica padrão
                    faturamentos = db.faturamentos_gerais()

                if faturamentos is None:
                    faturamentos = []

                return render_template('consultar_faturamento.html',
                                       empresa=empresa,
                                       cias=cias,
                                       mecanicos=mecanicos,
                                       faturamentos=faturamentos)

            elif session['empresa'] == 'portal':
                empresa = session['empresa']
                # Certifique-se de passar a conexão com o banco de dados
                db = faturamento.FaturamentoPortal()

                # Listas para preencher os selects
                cias = db.companhias()
                print(cias)  # Exemplo, substitua com os valores reais
                mecanicos = db.funcionarios()
                print(mecanicos)  # Exemplo, substitua com os valores reais

                if request.method == 'POST':
                    data_inicio = request.form.get('data_inicio')
                    data_fim = request.form.get('data_fim')
                    companhia = request.form.get('companhia')
                    numero_os = request.form.get('numero_os')
                    placa = request.form.get('placa')
                    mecanico_servico = request.form.get('mecanico_servico')

                    # Implementar a lógica para buscar os faturamentos no banco de dados com base nos filtros

                    faturamentos = db.faturamentos_gerais(
                        data_inicio, data_fim, placa, mecanico_servico, numero_os, companhia)
                else:
                    # Se for uma requisição GET, buscar todos os faturamentos ou usar uma lógica padrão
                    faturamentos = db.faturamentos_gerais()

                if faturamentos is None:
                    faturamentos = []

                # Lógica de paginação

                return render_template('consultar_faturamento.html',
                                       empresa=empresa,
                                       cias=cias,
                                       mecanicos=mecanicos,
                                       faturamentos=faturamentos)

            else:
                return redirect('/')

    @app.route('/cadastros/companhias')
    def tela_cadastro_companhia():
        if 'usuario' in session:
            empresa = session['empresa']
            return render_template('cadastrar_companhias.html', empresa=empresa)
        else:
            print('usario não está logado')
            return redirect('/')

    @app.route('/cadastros/baterias')
    def tela_cadastro_bateria():
        if 'usuario' in session:
            empresa = session['empresa']
            return render_template('cadastrar_bateria.html', empresa=empresa)
        else:
            print('usario não está logado')
            return redirect('/')

    @app.route('/cadastros/oleos')
    def tela_cadastro_oleo():
        if 'usuario' in session:
            empresa = session['empresa']
            return render_template('cadastrar_oleo.html', empresa=empresa)
        else:
            print('usario não está logado')
            return redirect('/')

    @app.route('/cadastros/funcionarios')
    def tela_cadastro_funcionarios():
        if 'usuario' in session:
            empresa = session['empresa']
            return render_template('cadastrar_funcionarios.html', empresa=empresa)
        else:
            print('usario não está logado')
            return redirect('/')

    @app.route('/oleo-cadastrar', methods=['GET', 'POST'])
    def cadastrar_oleos():
        if request.method == 'POST':
            if session['empresa'] == 'gr7':
                dados = request.form.to_dict()
                db = dados_notas.DadosGastos()
                db.cadastrar_oleo(dados)
                return redirect('/cadastros/oleos')
            elif session['empresa'] == 'portal':
                dados = request.form.to_dict()
                db = dados_notas.DadosGastosPortal()
                db.cadastrar_oleo(dados)
                return redirect('/cadastros/oleos')
        else:
            return 'erro aqui'

    @app.route('/cadastros/companhia-cadastrar', methods=['GET', 'POST'])
    def cadastrar_companhia():
        if request.method == 'POST':
            if session['empresa'] == 'gr7':
                dados = request.form.to_dict()
                db = dados_notas.DadosGastos()
                db.cadastrar_companhia(dados)
                return redirect('/cadastros/companhias')
            elif session['empresa'] == 'portal':
                dados = request.form.to_dict()
                db = dados_notas.DadosGastosPortal()
                db.cadastrar_companhia(dados)
                return redirect('/cadastros/companhias')
        else:
            return 'erro aqui'

    @app.route('/funcionario-cadastrar', methods=['GET', 'POST'])
    def cadastrar_funcionario():
        if request.method == 'POST':
            if session['empresa'] == 'gr7':
                dados = request.form.to_dict()
                db = dados_notas.DadosGastos()
                db.cadastrar_funcionario(dados)
                return redirect('/cadastros/funcionarios')
            elif session['empresa'] == 'portal':
                dados = request.form.to_dict()
                db = dados_notas.DadosGastosPortal()
                db.cadastrar_funcionario(dados)
                return redirect('/cadastros/funcionarios')
        else:
            return 'erro aqui'

    @app.route('/bateria-cadastrar', methods=['GET', 'POST'])
    def cadastrar_bateria():
        if request.method == 'POST':
            if session['empresa'] == 'gr7':
                dados = request.form.to_dict()
                db = dados_notas.DadosGastos()
                db.cadastrar_baterias(dados)
                return redirect('/cadastros/oleos')
            elif session['empresa'] == 'portal':
                dados = request.form.to_dict()
                db = dados_notas.DadosGastosPortal()
                db.cadastrar_baterias(dados)
                return redirect('/cadastros/oleos')
        else:
            return 'erro aqui'
