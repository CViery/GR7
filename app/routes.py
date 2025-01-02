from app import app
from flask import request, redirect, render_template, flash, session, jsonify, make_response, Response
from services import login, cadastrar_notas, cadastrar_duplicata, dados_notas, faturamento, utills, xlxs, rotas
from datetime import datetime
from flask_paginate import Pagination, get_page_parameter
from database import gastos_db
from xhtml2pdf import pisa
from io import BytesIO
import json


PERMISSAO_TOTAL_ADMIN = 0
PERMISSAO_GR7_USER = 1
PERMISSAO_PORTAL_ADMIN = 2

class Routes:
    def __init__(self):
        pass

    @app.route('/')
    def show_login():
        return render_template('login.html')

    @app.route('/autenticar', methods=['POST'])
    def autenticar():
        try:
            usuario = request.form.get('usuario')
            senha = request.form.get('senha')
            empresa = request.form.get('empresa')

            # Verificar se os campos obrigatórios estão presentes
            if not usuario or not senha or not empresa:
                flash('Preencha todos os campos!')
                return redirect('/')

            db = login.Login()
            auten = db.login(usuario.upper(), senha)

            if auten == 'ADMIN':
                session['usuario'] = usuario
                session['empresa'] = empresa
                if empresa == 'gr7':
                    if session['permission_empresa'] in [PERMISSAO_TOTAL_ADMIN, PERMISSAO_GR7_USER]:
                        return redirect('/home')
                    else:
                        flash('Desculpe, seu acesso não permite acessar esta área.')
                        return redirect('/')
                elif empresa == 'portal':
                    if session['permission_empresa'] in [PERMISSAO_PORTAL_ADMIN, PERMISSAO_TOTAL_ADMIN]:
                        return redirect('/home')
                    else:
                        flash('Desculpe, empresa inválida ou sem permissão.')
                        return redirect('/')
            elif auten == 'NORMAL':
                session['usuario'] = usuario
                session['empresa'] = empresa
                if empresa == 'gr7':
                    if session['permission_empresa'] in [PERMISSAO_GR7_ADMIN, PERMISSAO_GR7_USER]:
                        return redirect('/home')
                    else:
                        flash('Desculpe, empresa inválida ou sem permissão.')
                        return redirect('/')
                elif empresa == 'portal':
                    if session['permission_empresa'] == PERMISSAO_PORTAL_ADMIN:
                        return redirect('/home')
                    else:
                        flash('Desculpe, empresa inválida ou sem permissão.')
                        return redirect('/')
                return 'Usuário Normal'
            else:
                flash('Usuário ou senha incorretos.')
                return redirect('/')

        except Exception as e:
            print(f"Erro durante autenticação: {e}")
            flash('Ocorreu um erro. Tente novamente.')
            return redirect('/')

    @app.route('/logout')
    def logout():
        # Remover todas as variáveis de sessão relacionadas ao usuário
        session.pop('usuario', None)
        session.pop('empresa', None)
        session.pop('permission_empresa', None)  # Caso esteja utilizando esta variável
        flash('Você saiu da sessão com sucesso.')
        return redirect('/')

    
    @app.route('/home')
    def home():
        try:
            # Verificar se o usuário está logado
            if 'usuario' not in session:
                flash('Usuário não está logado.')
                return redirect('/')

            # Obter as informações da sessão
            usuario = session['usuario']
            empresa = session['empresa']
            permission = session.get('permission', None)

            if empresa == 'gr7':
                if permission == 'ADMIN':
                    return rotas.render_gr7_admin(usuario)
                else:
                    flash('Você não tem permissão para acessar esta página.')
                    return redirect('/')

            elif empresa == 'portal':
                if permission == 'ADMIN':
                    return rotas.render_portal_admin(usuario)
                elif permission == 'NORMAL':
                    return rotas.render_portal_normal(usuario)
                else:
                    flash('Permissão de acesso inválida.')
                    return redirect('/')

            else:
                flash('Empresa não reconhecida.')
                return redirect('/')

        except Exception as e:
            print(f"Erro no carregamento da página home: {e}")
            flash('Ocorreu um erro ao carregar a página. Tente novamente.')
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
            USUARIO = session['usuario']
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
                'despesa': request.form['despesa'],
                'sub': request.form['subcategoria'],
                'usuario': USUARIO,
                'obs':request.form['obs']
            }
            print(dados)
            enviar.cadastrar(dados, USUARIO)
            if dados['boleto'] == 'Sim':
                return render_template('cadastrar_boleto.html', empresa=session['empresa'], num_nota=dados['nota'], fornecedor=dados['fornecedor'])
            else:
                flash('Nota cadastrada')
                return redirect('/gastos/cadastros/notas')
        elif session['empresa'] == 'portal':
            # alterar dados para banco portal
            enviar = cadastrar_notas.NotasPortal()
            USUARIO = session['usuario']
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
                'despesa': request.form['despesa'],
                'sub': request.form['subcategoria'],
                'usuario': USUARIO,
                'obs':request.form['obs']
            }
            enviar.cadastrar(dados,USUARIO)
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

            return render_template('resposta_cadastro.html', rota='/gastos/cadastros/duplicatas')
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
            db.cadastrar_duplicatas(duplicata)

            # Aqui você pode salvar a duplicata no banco de dados
            # ...

            return render_template('resposta_cadastro.html', rota='/gastos/cadastros/duplicatas')

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
        def get_mes_nome(mes_codigo):
                match mes_codigo:
                    case "01": return 'Janeiro'
                    case "02": return "Fevereiro"
                    case "03": return "Março"
                    case "04": return "Abril"
                    case "05": return "Maio"
                    case "06": return "Junho"
                    case "07": return "Julho"
                    case "08": return "Agosto"
                    case "09": return "Setembro"
                    case "10": return "Outubro"
                    case "11": return "Novembro"
                    case "12": return "Dezembro"
        if 'usuario' in session:
            if session['empresa'] == 'gr7':
                session['link'] = '/gastos'
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

                        ano_dados = request.form['ano']

                        dados_tipos = db.dados_gastos(mes_dados, ano_dados)
                        valor_gasto = db.valor_gastos(mes_dados, ano_dados)
                        mes_select = get_mes_nome(mes_dados)
                        ano_select = ano_dados

                    else:
                        # Usar data atual se não houver filtros específicos para despesas
                        now = datetime.now()
                        mes_dados = now.strftime('%m')

                        ano_dados = now.strftime('%Y')
                        dados_tipos = db.dados_gastos(mes_dados, ano_dados)
                        valor_gasto = db.valor_gastos(mes_dados, ano_dados)
                        mes_select = get_mes_nome(mes_dados)
                        ano_select = ano_dados

                    if 'dia' in request.form:
                        # Processar formulário de filtro de boletos
                        data = request.form['dia']
                        dia = data[8:]
                        mes = data[5:7]
                        ano = data[:4]
                        boletos = db.boletos_do_dia(dia, mes, ano)
                        valor_a_pagar = db.valor_a_pagar(dia, mes, ano)
                        dia = data
                    else:
                        # Usar data atual se não houver filtro específico para boletos
                        now = datetime.now()
                        dia = now.strftime('%d')
                        mes = now.strftime('%m')
                        ano = now.strftime('%Y')
                        boletos = db.boletos_do_dia(dia, mes, ano)
                        valor_a_pagar = db.valor_a_pagar(dia, mes, ano)
                        

                    return render_template('gastos.html', anos=anos, meses=meses, tipo_despesa=dados_tipos, empresa=empresa, boletos=boletos, valor_gastos=valor_gasto, valor_a_pagar=valor_a_pagar, mes_escolhido = mes_select, ano_escolhido = ano_select)
                else:
                    # Caso seja uma requisição GET, usar a data atual
                    now = datetime.now()
                    dia = now.strftime('%d')
                    mes = now.strftime('%m')
                    ano = now.strftime('%Y')
                    dados_tipos = db.dados_gastos(mes, ano)
                    boletos = db.boletos_do_dia(dia, mes, ano)
                    valor_gasto = db.valor_gastos(mes, ano)
                    valor_a_pagar = db.valor_a_pagar(dia, mes, ano)
                    mes_select = get_mes_nome(mes)
                    ano_select = ano
                    dia = now
                    return render_template('gastos.html', anos=anos, meses=meses, tipo_despesa=dados_tipos, empresa=empresa, boletos=boletos, valor_gastos=valor_gasto, valor_a_pagar=valor_a_pagar,mes_escolhido = mes_select, ano_escolhido = ano_select, dia=dia)
            if session['empresa'] == 'portal':
                if session['permission'] == 'ADMIN':
                    empresa = session['empresa']
                    session['link'] = '/gastos'
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

                            ano_dados = request.form['ano']

                            dados_tipos = db.dados_gastos(mes_dados, ano_dados)
                            print(dados_tipos)
                            valor_gasto = db.valor_gastos(mes_dados, ano_dados)
                            mes_select = get_mes_nome(mes_dados)
                            ano_select = ano_dados

                        else:
                            # Usar data atual se não houver filtros específicos para despesas
                            now = datetime.now()
                            mes_dados = now.strftime('%m')

                            ano_dados = now.strftime('%Y')
                            dados_tipos = db.dados_gastos(mes_dados, ano_dados)
                            print(dados_tipos)
                            valor_gasto = db.valor_gastos(mes_dados, ano_dados)
                            mes_select = get_mes_nome(mes_dados)
                            ano_select = ano_dados

                        if 'dia' in request.form:
                            # Processar formulário de filtro de boletos
                            data = request.form['dia']
                            dia = data[8:]
                            mes = data[5:7]
                            ano = data[:4]
                            boletos = db.boletos_do_dia(dia, mes, ano)
                            valor_a_pagar = db.valor_a_pagar(dia, mes, ano)
                            mes_select = get_mes_nome(mes)
                            ano_select = ano
                        else:
                            # Usar data atual se não houver filtro específico para boletos
                            now = datetime.now()
                            dia = now.strftime('%d')
                            mes = now.strftime('%m')
                            ano = now.strftime('%Y')
                            boletos = db.boletos_do_dia(dia, mes, ano)
                            valor_a_pagar = db.valor_a_pagar(dia, mes, ano)
                            mes_select = get_mes_nome(mes)
                            ano_select = ano

                        return render_template('gastos.html', anos=anos, meses=meses, tipo_despesa=dados_tipos, empresa=empresa, boletos=boletos, valor_gastos=valor_gasto, valor_a_pagar=valor_a_pagar,mes_escolhido = mes_select, ano_escolhido = ano_select, dia=dia)
                    else:
                        # Caso seja uma requisição GET, usar a data atual
                        now = datetime.now()
                        dia = now.strftime('%d')
                        mes = now.strftime('%m')
                        ano = now.strftime('%Y')
                        dados_tipos = db.dados_gastos(mes, ano)
                        boletos = db.boletos_do_dia(dia, mes, ano)
                        valor_gasto = db.valor_gastos(mes, ano)
                        valor_a_pagar = db.valor_a_pagar(dia, mes, ano)
                        mes_select = get_mes_nome(mes)
                        ano_select = ano

                        return render_template('gastos.html', anos=anos, meses=meses, tipo_despesa=dados_tipos, empresa=empresa, boletos=boletos, valor_gastos=valor_gasto, valor_a_pagar=valor_a_pagar,mes_escolhido = mes_select, ano_escolhido = ano_select, dia=dia)
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
        if session['empresa'] == 'gr7':
            db = utills.Utills()
            dados = request.form.to_dict()
            db.cadastrar_fornecedor(dados)
            return redirect('/cadastros/fornecedor')
        elif session['empresa'] == 'portal':
            db = utills.Utills_portal()
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
                return redirect('/cadastros/despesas')
            else:
                return 'erro aqui'
        elif session['empresa'] == 'portal':
            if request.method == 'POST':
                despesa = request.form['despesa']
                db = dados_notas.DadosGastosPortal()
                db.cadastrar_despesa(despesa)
                return redirect('/cadastros/despesas')
            else:
                return 'erro aqui'

    @app.route('/consultar_notas', methods=['GET', 'POST'])
    def consultas():
        if 'usuario' in session:
            if session['empresa'] == 'gr7':
                empresa = session['empresa']
                session['link'] = '/consultar_notas'
                db = dados_notas.DadosGastos()
                db_utils = utills.Utills()
                mes = str(datetime.now().month)
                ano = str(datetime.now().year)
                fornecedores = db_utils.fornecedores()
                despesas = db_utils.despesas()
                notas = []

                data_inicio = request.args.get('data_inicio')
                data_fim = request.args.get('data_fim')
                fornecedor = request.args.get('fornecedor')
                despesa = request.args.get('despesa')
                obs = request.args.get('obs')

                if request.method == 'POST':
                    data_inicio = request.form.get('data_inicio')
                    data_fim = request.form.get('data_fim')
                    fornecedor = request.form.get('fornecedor')
                    despesa = request.form.get('despesa')
                    obs = request.form.get('obs')
                    notas = db.filtrar_notas(
                        data_inicio, data_fim, fornecedor, despesa, obs)
                    
                    valor = db.filtrar_notas_valor(
                        data_inicio, data_fim, fornecedor, despesa, obs)
                elif data_inicio or data_fim or fornecedor or despesa or obs:
                    notas = db.filtrar_notas(
                        data_inicio, data_fim, fornecedor, despesa, obs)
                    valor = db.filtrar_notas_valor(
                        data_inicio, data_fim, fornecedor, despesa, obs)
                else:
                    notas = db.todas_as_notas_mes(mes, ano)
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
                session['link'] = '/consultar_notas'
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


    @app.route('/dados_boletos/<num_nota>', methods=['GET', 'POST'])
    def dados_boletos(num_nota):
         if 'usuario' in session:
            if session['empresa'] == 'gr7':
                empresa = session['empresa']
                db = dados_notas.DadosGastos()
                boletos = db.todos_os_boletos_por_nota(num_nota)
                quantidade = len(boletos)
                valor = db.valor_gastos_boletos_valor(num_nota)
                link = session['link']
                nota = db.nota_por_numero(num_nota)
                return render_template('dados_boletos.html', empresa=empresa, boletos=boletos, valor=valor, quantidade=quantidade, num_nota=num_nota, link=link, nota=nota)
            elif session['empresa'] == 'portal':
                empresa = session['empresa']
                db = dados_notas.DadosGastosPortal()
                boletos = db.todos_os_boletos_por_nota(num_nota)
                quantidade = len(boletos)
                valor = db.valor_gastos_boletos_valor(num_nota)
                link = session['link']
                nota = db.nota_por_numero(num_nota)
                return render_template('dados_boletos.html', empresa=empresa, boletos=boletos, valor=valor, quantidade=quantidade, num_nota=num_nota, link=link, nota=nota)
        

    @app.route('/consultar_boletos', methods=['GET', 'POST'])
    def consultar_boletos():
        if 'usuario' in session:
            if session['empresa'] == 'gr7':
                session['link'] = '/consultar_boleto'
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
                session['link'] = '/consultar_boleto'
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
                    def get_mes_nome(mes_codigo):
                        match mes_codigo:
                            case "01": return 'Janeiro'
                            case "02": return "Fevereiro"
                            case "03": return "Março"
                            case "04": return "Abril"
                            case "05": return "Maio"
                            case "06": return "Junho"
                            case "07": return "Julho"
                            case "08": return "Agosto"
                            case "09": return "Setembro"
                            case "10": return "Outubro"
                            case "11": return "Novembro"
                            case "12": return "Dezembro"
                            
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

                            if mes_dados and ano_dados:
                                session['mes_atual'] = mes_dados
                                session['ano_atual'] = ano_dados
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
                                ticket = services.ticket(mes_dados, ano_dados)
                                passagens = services.passagens(
                                    mes_dados, ano_dados)
                                valor_meta_int = db.faturamento_meta_mes_int(mes_dados, ano_dados)
                                mes_select = get_mes_nome(mes_dados)
                                ano_select = ano_dados

                            else:
                                # Usar data atual se não houver filtros específicos para faturamentos
                                now = datetime.now()
                                mes_dados = now.strftime('%m')
                                ano_dados = now.strftime('%Y')
                                session['mes_atual'] = mes_dados
                                print(mes_dados)
                                session['ano_atual'] = ano_dados
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
                                ticket = services.ticket(mes_dados, ano_dados)
                                passagens = services.passagens(
                                    mes_dados, ano_dados)
                                valor_meta_int = db.faturamento_meta_mes_int(mes_dados, ano_dados)
                                mes_select = get_mes_nome(mes_dados)
                               
                                ano_select = ano_dados
                            return render_template('faturamentos.html',
                                                   anos=anos,
                                                   meses=meses,
                                                   valor_faturamento_total=valor_faturamento_total,
                                                   valor_faturamento_meta=valor_faturamento_meta,
                                                   faturamento_mecanicos=faturamento_mecanicos,
                                                   faturamento_companhia=faturamento_cias,
                                                   faturamento_servico=faturamento_servico,
                                                   empresa=empresa, valor_dinheiro=valor_dinheiro,
                                                   ticket=ticket,
                                                   passagens=passagens,
                                                   valor_meta_int=valor_meta_int,
                                                   mes_escolhido = mes_select,
                                                   ano_escolhido = ano_select
                                                   )
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
                        ticket = services.ticket(mes_dados, ano_dados)
                        passagens = services.passagens(mes_dados, ano_dados)
                        valor_meta_int = db.faturamento_meta_mes_int(mes_dados, ano_dados)
                        mes_select = get_mes_nome(mes_dados)
                        
                        ano_select = ano_dados
                        return render_template('faturamentos.html',
                                               anos=anos,
                                               meses=meses,
                                               valor_faturamento_total=valor_faturamento_total,
                                               valor_faturamento_meta=valor_faturamento_meta,
                                               faturamento_mecanicos=faturamento_mecanicos,
                                               faturamento_companhia=faturamento_cias,
                                               faturamento_servico=faturamento_servico,
                                               empresa=empresa, valor_dinheiro=valor_dinheiro, ticket=ticket, passagens=passagens, valor_meta_int=valor_meta_int, mes_escolhido=mes_select,
                                               ano_escolhido=ano_select)
                    
            elif session['empresa'] == 'portal':
                if session['permission'] == 'ADMIN':
                    def get_mes_nome(mes_codigo):
                        match mes_codigo:
                            case "01": return 'Janeiro'
                            case "02": return "Fevereiro"
                            case "03": return "Março"
                            case "04": return "Abril"
                            case "05": return "Maio"
                            case "06": return "Junho"
                            case "07": return "Julho"
                            case "08": return "Agosto"
                            case "09": return "Setembro"
                            case "10": return "Outubro"
                            case "11": return "Novembro"
                            case "12": return "Dezembro"
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
                                ticket = services.ticket(mes_dados, ano_dados)
                                passagens = services.passagens(
                                    mes_dados, ano_dados)
                                valor_meta_int = db.faturamento_meta_mes_int(mes_dados, ano_dados)
                                mes_select = get_mes_nome(mes_dados)
                                ano_select = ano_dados
                                
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
                                ticket = services.ticket(mes_dados, ano_dados)
                                passagens = services.passagens(
                                    mes_dados, ano_dados)
                                valor_meta_int = db.faturamento_meta_mes_int(mes_dados, ano_dados)
                                mes_select = get_mes_nome(mes_dados)
                                ano_select = ano_dados
                            return render_template('faturamentos.html',
                                                   anos=anos,
                                                   meses=meses,
                                                   valor_faturamento_total=valor_faturamento_total,
                                                   valor_faturamento_meta=valor_faturamento_meta,
                                                   faturamento_mecanicos=faturamento_mecanicos,
                                                   faturamento_companhia=faturamento_cias,
                                                   faturamento_servico=faturamento_servico,
                                                   empresa=empresa, ticket=ticket,
                                                   passagens=passagens,
                                                   valor_meta_int=valor_meta_int,mes_escolhido=mes_select,
                                               ano_escolhido=ano_select,valor_dinheiro=valor_dinheiro)
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
                        ticket = services.ticket(mes_dados, ano_dados)
                        passagens = services.passagens(mes_dados, ano_dados)
                        valor_meta_int = db.faturamento_meta_mes_int(mes_dados, ano_dados)
                        mes_select = get_mes_nome(mes_dados)
                        ano_select = ano_dados
                        
                        return render_template('faturamentos.html',
                                               anos=anos,
                                               meses=meses,
                                               valor_faturamento_total=valor_faturamento_total,
                                               valor_faturamento_meta=valor_faturamento_meta,
                                               faturamento_mecanicos=faturamento_mecanicos,
                                               faturamento_companhia=faturamento_cias,
                                               faturamento_servico=faturamento_servico,
                                               empresa=empresa, ticket=ticket, passagens=passagens, valor_meta_int=valor_meta_int,mes_escolhido=mes_select,
                                               ano_escolhido=ano_select,valor_dinheiro=valor_dinheiro)
                elif session['permission'] == 'NORMAL':
                    def get_mes_nome(mes_codigo):
                        match mes_codigo:
                            case "01": return 'Janeiro'
                            case "02": return "Fevereiro"
                            case "03": return "Março"
                            case "04": return "Abril"
                            case "05": return "Maio"
                            case "06": return "Junho"
                            case "07": return "Julho"
                            case "08": return "Agosto"
                            case "09": return "Setembro"
                            case "10": return "Outubro"
                            case "11": return "Novembro"
                            case "12": return "Dezembro"
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
                                ticket = services.ticket(mes_dados, ano_dados)
                                passagens = services.passagens(
                                    mes_dados, ano_dados)
                                valor_meta_int = db.faturamento_meta_mes_int(mes_dados, ano_dados)
                                mes_select = get_mes_nome(mes_dados)
                                ano_select = ano_dados
                                

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
                                ticket = services.ticket(mes_dados, ano_dados)
                                passagens = services.passagens(
                                    mes_dados, ano_dados)
                                valor_meta_int = db.faturamento_meta_mes_int(mes_dados, ano_dados)
                                mes_select = get_mes_nome(mes_dados)
                                ano_select = ano_dados
                               

                            return render_template('faturamentos.html',
                                                   anos=anos,
                                                   meses=meses,
                                                   valor_faturamento_total=valor_faturamento_total,
                                                   valor_faturamento_meta=valor_faturamento_meta,
                                                   faturamento_mecanicos=faturamento_mecanicos,
                                                   faturamento_companhia=faturamento_cias,
                                                   faturamento_servico=faturamento_servico,
                                                   empresa=empresa, ticket=ticket,
                                                   passagens=passagens, valor_meta_int=valor_meta_int,mes_escolhido=mes_select,
                                               ano_escolhido=ano_select,valor_dinheiro=valor_dinheiro)
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
                        ticket = services.ticket(mes_dados, ano_dados)
                        passagens = services.passagens(mes_dados, ano_dados)
                        mes_select = get_mes_nome(mes_dados)
                        ano_select = ano_dados
                        valor_meta_int = db.faturamento_meta_mes_int(mes_dados, ano_dados)
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
                                               empresa=empresa, ticket=ticket, passagens=passagens, valor_meta_int=valor_meta_int,mes_escolhido=mes_select,
                                               ano_escolhido=ano_select,valor_dinheiro=valor_dinheiro)

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
                mecanicos = db.funcionarios()
                response = ''
                return render_template('cadastrar_faturamento.html', empresa=empresa, cias=cias, mecanicos=mecanicos, response=response)
            elif session['empresa'] == 'portal':
                empresa = session['empresa']
                db = faturamento.FaturamentoPortal()
                cias = db.companhias()
              # Exemplo, substitua com os valores reais
                mecanicos = db.funcionarios()
                response = ''
                return render_template('cadastrar_faturamento.html', empresa=empresa, cias=cias, mecanicos=mecanicos, response=response)
        else:
            print('Usuário não está logado')
            return redirect('/')

    @app.route('/submit_form', methods=['POST'])
    def submit_form():
        if session['empresa'] == 'gr7':
            db = faturamento.Faturamento()
            data = request.form.to_dict()
            USUARIO = session['usuario']
            cadastrar = db.cadastrar(data, USUARIO)
            if cadastrar:
                db = faturamento.Faturamento()
                cias = db.companhias()
                empresa = session['empresa']
                mecanicos = db.funcionarios()
                response = f'A OS {data['num_os']} Já esta cadastrada'
                return render_template('cadastrar_faturamento.html', empresa=empresa, cias=cias, mecanicos=mecanicos, response=response)
            else:
                db = faturamento.Faturamento()
                cias = db.companhias()
                empresa = session['empresa']
                mecanicos = db.funcionarios()
                response = f'A OS {data['num_os']} CADASTRADA COM SUCESSO'
                return render_template('cadastrar_faturamento.html', empresa=empresa, cias=cias, mecanicos=mecanicos, response=response)
        elif session['empresa'] == 'portal':
            db = faturamento.FaturamentoPortal()
            data = request.form.to_dict()
            USUARIO = session['usuario']
            cadastrar = db.cadastrar(data, USUARIO)
            if cadastrar:
                db = faturamento.FaturamentoPortal()
                cias = db.companhias()
                empresa = session['empresa']
                mecanicos = db.funcionarios()
                response = f'A OS {data['num_os']} Já esta cadastrada'
                return render_template('cadastrar_faturamento.html', empresa=empresa, cias=cias, mecanicos=mecanicos, response=response)
            else:
                db = faturamento.FaturamentoPortal()
                cias = db.companhias()
                empresa = session['empresa']
                mecanicos = db.funcionarios()
                response = f'A OS {data['num_os']} CADASTRADA COM SUCESSO'
                return render_template('cadastrar_faturamento.html', empresa=empresa, cias=cias, mecanicos=mecanicos, response=response)
            

    @app.route('/faturamentos/consultar', methods=['GET', 'POST'])
    def consultar_faturamentos():
        if 'usuario' in session:
            if session['empresa'] == 'gr7':
                empresa = session['empresa']
                # Certifique-se de passar a conexão com o banco de dados
                db = faturamento.Faturamento()
                
                # Listas para preencher os selects
                cias = db.companhias()

                mecanicos = db.funcionarios()

                exportar = None
                
                if request.method == 'POST':
                    data_inicio = request.form.get('data_inicio')
                    data_fim = request.form.get('data_fim')
                    companhia = request.form.get('companhia')
                    numero_os = request.form.get('num_os')
                    
                    placa = request.form.get('placa')
                    mecanico_servico = request.form.get('mecanico_servico')

                    # Implementar a lógica para buscar os faturamentos no banco de dados com base nos filtros
                    faturamentos = db.filtrar_os(
                        data_inicio, data_fim, placa, mecanico_servico, numero_os, companhia)
                    
                    valor = db.filtrar_os_valor(data_inicio, data_fim, placa, mecanico_servico, numero_os, companhia)
                    valor_meta = db.filtrar_os_valor_meta(data_inicio, data_fim, placa, mecanico_servico, numero_os, companhia)
                        
                else:
                    # Se for uma requisição GET, buscar todos os faturamentos ou usar uma lógica padrão
                    faturamentos = db.faturamentos_gerais()
                    valor = db.faturamentos_gerais_valor()
                    valor_meta = db.faturamentos_gerais_valor_meta()
                    
                        

                if faturamentos is None:
                    faturamentos = []

                return render_template('consultar_faturamento.html',
                                       empresa=empresa,
                                       cias=cias,
                                       mecanicos=mecanicos,
                                       faturamentos=faturamentos, valor=valor, valor_meta=valor_meta)

            elif session['empresa'] == 'portal':
                empresa = session['empresa']
                # Certifique-se de passar a conexão com o banco de dados
                db = faturamento.FaturamentoPortal()

                # Listas para preencher os selects
                cias = db.companhias()

                mecanicos = db.funcionarios()

                if request.method == 'POST':
                    data_inicio = request.form.get('data_inicio')
                    data_fim = request.form.get('data_fim')
                    companhia = request.form.get('companhia')
                    numero_os = request.form.get('num_os')
                    placa = request.form.get('placa')
                    mecanico_servico = request.form.get('mecanico_servico')

                    # Implementar a lógica para buscar os faturamentos no banco de dados com base nos filtros

                    faturamentos = db.filtrar_os(
                        data_inicio, data_fim, placa, mecanico_servico, numero_os, companhia)
                    valor = db.filtrar_os_valor(data_inicio, data_fim, placa, mecanico_servico, numero_os, companhia)
                    valor_meta = db.filtrar_os_valor_meta(data_inicio, data_fim, placa, mecanico_servico, numero_os, companhia)
                    
                else:
                    # Se for uma requisição GET, buscar todos os faturamentos ou usar uma lógica padrão
                    faturamentos = db.faturamentos_gerais()
                    valor = db.faturamentos_gerais_valor()
                    valor_meta = db.faturamentos_gerais_valor_meta()
                    

                if faturamentos is None:
                    faturamentos = []

                # Lógica de paginação

                return render_template('consultar_faturamento.html',
                                       empresa=empresa,
                                       cias=cias,
                                       mecanicos=mecanicos,
                                       faturamentos=faturamentos,valor=valor, valor_meta=valor_meta)

            else:
                return redirect('/')
            
    @app.route('/faturamentos/ordens_com_dinheiro/', methods=['GET', 'POST'])
    def consultar_faturamentos_c_dinheiro():
        if 'usuario' in session:
            if session['empresa'] == 'gr7':
                mes = session.get('mes_atual')
                ano = session.get('ano_atual')
                empresa = session['empresa']
                # Certifique-se de passar a conexão com o banco de dados
                db = faturamento.Faturamento()
                
                # Listas para preencher os selects
                

                faturamentos = db.faturamento_dinheiro_ordens(mes,ano)
                valor = db.faturamento_dinheiro(mes,ano)
                if faturamentos is None:
                    faturamentos = []

                return render_template('consultar_faturamento_dinheiro.html',
                                       empresa=empresa,
                                       faturamentos=faturamentos, valor=valor)

            elif session['empresa'] == 'portal':
                mes = session.get('mes_atual')
                ano = session.get('ano_atual')
                empresa = session['empresa']
                # Certifique-se de passar a conexão com o banco de dados
                db = faturamento.FaturamentoPortal()
                

                faturamentos = db.faturamento_dinheiro_ordens(mes,ano)
                valor = db.faturamento_dinheiro(mes,ano)
                if faturamentos is None:
                    faturamentos = []

                return render_template('consultar_faturamento_dinheiro.html',
                                       empresa=empresa,
                                       faturamentos=faturamentos, valor=valor)

            else:
                return redirect('/')

    @app.route('/baixar')
    def baixar_excel():
        if 'usuario' in session:
            if 'dados_exportar' in session:
                dados = session['dados_exportar']
                excel = xlxs.GerarExcel()
                arquivo = excel.exportar_faturamentos_excel(dados)
                
                if arquivo:
                    return arquivo
                else:
                    print('Erro ao gerar o arquivo Excel.')
                    return redirect('/faturamentos/consultar')
            else:
                print('Dados para exportação não encontrados na sessão.')
                return redirect('/faturamentos/consultar')
        else:
            print('Usuário não está logado.')
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

    @app.route('/relatorios')
    def page_relatorios():
        return render_template('relatorios.html')




    @app.route('/fechamento_mensal', methods=['GET', 'POST'])
    def gerar_pdf():
        mes = request.form.get('mes')
        ano = request.form.get('ano')
        print(f'mes selecionado {mes}')
        print(f'Ano selecionado {ano}')
        # Dados para o template
        db = faturamento.Faturamento()
        services = utills.Utills()
        empresa = 'gr7'
        valor_faturamento_total = db.faturamento_total_mes(mes, ano)
        valor_faturamento_meta = db.faturamento_meta_mes(mes, ano)
        faturamento_mecanicos = db.faturamento_mecanico(mes, ano)
        faturamento_cias = db.faturamento_companhia(mes, ano)
        faturamento_servico = db.faturamento_servico(mes, ano)
        valor_dinheiro = db.faturamento_dinheiro(mes, ano)
        ticket = services.ticket(mes, ano)
        passagens = services.passagens(mes, ano)
        valor_meta_int = db.faturamento_meta_mes_int(mes, ano)
        mecanicos = db.faturamento_mecanico(mes, ano)
        dados_filtros = db.filtros_mecanico(mes, ano) 
        context = {
            'valor_faturamento_total': valor_faturamento_total,
            'valor_faturamento_meta': valor_faturamento_meta,
            'faturamento_mecanicos': faturamento_mecanicos,
            'faturamento_companhia': faturamento_cias,
            'faturamento_servico': faturamento_servico,
            'empresa': 'empresa',
            'valor_dinheiro': valor_dinheiro,
            'ticket': ticket,
            'passagens': passagens,
            'valor_meta_int': valor_meta_int,
            'mes_escolhido': mes,
            'ano_escolhido': ano,
            'dados_filtros': dados_filtros
        }
        
        # Renderiza o template HTML
        html = render_template('relatorio_faturamento.html', **context)
        
        # Gera um buffer em memória para o PDF
        pdf_buffer = BytesIO()
        
        # Gera o PDF
        pisa_status = pisa.CreatePDF(
            html.encode('utf-8'), dest=pdf_buffer, encoding='utf-8'
        )
        
        # Verifica se ocorreu um erro
        if pisa_status.err:
            return "Erro ao gerar o PDF", 500

        # Nome seguro para o arquivo
        name_arquivo = f"Relatorio_{mes}_{ano}".replace(" ", "_").replace("/", "-")
        
        # Movendo o ponteiro do buffer para o início
        pdf_buffer.seek(0)
        
        # Retorna o PDF como uma resposta Flask
        response = Response(
            pdf_buffer,
            content_type='application/pdf'
        )
        response.headers['Content-Disposition'] = f'attachment; filename="{name_arquivo}.pdf"'
        return response

    @app.route('/api/subcategorias', methods=['GET'])
    def get_subcategorias():
        if session['empresa'] == 'gr7' or 'portal':
            despesa = request.args.get('despesa')
            if not despesa:
                return jsonify([])

            # Substitua com sua lógica para buscar subcategorias no banco de dados
            db = gastos_db.GastosDataBase()
            dados = db.get_subcategorias(despesa)
            subcategorias = dados
            subcategorias = [sub[3] for sub in subcategorias]
            print(subcategorias)
            return jsonify(subcategorias)

    @app.route('/editar/faturamento/<int:num_os>', methods=['GET', 'POST'])
    def editar_faturamento(num_os):
        if 'usuario' in session:
            if session['permission'] == 'ADMIN' and session['empresa'] == 'gr7':
                db = faturamento.Faturamento()
                try:
                    # Obter os dados da ordem de serviço
                    ordem = db.ordem_de_servico(num_os)
                    ordem_dict = json.loads(ordem)

                    if request.method == 'POST':
                        try:
                            # Validar e processar os dados enviados pelo formulário
                            updated_data = {
                                "placa": request.form.get('placa'),
                                "modelo_veiculo": request.form.get('modelo_veiculo'),
                                "data_orcamento": request.form.get('data_orcamento'),
                                "data_faturamento": request.form.get('data_faturamento'),
                                "mes_faturamento": request.form.get('mes_faturamento'),
                                "ano_faturamento": request.form.get('ano_faturamento'),
                                "dias_servico": request.form.get('dias_servico'),
                                "numero_os": request.form.get('numero_os'),
                                "companhia": request.form.get('companhia'),
                                "valor_pecas": float(request.form.get('valor_pecas', 0)),
                                "valor_servicos": float(request.form.get('valor_servicos', 0)),
                                "total_os": float(request.form.get('total_os', 0)),
                                "mecanico_servico": request.form.get('mecanico_servico'),
                                "valor_servico_freios": float(request.form.get('valor_servico_freios', 0)),
                                "valor_servico_suspensao": float(request.form.get('valor_servico_suspensao', 0)),
                                "valor_servico_injecao_ignicao": float(request.form.get('valor_servico_injecao_ignicao', 0)),
                                "valor_servico_cabecote_motor_arr": float(request.form.get('valor_servico_cabecote_motor_arr', 0)),
                                "valor_outros_servicos": float(request.form.get('valor_outros_servicos', 0)),
                                "valor_servicos_oleos": float(request.form.get('valor_servicos_oleos', 0)),
                                "valor_servico_transmissao": float(request.form.get('valor_servico_transmissao', 0)),
                                "obs": request.form.get('obs'),
                            }

                            # Atualizar no banco de dados
                            db.atualizar_ordem_de_servico(num_os, updated_data)
                            flash("Ordem de serviço atualizada com sucesso!", "success")
                            return redirect('/faturamentos/consultar')
                        except Exception as e:
                            flash(f"Erro ao atualizar: {e}", "danger")
                    return render_template('editar_faturamento.html', ordem=ordem_dict)
                except Exception as e:
                    return f"Erro ao buscar ordem de serviço: {e}", 500
        return "Acesso negado", 403
