from app import app
from flask import request, redirect, render_template, flash, session, jsonify, make_response, Response
from services import login, cadastrar_notas, cadastrar_duplicata, dados_notas, faturamento, utills, xlxs, rotas
from datetime import datetime
from flask_paginate import Pagination, get_page_parameter
from database import gastos_db, conection
from xhtml2pdf import pisa
from io import BytesIO
import json
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.drawing.image import Image

PERMISSAO_TOTAL_ADMIN = 0
PERMISSAO_GR7_USER = 1
PERMISSAO_PORTAL_ADMIN = 2
SEM_PERMISSAO = 3
PERMISSAO_GR7_MORUMBI_ADMIN = 4

# Dados simulados
lojas = ["Loja 1", "Loja 2"]
funcionarios = {"Loja 1": ["Carlos", "Ana"], "Loja 2": ["Marcos", "Julia"]}

dados_loja = {
    "Loja 1": {"meses": ["Jan", "Fev", "Mar"], "faturamento": [10000, 12000, 15000], "servicos": ["Fluido", "Sangria", "Filtro"], "quantidades": [50, 30, 40]},
    "Loja 2": {"meses": ["Jan", "Fev", "Mar"], "faturamento": [8000, 11000, 14000], "servicos": ["Fluido", "Sangria", "Filtro"], "quantidades": [40, 35, 45]}
}

dados_funcionario = {
    "Carlos": {"meses": ["Jan", "Fev", "Mar"], "desempenho": [2000, 2500, 3000]},
    "Ana": {"meses": ["Jan", "Fev", "Mar"], "desempenho": [1800, 2300, 2800]},
    "Marcos": {"meses": ["Jan", "Fev", "Mar"], "desempenho": [2200, 2700, 3200]},
    "Julia": {"meses": ["Jan", "Fev", "Mar"], "desempenho": [1900, 2400, 2900]}
}


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
                elif empresa == 'gr7 morumbi':
                    if session['permission_empresa'] in [PERMISSAO_GR7_MORUMBI_ADMIN, PERMISSAO_TOTAL_ADMIN]:
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
                elif empresa == 'gr7 morumbi':
                    if session['permission_empresa'] == PERMISSAO_GR7_MORUMBI_ADMIN:
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
                
            elif empresa == 'gr7 morumbi':
                if permission == 'ADMIN':
                    return rotas.render_gr7_morumbi_admin(usuario)
                elif permission == 'NORMAL':
                    return rotas.render_gr7_morumbi_normal(usuario)
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
            if session['empresa'] == 'gr7':
                db = utills.Utills()
            elif session['empresa'] == 'portal':
                db = utills.Utills_portal()
            elif session['empresa'] == 'gr7 morumbi':
                db = utills.UttilsGr7Morumbi()
            
            fornecedores = db.fornecedores()
            despesas = db.despesas()
            empresa = session['empresa']
            emitido_para = db.emitido_para()
            return render_template('cadastrar_notas.html', empresa=empresa, fornecedores=fornecedores, despesas=despesas, emitido_para=emitido_para)
        else:
            flash('usario não está logado')
            return redirect('/')

    @app.route('/gastos/cadastros/notas-cadastrar-nota', methods=['POST'])
    def cadastrar_nota():
        if session['empresa'] == 'gr7':
            enviar = cadastrar_notas.Notas()
        elif session['empresa'] == 'portal':
            enviar = cadastrar_notas.NotasPortal()
        elif session['empresa'] == 'gr7 morumbi':
            enviar = cadastrar_notas.Notas_morumbi()
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
        enviar.cadastrar(dados, USUARIO)
        if dados['boleto'] == 'Sim':
            return render_template('cadastrar_boleto.html', empresa=session['empresa'], num_nota=dados['nota'], fornecedor=dados['fornecedor'])
        else:
            flash('Nota cadastrada')
            return redirect('/gastos/cadastros/notas')

    @app.route('/gastos/cadatro/duplicata')
    def duplicata():
        if 'usuario' in session:
            empresa = session['empresa']
            return render_template('cadastrar_duplicatas.html', empresa=empresa)
        else:
            print('usario não está logado')
            return redirect('/')

    @app.route('/cadastrar_boletos', methods=['POST'])
    def cadastrar_boletos():
        try:
            # Define o banco de dados de acordo com a empresa que o usuario está logado
            if session['empresa'] == 'gr7':
                db = cadastrar_notas.Boletos()
            elif session['empresa'] == 'portal':
                db = cadastrar_notas.BoletosPortal()
            elif session['empresa'] == 'gr7 morumbi':
                db = cadastrar_notas.BoletosMorumbi()
            else:
                return "Empresa não reconhecida", 400

            # Coleta e processa os dados do formulário
            numero_nota = request.form['num_nota']
            fornecedor = request.form['fornecedor']
            num_parcelas = int(request.form['numParcelas'])
            parcelas = []

            for i in range(1, num_parcelas + 1):
                valor = request.form[f'valorParcela{i}']
                data_vencimento = request.form[f'dataVencimento{i}']
                parcelas.append({'valor': valor, 'data_vencimento': data_vencimento})

            for parcela in parcelas:
                boleto = {
                    'num_nota': numero_nota,
                    'notas': '',
                    'fornecedor': fornecedor,
                    'vencimento': parcela['data_vencimento'],
                    'valor': parcela['valor']
                }
                db.cadastrar(boleto)

            flash('Boletos cadastrados com sucesso!')
            return redirect('/gastos/cadastros/notas')
        
        except Exception as e:
            print(f'Erro: {e}')
            return "Erro no processamento dos dados", 400
        
    @app.route('/api/nota/<numero_nota>', methods=['GET'])
    def get_nota(numero_nota):
        if session['empresa'] == 'gr7':
            db = dados_notas.DadosGastos()
        elif session['empresa'] == 'portal':
            db = dados_notas.DadosGastosPortal()
        elif session['empresa'] == 'gr7 morumbi':
            db = dados_notas.DadosGastosMorumbi()
            
        nota = db.nota_por_numero(numero_nota)
        if nota:
            return jsonify(nota)
        else:
            return jsonify({'error': 'Nota não encontrada'}), 404
        
    @app.route('/cadastrar_duplicata', methods=['POST'])
    def cadastrar_duplicata():
        if session['empresa'] == 'gr7':
            db = cadastrar_duplicata.Boletos()
        elif session['empresa'] == 'portal':
            db = cadastrar_duplicata.BoletosPortal()
        elif session['empresa'] == 'gr7 morumbi':
            db = cadastrar_duplicata.Boletos_morumbi()

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
            
        db.cadastrar_duplicatas(duplicata)

            # Aqui você pode salvar a duplicata no banco de dados
            # Colocar para retornar na tela de cadastos

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

        if 'usuario' not in session:
            print('Usuário não está logado')
            return redirect('/')

        empresa = session.get('empresa')
        session['link'] = '/gastos'

        # Seleciona o banco de dados conforme a empresa
        if empresa == 'gr7':
            db = dados_notas.DadosGastos()
        elif empresa == 'portal':
            if session.get('permission') == 'ADMIN':
                db = dados_notas.DadosGastosPortal()
            else:
                return render_template('resposta_permissao.html', empresa=empresa)
        elif empresa == 'gr7 morumbi':
            db = dados_notas.DadosGastosMorumbi()
        else:
            return "Empresa não suportada", 400

        meses = [(f"{i:02}", get_mes_nome(f"{i:02}")) for i in range(1, 13)]
        anos = [str(ano) for ano in range(2024, 2031)]

        # Pega dados padrão (mês, ano, dia atuais)
        now = datetime.now()
        dia_atual = now.strftime('%d')
        mes_atual = now.strftime('%m')
        ano_atual = now.strftime('%Y')

        if request.method == 'POST':
            mes_dados = request.form.get('mes', mes_atual)
            ano_dados = request.form.get('ano', ano_atual)

            dados_tipos = db.dados_gastos(mes_dados, ano_dados)
            valor_gasto = db.valor_gastos(mes_dados, ano_dados)
            mes_select = get_mes_nome(mes_dados)
            ano_select = ano_dados

            if 'dia' in request.form:
                data = request.form['dia']
                dia = data[8:]
                mes = data[5:7]
                ano = data[:4]
            else:
                dia = dia_atual
                mes = mes_atual
                ano = ano_atual

            boletos = db.boletos_do_dia(dia, mes, ano)
            valor_a_pagar = db.valor_a_pagar(dia, mes, ano)

            return render_template('gastos.html', anos=anos, meses=meses,
                                tipo_despesa=dados_tipos, empresa=empresa,
                                boletos=boletos, valor_gastos=valor_gasto,
                                valor_a_pagar=valor_a_pagar, 
                                mes_escolhido=mes_select,
                                ano_escolhido=ano_select, dia=f"{ano}-{mes}-{dia}")
        else:
            # Requisição GET
            dados_tipos = db.dados_gastos(mes_atual, ano_atual)
            valor_gasto = db.valor_gastos(mes_atual, ano_atual)
            boletos = db.boletos_do_dia(dia_atual, mes_atual, ano_atual)
            valor_a_pagar = db.valor_a_pagar(dia_atual, mes_atual, ano_atual)

            return render_template('gastos.html', anos=anos, meses=meses,
                                tipo_despesa=dados_tipos, empresa=empresa,
                                boletos=boletos, valor_gastos=valor_gasto,
                                valor_a_pagar=valor_a_pagar,
                                mes_escolhido=get_mes_nome(mes_atual),
                                ano_escolhido=ano_atual,
                                dia=now.strftime('%Y-%m-%d'))

    @app.route('/atualizar', methods=['POST'])
    def atualizar_boletos():
        if 'empresa' not in session:
            return 'Sessão expirada ou não autenticada', 401

        empresa = session['empresa']

        # Seleciona o DB apropriado
        if empresa == 'gr7':
            db = dados_notas.DadosGastos()
        elif empresa == 'portal':
            db = dados_notas.DadosGastosPortal()
        elif empresa == 'gr7 morumbi':
            db = dados_notas.DadosGastosMorumbi()
        else:
            return 'Empresa não suportada', 400

        dia = request.form.get('dia')
        mes = request.form.get('mes')
        ano = request.form.get('ano')

        # Usa data atual se o campo dia não for fornecido
        if not dia:
            dia = datetime.now().strftime('%d')

        # Valida presença de mês e ano
        if not mes or not ano:
            return 'Parâmetros inválidos', 400

        boletos = db.boletos_do_dia(dia, mes, ano)
        return jsonify({'boletos': boletos})
    
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
        elif session['empresa'] == 'portal':
            db = utills.Utills_portal()
        elif session['empresa'] == 'gr7 morumbi':
            db = utills.UttilsGr7Morumbi()

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
        if request.method == 'POST':
            if session['empresa'] == 'gr7':
                db = dados_notas.DadosGastos()
            elif session['empresa'] == 'portal':
                db = dados_notas.DadosGastosPortal()
            elif session['empresa'] == 'gr7 morumbi':
                db = dados_notas.DadosGastosMorumbi()

            despesa = request.form['despesa']
                
            db.cadastrar_despesa(despesa)
            # Criar tela retorno
            return redirect('/cadastros/despesas')
        else:
            return 'erro aqui'

    @app.route('/consultar_notas', methods=['GET', 'POST'])
    def consultas():
        if 'usuario' in session:
            if session['empresa'] == 'gr7':
                db = dados_notas.DadosGastos()
                db_utils = utills.Utills()
            elif session['empresa'] == 'portal':
                db = dados_notas.DadosGastosPortal()
                db_utils = utills.Utills_portal()
            elif session['empresa'] == 'gr7 morumbi':
                db = dados_notas.DadosGastosMorumbi()
                db_utils = utills.UttilsGr7Morumbi()

            empresa = session['empresa']
            session['link'] = '/consultar_notas'
                
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
        else:
            print('Usuário não está logado')
            return redirect('/')


    @app.route('/dados_boletos/<num_nota>', methods=['GET', 'POST'])
    def dados_boletos(num_nota):
         if 'usuario' in session:
            if session['empresa'] == 'gr7':
                db = dados_notas.DadosGastos()
            elif session['empresa'] == 'portal':
                db = dados_notas.DadosGastosPortal()
            elif session['empresa'] == 'gr7 morumbi':
                db = dados_notas.DadosGastosMorumbi()
                
            empresa = session['empresa']
                
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
                db = dados_notas.DadosGastos()
                db_utils = utills.Utills()
            elif session['empresa'] == 'portal':
                db = dados_notas.DadosGastosPortal()
                db_utils = utills.Utills_portal()
            elif session['empresa'] == 'gr7 morumbi':
                db = dados_notas.DadosGastosMorumbi()
                db_utils = utills.UttilsGr7Morumbi()

            session['link'] = '/consultar_boleto'
            empresa = session['empresa']
                
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
        else:
            print('Usuário não está logado')
            return redirect('/')

    @app.route('/faturamento', methods=['GET', 'POST'])
    def tela_faturamentos():
        if 'usuario' not in session:
            print('Usuário não está logado')
            return redirect('/')

        empresa = session.get('empresa')
        permissao = session.get('permission')

       
        match empresa:
            case 'gr7':
                db = faturamento.Faturamento()
                services = utills.Utills()
            case 'portal':
                db = faturamento.FaturamentoPortal()
                services = utills.Utills_portal()
            case 'gr7 morumbi':
                db = faturamento.FaturamentoMorumbi()
                services = utills.UttilsGr7Morumbi()
            case _:
                return "Empresa não suportada", 400

        
        def get_mes_nome(codigo):
            meses_map = {
                '01': 'Janeiro', '02': 'Fevereiro', '03': 'Março', '04': 'Abril',
                '05': 'Maio', '06': 'Junho', '07': 'Julho', '08': 'Agosto',
                '09': 'Setembro', '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro',
                '1': 'Janeiro', '2': 'Fevereiro', '3': 'Março', '4': 'Abril',
                '5': 'Maio', '6': 'Junho', '7': 'Julho', '8': 'Agosto',
                '9': 'Setembro', '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro'
            }
            return meses_map.get(str(int(codigo)).zfill(2), "Mês Inválido")

        
        meses = [(str(i).zfill(2), get_mes_nome(str(i))) for i in range(1, 13)]
        anos = [str(ano) for ano in range(2024, 2031)]

        
        if request.method == 'POST':
            mes_dados = request.form.get('mes')
            ano_dados = request.form.get('ano')
        else:
            now = datetime.now()
            mes_dados = now.strftime('%m')
            ano_dados = now.strftime('%Y')

       
        if mes_dados and ano_dados:
            session['mes_atual'] = mes_dados
            session['ano_atual'] = ano_dados

        try:
            
            valor_faturamento_total = db.faturamento_total_mes(mes_dados, ano_dados)
            valor_faturamento_meta = db.faturamento_meta_mes(mes_dados, ano_dados)
            faturamento_mecanicos = db.faturamento_mecanico(mes_dados, ano_dados)
            faturamento_cias = db.faturamento_companhia(mes_dados, ano_dados)
            faturamento_servico = db.faturamento_servico(mes_dados, ano_dados)
            valor_dinheiro = db.faturamento_dinheiro(mes_dados, ano_dados)
            ticket = services.ticket(mes_dados, ano_dados)
            passagens = services.passagens(mes_dados, ano_dados)
            valor_meta_int = db.faturamento_meta_mes_int(mes_dados, ano_dados)
            mes_select = get_mes_nome(mes_dados)
            ano_select = ano_dados

            return render_template(
                'faturamentos.html',
                anos=anos,
                meses=meses,
                valor_faturamento_total=valor_faturamento_total,
                valor_faturamento_meta=valor_faturamento_meta,
                faturamento_mecanicos=faturamento_mecanicos,
                faturamento_companhia=faturamento_cias,
                faturamento_servico=faturamento_servico,
                empresa=empresa,
                valor_dinheiro=valor_dinheiro,
                ticket=ticket,
                passagens=passagens,
                valor_meta_int=valor_meta_int,
                mes_escolhido=mes_select,
                ano_escolhido=ano_select
            )

        except Exception as e:
            print(f"Erro ao processar faturamento: {e}")
            return "Erro interno no servidor", 500

    @app.route('/faturamentos/cadastrar', methods=['GET', 'POST'])
    def cadastrar_faturamento():
        if 'usuario' in session:
            if session['empresa'] == 'gr7':
                db = faturamento.Faturamento()
            elif session['empresa'] == 'portal':
                db = faturamento.FaturamentoPortal()
            elif session['empresa'] == 'gr7 morumbi':
                db = faturamento.FaturamentoMorumbi()

            cias = db.companhias()
            mecanicos = db.funcionarios()
            response = ''
            empresa = session['empresa']
            print(empresa)
            return render_template('cadastrar_faturamento.html', empresa=empresa, cias=cias, mecanicos=mecanicos, response=response)
        else:
            print('Usuário não está logado')
            return redirect('/')

    @app.route('/submit_form', methods=['POST'])
    def submit_form():
        if session['empresa'] == 'gr7':
            db = faturamento.Faturamento()
        elif session['empresa'] == 'portal':
            db = faturamento.FaturamentoPortal()
        elif session['empresa'] == 'gr7 morumbi':
            db = faturamento.FaturamentoMorumbi()

        data = request.form.to_dict()
        USUARIO = session['usuario']
        cadastrar = db.cadastrar(data, USUARIO)
        if cadastrar:
            db = faturamento.Faturamento()
            cias = db.companhias()
            empresa = session['empresa']
            mecanicos = db.funcionarios()
            response = f"A OS {data['num_os']} Já está cadastrada"
            return render_template('cadastrar_faturamento.html', empresa=empresa, cias=cias, mecanicos=mecanicos, response=response)
        else:
            db = faturamento.Faturamento()
            cias = db.companhias()
            empresa = session['empresa']
            mecanicos = db.funcionarios()
            response = f"A OS {data['num_os']} CADASTRADA COM SUCESSO"
            return render_template('cadastrar_faturamento.html', empresa=empresa, cias=cias, mecanicos=mecanicos, response=response)           

    @app.route('/faturamentos/consultar', methods=['GET', 'POST'])
    def consultar_faturamentos():
        if 'usuario' in session:
            if session['empresa'] == 'gr7':
                empresa = session['empresa']
                db = faturamento.Faturamento()
            elif session['empresa'] == 'portal':
                empresa = session['empresa']
                db = faturamento.FaturamentoPortal()
            elif session['empresa'] == 'gr7 morumbi':
                empresa = session['empresa']
                db = faturamento.FaturamentoMorumbi()
            

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

            return render_template('consultar_faturamento.html',
                                       empresa=empresa,
                                       cias=cias,
                                       mecanicos=mecanicos,
                                       faturamentos=faturamentos, valor=valor, valor_meta=valor_meta)
        else:
            return redirect('/')
            
    @app.route('/faturamentos/ordens_com_dinheiro/', methods=['GET', 'POST'])
    def consultar_faturamentos_c_dinheiro():
        if 'usuario' in session:
            if session['empresa'] == 'gr7':
                db = faturamento.Faturamento()
            elif session['empresa'] == 'portal':
                db = faturamento.FaturamentoPortal()
            elif session['empresa'] == 'gr7 morumbi':
                db = faturamento.FaturamentoMorumbi()

            mes = session.get('mes_atual')
            ano = session.get('ano_atual')
            empresa = session['empresa']
                # Certifique-se de passar a conexão com o banco de dados
                
                
                # Listas para preencher os selects
                

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
                db = dados_notas.DadosGastos()
            elif session['empresa'] == 'portal':
                db = dados_notas.DadosGastosPortal
            elif session['empresa'] == 'gr7 morumbi':
                db = dados_notas.DadosGastosMorumbi()

            dados = request.form.to_dict()
            db.cadastrar_oleo(dados)
            return redirect('/cadastros/oleos')
        else:
            return 'erro aqui'

    @app.route('/cadastros/companhia-cadastrar', methods=['GET', 'POST'])
    def cadastrar_companhia():
        if request.method == 'POST':
            if session['empresa'] == 'gr7':
                db = dados_notas.DadosGastos()
            elif session['empresa'] == 'portal':
                db = dados_notas.DadosGastosPortal()
            elif session['empresa'] == 'gr7 morumbi':
                db = dados_notas.DadosGastosMorumbi()
                
            dados = request.form.to_dict()   
            db.cadastrar_companhia(dados)
            return redirect('/cadastros/companhias')
        else:
            return 'erro aqui'

    @app.route('/funcionario-cadastrar', methods=['GET', 'POST'])
    def cadastrar_funcionario():
        if request.method == 'POST':
            if session['empresa'] == 'gr7':
                db = dados_notas.DadosGastos()
            elif session['empresa'] == 'potal':
                db = dados_notas.DadosGastosPortal()
            elif session['empresa'] == 'potal':
                db = dados_notas.DadosGastosMorumbi()

            dados = request.form.to_dict()
            db.cadastrar_funcionario(dados)
            return redirect('/cadastros/funcionarios')
        else:
            return 'erro aqui'

    @app.route('/bateria-cadastrar', methods=['GET', 'POST'])
    def cadastrar_bateria():
        if request.method == 'POST':
            if session['empresa'] == 'gr7':
                db = dados_notas.DadosGastos()
            elif session['empresa'] == 'portal':
                db = dados_notas.DadosGastosPortal()
            elif session['empresa'] == 'gr7 morumbi':
                db = dados_notas.DadosGastosMorumbi()

            dados = request.form.to_dict()
            db.cadastrar_baterias(dados)
            return redirect('/cadastros/oleos')
        else:
            return 'erro aqui'

    @app.route('/relatorios')
    def page_relatorios():
        if session['empresa'] == 'gr7':
            db = faturamento.Faturamento()
            db_utils = utills.Utills()
        elif session['empresa'] == 'portal':
            db = faturamento.FaturamentoPortal()
            db_utils = utills.Utills()
        elif session['empresa'] == 'gr7 morumbi':
            db = faturamento.FaturamentoMorumbi()
            db_utils = utills.UttilsGr7Morumbi()

        departamentos = db_utils.despesas()
        mecanicos = db.funcionarios()
        context = {
                'departamentos': departamentos,
                'mecanicos': mecanicos
            } 
        return render_template('relatorios.html', **context)

    @app.route('/fechamento_mensal', methods=['GET', 'POST'])
    def gerar_pdf():
        if session['empresa'] == 'gr7':
            db = faturamento.Faturamento()
            services = utills.Utills()
            empresa = session['empresa']
        elif session['empresa'] == 'portal':
            db = faturamento.FaturamentoPortal()
            services = utills.Utills_portal()
            empresa = session['empresa']
        elif session['empresa'] == 'portal':
            db = faturamento.FaturamentoMorumbi()
            services = utills.UttilsGr7Morumbi()
            empresa = session['empresa']   
        mes = request.form.get('mes')
        ano = request.form.get('ano')
        # Dados para o template
        
        
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
        dados_revitalizacao = db.revitalizacao_mecanico(mes,ano)
        context = {
            'valor_faturamento_total': valor_faturamento_total,
            'valor_faturamento_meta': valor_faturamento_meta,
            'faturamento_mecanicos': faturamento_mecanicos,
            'faturamento_companhia': faturamento_cias,
            'faturamento_servico': faturamento_servico,
            'empresa': empresa,
            'valor_dinheiro': valor_dinheiro,
            'ticket': ticket,
            'passagens': passagens,
            'valor_meta_int': valor_meta_int,
            'mes_escolhido': mes,
            'ano_escolhido': ano,
            'dados_filtros': dados_filtros,
            'dados_revitalizacao': dados_revitalizacao
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
        if session['empresa'] == 'gr7' or 'portal' or 'gr7 morumbi':
            despesa = request.args.get('despesa')
            if not despesa:
                return jsonify([])

            # Substitua com sua lógica para buscar subcategorias no banco de dados
            db = gastos_db.GastosDataBase()
            dados = db.get_subcategorias(despesa)
            subcategorias = dados
            subcategorias = [sub[3] for sub in subcategorias]
            return jsonify(subcategorias)


    @app.route('/fechamento_filtros', methods=['GET', 'POST'])
    def gerar_relatorio_filtros():
        # Obtendo os valores do formulário
        if session['empresa'] == 'gr7':
            db = faturamento.Faturamento()
            services = utills.Utills()
            empresa = session['empresa']
        elif session['empresa'] == 'portal':
            db = faturamento.FaturamentoPortal()
            services = utills.Utills_portal()
            empresa = session['empresa']
        elif session['empresa'] == 'gr7 morumbi':
            db = faturamento.FaturamentoMorumbi()
            services = utills.UttilsGr7Morumbi()
            empresa = session['empresa']

        mes = request.form.get('mes')
        ano = request.form.get('ano')
        mecanico = request.form.get('mecanico')
        
      


        # Buscando os dados de acordo com os filtros
        dados = db.ordens_filtro_e_higienizacao(mes, ano, mecanico)
        
        # Definindo o nome da empresa
        empresa = session['empresa']

        # Contexto que será passado para o template
        context = {
            'empresa': empresa,
            'mecanico': mecanico,
            'mes': mes,
            'ano': ano,
            'dados': dados
        }

        # Renderizando o template HTML
        html = render_template('relatorio_filtros.html', **context)

        # Criando um buffer de memória para o PDF
        pdf_buffer = BytesIO()

        # Gerando o PDF a partir do HTML
        pisa_status = pisa.CreatePDF(
            html.encode('utf-8'), dest=pdf_buffer, encoding='utf-8'
        )

        # Verificando se ocorreu algum erro na geração do PDF
        if pisa_status.err:
            return "Erro ao gerar o PDF", 500

        # Criando um nome seguro para o arquivo
        name_arquivo = f"Relatorio_{mes}_{ano}_{mecanico}".replace(" ", "_").replace("/", "-")

        # Movendo o ponteiro do buffer para o início
        pdf_buffer.seek(0)

        # Retornando o PDF como resposta Flask
        response = Response(
            pdf_buffer,
            content_type='application/pdf'
        )
        response.headers['Content-Disposition'] = f'attachment; filename="{name_arquivo}.pdf"'

        return response

    @app.route('/fechamento_revitalizacao', methods=['GET', 'POST'])
    def gerar_relatorio_revitalizacao():
        # Obtendo os valores do formulário
        if session['empresa'] == 'gr7':
            db = faturamento.Faturamento()
            empresa = session['empresa']
        elif session['empresa'] == 'portal':
            db = faturamento.FaturamentoPortal()
            empresa = session['empresa']
        elif session['empresa'] == 'portal':
            db = faturamento.FaturamentoPortal()
            empresa = session['empresa']

        mes = request.form.get('mes')
        ano = request.form.get('ano')
        mecanico = request.form.get('mecanico')
        
        # Buscando os dados de acordo com os filtros
        dados = db.ordens_revitalizacao(mes, ano, mecanico)
        
        # Definindo o nome da empresa
        empresa = session['empresa']

        # Contexto que será passado para o template
        context = {
            'empresa': empresa,
            'mecanico': mecanico,
            'mes': mes,
            'ano': ano,
            'dados': dados
        }

        # Renderizando o template HTML
        html = render_template('relatorio_revitalizacao.html', **context)

        # Criando um buffer de memória para o PDF
        pdf_buffer = BytesIO()

        # Gerando o PDF a partir do HTML
        pisa_status = pisa.CreatePDF(
            html.encode('utf-8'), dest=pdf_buffer, encoding='utf-8'
        )

        # Verificando se ocorreu algum erro na geração do PDF
        if pisa_status.err:
            return "Erro ao gerar o PDF", 500

        # Criando um nome seguro para o arquivo
        name_arquivo = f"Relatorio_{mes}_{ano}_{mecanico}".replace(" ", "_").replace("/", "-")

        # Movendo o ponteiro do buffer para o início
        pdf_buffer.seek(0)

        # Retornando o PDF como resposta Flask
        response = Response(
            pdf_buffer,
            content_type='application/pdf'
        )
        response.headers['Content-Disposition'] = f'attachment; filename="{name_arquivo}.pdf"'

        return response
    
    @app.route('/fechamento_dinheiro', methods=['GET', 'POST'])
    def gerar_relatorio_dinheiro():
        # Obtendo os valores do formulário
        mes = request.form.get('mes')
        ano = request.form.get('ano')
        mecanico = request.form.get('mecanico')
        

        # Inicializando os objetos para acessar os dados
        if session['empresa'] == 'gr7':
            db = faturamento.Faturamento()
            empresa = session['empresa']
        elif session['empresa'] == 'portal':
            db = faturamento.FaturamentoPortal()
            empresa = session['empresa']
        elif session['empresa'] == 'portal':
            db = faturamento.FaturamentoMorumbi()
            empresa = session['empresa']

        # Buscando os dados de acordo com os filtros
        dados = db.ordens_dinheiro_relat(mes, ano)
        

        # Contexto que será passado para o template
        context = {
            'empresa': empresa,
            'mecanico': mecanico,
            'mes': mes,
            'ano': ano,
            'dados': dados
        }

        # Renderizando o template HTML
        html = render_template('relatorio_dinheiro.html', **context)

        # Criando um buffer de memória para o PDF
        pdf_buffer = BytesIO()

        # Gerando o PDF a partir do HTML
        pisa_status = pisa.CreatePDF(
            html.encode('utf-8'), dest=pdf_buffer, encoding='utf-8'
        )

        # Verificando se ocorreu algum erro na geração do PDF
        if pisa_status.err:
            return "Erro ao gerar o PDF", 500

        # Criando um nome seguro para o arquivo
        name_arquivo = f"Relatorio_{mes}_{ano}_{mecanico}".replace(" ", "_").replace("/", "-")

        # Movendo o ponteiro do buffer para o início
        pdf_buffer.seek(0)

        # Retornando o PDF como resposta Flask
        response = Response(
            pdf_buffer,
            content_type='application/pdf'
        )
        response.headers['Content-Disposition'] = f'attachment; filename="{name_arquivo}.pdf"'

        return response

    @app.route('/baixar_os', methods=['GET', 'POST'])
    def gerar_relatorio_ordens():
        # Obtendo os valores do formulário
        mes = request.form.get('mes')
        ano = request.form.get('ano')

        
        # Inicializando os objetos para acessar os dados
        if session['empresa'] == 'gr7':
            db = faturamento.Faturamento()
            empresa = session['empresa']
        elif session['empresa'] == 'portal':
            db = faturamento.FaturamentoPortal()
            empresa = session['empresa']
        elif session['empresa'] == 'gr7 morumbi':
            db = faturamento.FaturamentoMorumbi()
            empresa = session['empresa']
        

        # Buscando os dados de acordo com os filtros
        dados = db.faturamentos_ordens(mes, ano)

        # Criando o arquivo Excel
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = f"Relatório ordens - {empresa}"

        # Adicionando cabeçalhos
        colunas = [
            'Placa', 'Modelo Veículo', 'Data Orçamento', 'Data Faturamento', 'Dias Serviço', 
            'Número OS', 'Companhia', 'Valor Peças', 'Valor Serviços', 'Total OS', 
            'Valor Revitalização', 'Valor Aditivo', 'Quantidade Litros', 'Valor Fluido Sangria',
            'Valor Palheta', 'Valor Limpeza Freios', 'Valor Pastilha Para-brisa', 
            'Valor Filtro', 'Valor Pneu', 'Valor Bateria', 'Modelo Bateria', 
            'Litros Óleo Motor', 'Valor Litro Óleo', 'Marca e Tipo Óleo', 'Mecânico Serviço', 
            'Serviço Filtro', 'Valor P Meta', 'Valor em Dinheiro', 'Valor Serviço Freios', 
            'Valor Serviço Suspensão', 'Valor Serviço Injeção/Ignição', 
            'Valor Serviço Cabeçote Motor Arrefecimento', 'Valor Outros Serviços', 
            'Valor Serviços Óleos', 'Valor Serviço Transmissão', 'Observações'
        ]
        sheet.append(colunas)

        # Adicionando os dados
        for ordem_servico in dados:
            linha = [
                ordem_servico['placa'],
                ordem_servico['modelo_veiculo'],
                ordem_servico['data_orcamento'],
                ordem_servico['data_faturamento'],
                ordem_servico['dias_servico'],
                ordem_servico['numero_os'],
                ordem_servico['companhia'],
                ordem_servico['valor_pecas'],
                ordem_servico['valor_servicos'],
                ordem_servico['total_os'],
                ordem_servico['valor_revitalizacao'],
                ordem_servico['valor_aditivo'],
                ordem_servico['quantidade_litros'],
                ordem_servico['valor_fluido_sangria'],
                ordem_servico['valor_palheta'],
                ordem_servico['valor_limpeza_freios'],
                ordem_servico['valor_pastilha_parabrisa'],
                ordem_servico['valor_filtro'],
                ordem_servico['valor_pneu'],
                ordem_servico['valor_bateria'],
                ordem_servico['modelo_bateria'],
                ordem_servico['lts_oleo_motor'],
                ordem_servico['valor_lt_oleo'],
                ordem_servico['marca_e_tipo_oleo'],
                ordem_servico['mecanico_servico'],
                ordem_servico['servico_filtro'],
                ordem_servico['valor_p_meta'],
                ordem_servico['valor_em_dinheiro'],
                ordem_servico['valor_servico_freios'],
                ordem_servico['valor_servico_suspensao'],
                ordem_servico['valor_servico_injecao_ignicao'],
                ordem_servico['valor_servico_cabecote_motor_arr'],
                ordem_servico['valor_outros_servicos'],
                ordem_servico['valor_servicos_oleos'],
                ordem_servico['valor_servico_transmissao'],
                ordem_servico['obs']
            ]
            sheet.append(linha)

        # Criando um buffer de memória para o Excel
        excel_buffer = BytesIO()
        workbook.save(excel_buffer)
        excel_buffer.seek(0)

        # Criando um nome seguro para o arquivo
        nome_arquivo = f"Relatorio_{mes}_{ano}_".replace(" ", "_").replace("/", "-")

        # Retornando o Excel como resposta Flask
        response = Response(
            excel_buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response.headers['Content-Disposition'] = f'attachment; filename="{nome_arquivo}.xlsx"'

        return response
    

    @app.route('/relatorio_notas', methods=['GET', 'POST'])
    def gerar_relatorio_notas():
        # Obtendo os valores do formulário
        mes = request.form.get('mes')
        ano = request.form.get('ano')
        tipo_despesa = request.form.get('tipo_despesa')

       

        # Inicializando os objetos para acessar os dados
        if session['empresa'] == 'gr7':
            db = dados_notas.DadosGastos()
            nome_empresa = "GR7 Centro Automotivo"
        elif session['empresa'] == 'portal':
            db = dados_notas.DadosGastosPortal()
            nome_empresa = "Portal do Morumbi Centro Automotivo"
        elif session['empresa'] == 'gr7 morumbi':
            db = dados_notas.DadosGastosMorumbi()
            nome_empresa = "GR7 Morumbi Centro Automotivo"
        

        # Buscando os dados de acordo com os filtros
        dados = db.buscar_notas(mes, ano)

        # Criando o arquivo Excel
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Relatório Notas Fiscais"

        # Adicionando o "header" com nome da empresa e data/hora de geração
        data_hora_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Nome da empresa (primeira linha)
        sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=11)
        cell_empresa = sheet.cell(row=1, column=1)
        cell_empresa.value = nome_empresa
        cell_empresa.font = Font(bold=True, size=14)
        cell_empresa.alignment = Alignment(horizontal="center")

        # Data e hora de geração (segunda linha)
        sheet.merge_cells(start_row=2, start_column=1, end_row=2, end_column=11)
        cell_data_hora = sheet.cell(row=2, column=1)
        cell_data_hora.value = f"Relatório gerado em: {data_hora_geracao}"
        cell_data_hora.font = Font(italic=True, size=10)
        cell_data_hora.alignment = Alignment(horizontal="center")

        # Adicionando cabeçalhos personalizados (começam na terceira linha)
        colunas = [
            'Pago Por', 'Emitido Para', 'Status', 'Boleto', 'Número Nota', 
            'Fornecedor', 'Data Emissão', 'Valor', 'Duplicata', 'Tipo Despesa', 'Observações'
        ]

        # Estilizando o cabeçalho
        header_fill = PatternFill(start_color="FFD700", end_color="FFD700", fill_type="solid")
        header_font = Font(bold=True, color="000000", size=12)
        header_alignment = Alignment(horizontal="center", vertical="center")

        for col_num, column_title in enumerate(colunas, 1):
            cell = sheet.cell(row=3, column=col_num)
            cell.value = column_title
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment

        # Ajustando largura das colunas
        for col_num, column_title in enumerate(colunas, 1):
            sheet.column_dimensions[sheet.cell(row=3, column=col_num).column_letter].width = 20

        # Adicionando os dados (a partir da linha 4)
        for row_num, nota in enumerate(dados, 4):  # Começa na linha 4
            linha = [
                nota['pago_por'],
                nota['emitido_para'],
                nota['status'],
                nota['boleto'],
                nota['numero_nota'],
                nota['fornecedor'],
                nota['data_emissao'],
                nota['valor'],
                nota['duplicata'],
                nota['tipo_despesa'],
                nota['obs']
            ]
            for col_num, cell_value in enumerate(linha, 1):
                sheet.cell(row=row_num, column=col_num).value = cell_value

        # Criando um buffer de memória para o Excel
        excel_buffer = BytesIO()
        workbook.save(excel_buffer)
        excel_buffer.seek(0)

        # Criando um nome seguro para o arquivo
        nome_arquivo = f"Relatorio_Notas_{mes}_{ano}".replace(" ", "_").replace("/", "-")

        # Retornando o Excel como resposta Flask
        response = Response(
            excel_buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response.headers['Content-Disposition'] = f'attachment; filename="{nome_arquivo}.xlsx"'

        return response


    @app.route('/relatorio_boletos', methods=['GET', 'POST'])
    def gerar_relatorio_boletos():
        # Obtendo os valores do formulário
        mes = request.form.get('mes')
        ano = request.form.get('ano')

        # Inicializando os objetos para acessar os dados
        if session['empresa'] == 'gr7':
            db = dados_notas.DadosGastos()
            nome_empresa = "GR7 Centro Automotivo"
        elif session['empresa'] == 'portal':
            db = dados_notas.DadosGastosPortal()
            nome_empresa = "Portal do Morumbi Centro Automotivo"
        elif session['empresa'] == 'gr7 morumbi':
            db = dados_notas.DadosGastosMorumbi()
            nome_empresa = "GR7 Morumbi Centro Automotivo"

        # Buscando os dados de acordo com os filtros
        boletos = db.buscar_boletos(mes, ano)

        # Criando o arquivo Excel
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Relatório de boletos"

        # Adicionando o "header" com nome da empresa e data/hora de geração
        
        data_hora_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Nome da empresa (primeira linha)
        sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=5)
        cell_empresa = sheet.cell(row=1, column=1)
        cell_empresa.value = nome_empresa
        cell_empresa.font = Font(bold=True, size=14)
        cell_empresa.alignment = Alignment(horizontal="center")

        # Data e hora de geração (segunda linha)
        sheet.merge_cells(start_row=2, start_column=1, end_row=2, end_column=5)
        cell_data_hora = sheet.cell(row=2, column=1)
        cell_data_hora.value = f"Relatório gerado em: {data_hora_geracao}"
        cell_data_hora.font = Font(italic=True, size=10)
        cell_data_hora.alignment = Alignment(horizontal="center")

        # Adicionando cabeçalhos personalizados (começam na terceira linha)
        colunas = ['Número Nota', 'Notas', 'Fornecedor', 'Data Vencimento', 'Valor']

        # Estilizando o cabeçalho
        header_fill = PatternFill(start_color="FFD700", end_color="FFD700", fill_type="solid")
        header_font = Font(bold=True, color="000000", size=12)
        header_alignment = Alignment(horizontal="center", vertical="center")

        for col_num, column_title in enumerate(colunas, 1):
            cell = sheet.cell(row=3, column=col_num)
            cell.value = column_title
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment

        # Ajustando largura das colunas
        for col_num, column_title in enumerate(colunas, 1):
            sheet.column_dimensions[sheet.cell(row=3, column=col_num).column_letter].width = 20

        # Adicionando os dados (a partir da linha 4)
        for row_num, boleto in enumerate(boletos, 4):  # Começa na linha 4
            linha = [
                boleto['num_nota'],
                boleto['notas'],
                boleto['fornecedor'],
                boleto['data_vencimento'],
                boleto['valor']
            ]
            for col_num, cell_value in enumerate(linha, 1):
                sheet.cell(row=row_num, column=col_num).value = cell_value

        # Criando um buffer de memória para o Excel
        excel_buffer = BytesIO()
        workbook.save(excel_buffer)
        excel_buffer.seek(0)

        # Criando um nome seguro para o arquivo
        nome_arquivo = f"Relatorio_Boletos_{mes}_{ano}".replace(" ", "_").replace("/", "-")

        # Retornando o Excel como resposta Flask
        response = Response(
            excel_buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response.headers['Content-Disposition'] = f'attachment; filename="{nome_arquivo}.xlsx"'

        return response
    
    @app.route('/gerencial')
    def tela_gerencial():
        funcionarios = [
            {'id': 1, 'nome': 'Funcionário 1'},
            {'id': 2, 'nome': 'Funcionário 2'},
            # Adicione mais funcionários conforme necessário
        ]
        return render_template('gerencial.html', empresa="Oficina", funcionarios=funcionarios)

    @app.route('/dados-loja/<loja>')
    def dados_loja(loja):
        ano = request.args.get('ano', default=2025, type=int)
        
       
        if loja == 'GR7':     
            db = conection.Database() 
        elif loja == 'Portal': 
            conection.DatabasePortal()
        elif loja == 'GR7 Morumbi':
            conection. DatabaseMorumbi()
        
        

        faturamento = db.faturamento_loja_ano(loja, ano)
        
        

        return jsonify(faturamento)

    @app.route('/funcionarios-por-loja/<loja>')
    def funcionarios_por_loja(loja):
       
        if loja == 'GR7':
            db = conection.Database() 
        elif loja == "Portal": 
            db = conection.DatabasePortal()
        
        
        

        funcionarios = db.funcionarios_por_loja(loja)
        
        

        return jsonify(funcionarios)

    @app.route('/dados-funcionario/<mecanico>')
    def dados_funcionario(mecanico):
        loja = request.args.get('loja', default="GR7", type=str)
        ano = request.args.get('ano', default=2024, type=int)

        if loja == 'GR7':
            db = conection.Database() 
        elif loja == "Portal":
            db = conection.DatabasePortal()
        elif loja == "Morumbi":
            db = conection.DatabaseMorumbi()
        
        

        desempenho = db.desempenho_funcionario_ano(loja, mecanico, ano)
        
      

        return jsonify(desempenho)
