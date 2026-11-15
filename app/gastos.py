from datetime import datetime
from functools import wraps

from flask import flash, jsonify, redirect, render_template, request, session

from app import app
from database import gastos_db
from services import cadastrar_duplicata as duplicata_service
from services import cadastrar_notas, dados_notas, utills


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if 'usuario' not in session:
            flash('Faça login para continuar.')
            return redirect('/')
        return view(*args, **kwargs)
    return wrapped


def _dados_gastos():
    return dados_notas.DadosGastos()


def _mes_nome(codigo):
    nomes = (
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    )
    indice = int(codigo) - 1
    return nomes[indice] if 0 <= indice < 12 else ''


@app.route('/gastos/cadastros/notas')
@login_required
def tela_cadastro_notas():
    servico = utills.Utills()
    return render_template(
        'cadastrar_notas.html',
        empresa=session['empresa'],
        fornecedores=servico.fornecedores(),
        despesas=servico.despesas(),
        emitido_para=servico.emitido_para()
    )


@app.route('/gastos/cadastros/notas-cadastrar-nota', methods=['POST'])
@login_required
def cadastrar_nota():
    usuario = session['usuario']
    dados = {
        'empresa': session['empresa'],
        'emitido_para': request.form.get('emitido-para', ''),
        'status': request.form.get('status', ''),
        'boleto': request.form.get('boleto', 'Não'),
        'nota': request.form.get('nota', ''),
        'duplicata': request.form.get('duplicata', ''),
        'fornecedor': request.form.get('fornecedor', ''),
        'emissao': request.form.get('emissao', ''),
        'valor': request.form.get('valor', '0'),
        'despesa': request.form.get('despesa', ''),
        'sub': request.form.get('subcategoria', ''),
        'usuario': usuario,
        'obs': request.form.get('obs', '')
    }
    cadastrar_notas.Notas().cadastrar(dados, usuario)
    if dados['boleto'] == 'Sim':
        return render_template(
            'cadastrar_boleto.html',
            empresa=session['empresa'],
            num_nota=dados['nota'],
            fornecedor=dados['fornecedor']
        )
    flash('Nota cadastrada.')
    return redirect('/gastos/cadastros/notas')


@app.route('/gastos/cadatro/duplicata')
@app.route('/gastos/cadastros/duplicatas')
@login_required
def tela_duplicatas():
    return render_template('cadastrar_duplicatas.html', empresa=session['empresa'])


@app.route('/cadastrar_boletos', methods=['POST'])
@login_required
def cadastrar_boletos():
    numero_nota = request.form.get('num_nota', '')
    fornecedor = request.form.get('fornecedor', '')
    try:
        quantidade = int(request.form.get('numParcelas', '0'))
    except ValueError:
        return 'Quantidade de parcelas inválida.', 400

    servico = cadastrar_notas.Boletos()
    for indice in range(1, quantidade + 1):
        servico.cadastrar({
            'num_nota': numero_nota,
            'notas': '',
            'fornecedor': fornecedor,
            'vencimento': request.form.get(f'dataVencimento{indice}', ''),
            'valor': request.form.get(f'valorParcela{indice}', '0')
        })
    flash('Boletos cadastrados com sucesso!')
    return redirect('/gastos/cadastros/notas')


@app.route('/api/nota/<numero_nota>')
@login_required
def get_nota(numero_nota):
    nota = _dados_gastos().nota_por_numero(numero_nota)
    return jsonify(nota) if nota else (jsonify({'error': 'Nota não encontrada'}), 404)


@app.route('/cadastrar_duplicata', methods=['POST'])
@login_required
def cadastrar_duplicata():
    numeros = request.form.getlist('numeroNota[]')
    fornecedores = request.form.getlist('fornecedorNota[]')
    emissoes = request.form.getlist('dataEmissaoNota[]')
    valores = request.form.getlist('valorNota[]')
    notas = [
        {'numero': numero, 'fornecedor': fornecedores[i], 'data_emissao': emissoes[i], 'valor': valores[i]}
        for i, numero in enumerate(numeros)
        if i < len(fornecedores) and i < len(emissoes) and i < len(valores)
    ]
    try:
        quantidade = int(request.form.get('quantidadeParcelas', '0'))
    except ValueError:
        return 'Quantidade de parcelas inválida.', 400
    parcelas = [
        {
            'valor': request.form.get(f'valorParcela{i}', '0'),
            'vencimento': request.form.get(f'vencimentoParcela{i}', '')
        }
        for i in range(1, quantidade + 1)
    ]
    duplicata_service.Boletos().cadastrar_duplicatas({
        'numero_duplicata': request.form.get('numeroDuplicata', ''),
        'notas': notas,
        'parcelas': parcelas
    })
    return render_template('resposta_cadastro.html', rota='/gastos/cadastros/duplicatas')


@app.route('/gastos', methods=['GET', 'POST'])
@login_required
def tela_gastos():
    empresa = session['empresa']
    if empresa == 2 and session.get('permission') != 'ADMIN':
        return render_template('resposta_permissao.html', empresa=empresa)
    if empresa not in (1, 2, 3):
        return 'Empresa não suportada.', 400

    session['link'] = '/gastos'
    agora = datetime.now()
    mes_atual, ano_atual, dia_atual = agora.strftime('%m'), agora.strftime('%Y'), agora.strftime('%d')
    mes = request.form.get('mes', mes_atual)
    ano = request.form.get('ano', ano_atual)
    data = request.form.get('dia', agora.strftime('%Y-%m-%d'))
    dia_consulta = data[8:10] if len(data) >= 10 else dia_atual
    servico = _dados_gastos()
    return render_template(
        'gastos.html',
        anos=[str(valor) for valor in range(2024, agora.year + 2)],
        meses=[(f'{i:02}', _mes_nome(i)) for i in range(1, 13)],
        tipo_despesa=servico.dados_gastos(mes, ano),
        empresa=empresa,
        boletos=servico.boletos_do_dia(dia_consulta, mes, ano),
        valor_gastos=servico.valor_gastos(mes, ano),
        valor_a_pagar=servico.valor_a_pagar(dia_consulta, mes, ano),
        mes_escolhido=_mes_nome(mes),
        ano_escolhido=ano,
        dia=f'{ano}-{mes}-{dia_consulta}'
    )


@app.route('/atualizar', methods=['POST'])
@login_required
def atualizar_boletos():
    mes = request.form.get('mes')
    ano = request.form.get('ano')
    if not mes or not ano:
        return jsonify({'error': 'Parâmetros inválidos.'}), 400
    dia = request.form.get('dia') or datetime.now().strftime('%d')
    if len(dia) >= 10:
        dia = dia[8:10]
    return jsonify({'boletos': _dados_gastos().boletos_do_dia(dia, mes, ano)})


@app.route('/cadastros/despesas')
@login_required
def tela_cadastro_despesas():
    return render_template('cadastro_despesa.html', empresa=session['empresa'])


@app.route('/cadastros/despesas-cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar_despesa():
    if request.method == 'POST':
        _dados_gastos().cadastrar_despesa(request.form.get('despesa', '').strip())
        flash('Despesa cadastrada.')
        return redirect('/cadastros/despesas')
    return redirect('/cadastros/despesas')


@app.route('/consultar_notas', methods=['GET', 'POST'])
@login_required
def consultar_notas():
    servico = _dados_gastos()
    util = utills.Utills()
    filtros = {
        nome: (request.form.get(nome) if request.method == 'POST' else request.args.get(nome))
        for nome in ('data_inicio', 'data_fim', 'fornecedor', 'despesa', 'obs')
    }
    if any(filtros.values()):
        notas = servico.filtrar_notas(**filtros)
        valor = servico.filtrar_notas_valor(**filtros)
    else:
        notas = servico.todas_as_notas_mes(str(datetime.now().month), str(datetime.now().year))
        valor = servico.valor_nota()
    session['link'] = '/consultar_notas'
    return render_template(
        'consultar_notas.html', empresa=session['empresa'], fornecedores=util.fornecedores(),
        despesas=util.despesas(), notas=notas, valor=valor, **filtros
    )


@app.route('/dados_boletos/<num_nota>', methods=['GET', 'POST'])
@login_required
def dados_boletos(num_nota):
    servico = _dados_gastos()
    boletos = servico.todos_os_boletos_por_nota(num_nota)
    return render_template(
        'dados_boletos.html', empresa=session['empresa'], boletos=boletos,
        valor=servico.valor_gastos_boletos_valor(num_nota), quantidade=len(boletos),
        num_nota=num_nota, link=session.get('link', '/consultar_boletos'),
        nota=servico.nota_por_numero(num_nota)
    )


@app.route('/consultar_boletos', methods=['GET', 'POST'])
@login_required
def consultar_boletos():
    servico = _dados_gastos()
    util = utills.Utills()
    if request.method == 'POST':
        inicio = request.form.get('data_inicio')
        fim = request.form.get('data_fim')
        fornecedor = request.form.get('fornecedor')
        boletos = servico.filtrar_boletos(inicio, fim, fornecedor)
        valor = servico.filtrar_boletos_valor(inicio, fim, fornecedor)
    else:
        boletos = servico.todos_os_boletos()
        valor = servico.valor_boleto()
    session['link'] = '/consultar_boletos'
    return render_template(
        'consultar_boletos.html', empresa=session['empresa'], fornecedores=util.fornecedores(),
        boletos=boletos, valor=valor
    )


@app.route('/api/subcategorias')
@login_required
def get_subcategorias():
    despesa = request.args.get('despesa')
    if not despesa:
        return jsonify([])
    dados = gastos_db.GastosDataBase().get_subcategorias(despesa)
    return jsonify([item[3] for item in dados])


@app.route('/cadastros')
@login_required
def cadastros():
    return render_template('cadastros.html', empresa=session['empresa'])


@app.route('/cadastros/fornecedor')
@login_required
def tela_fornecedor():
    return render_template('cadastro_fornecedor.html', empresa=session['empresa'])


@app.route('/fornecedor_cadastrar', methods=['POST'])
@login_required
def fornecedor_cadastrar():
    utills.Utills().cadastrar_fornecedor({
        'cnpj': request.form.get('cnpj', '').strip(),
        'nome_empresa': request.form.get('nome_empresa', '').strip()
    })
    flash('Fornecedor cadastrado.')
    return redirect('/cadastros/fornecedor')


@app.route('/cadastros/companhias')
@login_required
def tela_companhias():
    return render_template('cadastrar_companhias.html', empresa=session['empresa'])


@app.route('/cadastros/companhia-cadastrar', methods=['POST'])
@login_required
def companhia_cadastrar():
    _dados_gastos().cadastrar_companhia({'depesa': request.form.get('despesa', '').strip()})
    flash('Companhia cadastrada.')
    return redirect('/cadastros/companhias')


@app.route('/cadastros/funcionarios')
@login_required
def tela_funcionarios():
    return render_template('cadastrar_funcionarios.html', empresa=session['empresa'])


@app.route('/funcionario-cadastrar', methods=['POST'])
@login_required
def funcionario_cadastrar():
    _dados_gastos().cadastrar_funcionario({'funcionario': request.form.get('funcionario', '').strip()})
    flash('Funcionário cadastrado.')
    return redirect('/cadastros/funcionarios')


@app.route('/cadastros/baterias')
@login_required
def tela_baterias():
    return render_template('cadastrar_bateria.html', empresa=session['empresa'])


@app.route('/bateria-cadastrar', methods=['POST'])
@login_required
def bateria_cadastrar():
    _dados_gastos().cadastrar_baterias({'bateria': request.form.get('bateria', '').strip()})
    flash('Bateria cadastrada.')
    return redirect('/cadastros/baterias')


@app.route('/cadastros/oleos')
@login_required
def tela_oleos():
    return render_template('cadastrar_oleo.html', empresa=session['empresa'])


@app.route('/oleo-cadastrar', methods=['POST'])
@login_required
def oleo_cadastrar():
    _dados_gastos().cadastrar_oleo({'oleo': request.form.get('oleo', '').strip()})
    flash('Óleo cadastrado.')
    return redirect('/cadastros/oleos')
