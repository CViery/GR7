from app import app
from flask import request, redirect, render_template, flash, session, jsonify
from services import login, cadastrar_notas, cadastrar_duplicata, dados_notas
from datetime import datetime

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
            print(usuario, senha, empresa)
            db = login.Login()
            auten = db.login(usuario.upper(), senha)
            print(auten)
            if auten:
                session['usuario'] = usuario
                session['empresa'] = empresa
                return render_template('index.html', empresa=empresa)
            else:
                flash('Usuário ou senha incorretos.')
                return redirect('/')
        except Exception as e:
            print(f"Erro durante autenticação: {e}")
            flash('Ocorreu um erro. Tente novamente.')
            return redirect('/')

    @app.route('/logout')
    def logout():
        session.pop('usuario', None)
        session.pop('empresa', None)
        flash('Você saiu da sessão com sucesso.')
        return redirect('/')

    @app.route('/gastos/cadastros/notas')
    def tela_cadastro_notas():
        if 'usuario' in session:
            empresa = session['empresa']
            return render_template('cadastrar_notas.html', empresa=empresa)
        else:
            print('usario não está logado')
            return redirect('/')
    
    @app.route('/gastos/cadastros/notas-cadastrar-nota', methods=['POST'])
    def cadastrar_nota():
        enviar = cadastrar_notas.Notas()
        dados = {
            'emitido_para' : request.form['emitido-para'],
            'status' : request.form['status'],
            'boleto' : request.form['boleto'],
            'nota' : request.form['nota'],
            'duplicata' : request.form['duplicata'],
            'fornecedor' : request.form['fornecedor'],
            'emissao' : request.form['emissao'],
            'valor' : request.form['valor'],
            'despesa' : request.form['despesa']
        }
        enviar.cadastrar(dados)
        if dados['boleto'] == 'Sim':
            return render_template('cadastrar_boleto.html', empresa=session['empresa'], num_nota=dados['nota'], fornecedor=dados['fornecedor'])
        else:
            return render_template('index.html', empresa=session['empresa'], show_alert=True)
        
    # Aqui você pode processar os dados como desejar
    # Por exemplo, você pode salvá-los em um banco de dados
        return 'Nota cadastrada com sucesso!'
    
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
            numero_nota = request.form['num_nota']
            fornecedor = request.form['fornecedor']
            num_parcelas = int(request.form['numParcelas'])
            parcelas = []
            for i in range(1, num_parcelas + 1):
                valor = request.form[f'valorParcela{i}']
                data_vencimento = request.form[f'dataVencimento{i}']
                parcelas.append({'valor': valor, 'data_vencimento': data_vencimento})

                # Aqui você pode salvar os dados no banco de dados ou processá-los conforme necessário
            """ print(f'Número da Nota: {numero_nota}')
            print(f'Fornecedor: {fornecedor}')
            print(f'Parcelas: {parcelas}') """
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

                # Redireciona para uma página de confirmação ou volta para a página inicial
            return 'Boleto Salvo'
        except Exception as e:
            print(f'Erro: {e}')
            return "Erro no processamento dos dados", 400

    
    

    @app.route('/api/nota/<numero_nota>', methods=['GET'])
    def get_nota(numero_nota):
        notas = {
        '12345': {'fornecedor': 'Fornecedor A', 'data_emissao': '01/06/2024', 'valor': '1000.00'},
        '67890': {'fornecedor': 'Fornecedor B', 'data_emissao': '05/06/2024', 'valor': '1500.00'},
        # Adicione mais notas conforme necessário
    }
        nota = notas.get(numero_nota)
        if nota:
            return jsonify(nota)
        else:
            return jsonify({'error': 'Nota não encontrada'}), 404

    @app.route('/cadastrar_duplicata', methods=['POST'])
    def cadastrar_duplicata():
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
        # ...

        return 'Duplicata cadastrada com sucesso!', 200

    
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
            # Se o formulário foi enviado
            if request.method == 'POST':
                dados_tipos = db.despesas('06', '2024')
                data = request.form['dia']
                dia = data[8:]
                mes = data[5:7]
                print(dia)
                print(mes)
                ano = data[:4]
                print(ano)
                boletos = db.boletos_do_dia(dia,mes,ano)
                return render_template('gastos.html',meses = meses,tipo_despesa = dados_tipos,empresa=empresa, boletos=boletos)
            else:
                # Caso contrário, use a data atual
                now = datetime.now()
                dia = now.strftime('%d')
                mes = now.strftime('%m')
                ano = now.strftime('%Y')
                print(dia)
                print(mes)
                print(ano)
                data = datetime.today()
                dados_tipos = db.despesas(data.month, data.year)
                boletos = db.boletos_do_dia(dia,mes,ano)
                return render_template('gastos.html',meses = meses,tipo_despesa = dados_tipos,empresa=empresa, boletos=boletos)
        else:
            print('Usuário não está logado')
            return redirect('/')
    
    @app.route('/atualizar', methods=['POST'])
    def atualizar_boletos():
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
            despesa = request.form['despesa']
            db = dados_notas.DadosGastos()
            db.cadastrar_despesa(despesa)
            return 'Despesa cadastrada'
        else:
            return 'erro aqui'
