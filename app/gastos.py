@app.route('/gastos/cadastros/notas')
    def tela_cadastro_notas():
        if 'usuario' in session:
            db = utills.Utills()
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
        if empresa == 1:
            db = dados_notas.DadosGastos()
        if empresa == 2:
            if session.get('permission') == 'ADMIN':
                db = dados_notas.DadosGastosPortal()
            else:
                return render_template('resposta_permissao.html', empresa=empresa)
        if empresa == 3:
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
        if empresa == 1:
            db = dados_notas.DadosGastos()
        if empresa == 2:
            db = dados_notas.DadosGastosPortal()
        if empresa == 3:
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
