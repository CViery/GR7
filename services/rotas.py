from flask import render_template, session
from services import faturamento, utills
from datetime import datetime


def calcular_meta(faturamento_liquido, valor_meta):
    try:
        atingido = float(str(faturamento_liquido).replace('R$', '').replace('.', '').replace(',', '.').strip())
    except Exception:
        atingido = 0

    restante = valor_meta - atingido
    if restante < 0:
        restante = 0

    percentual = (atingido / valor_meta) * 100 if valor_meta > 0 else 0
    if percentual > 100:
        percentual = 100

    return {
        'atingido': atingido,
        'restante': restante,
        'percentual': round(percentual, 2)
    }


def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


def moeda_para_float(valor):
    try:
        return float(
            str(valor)
            .replace('R$', '')
            .replace('.', '')
            .replace(',', '.')
            .strip()
        )
    except Exception:
        return 0


def _montar_rankings_e_grafico(db, mes_dados, ano_dados, empresa=None):
    """Monta Top Mecânicos, Top Companhias, Top Serviços e dados do gráfico diário para qualquer unidade."""
    faturamento_mecanicos = db.faturamento_mecanico(mes_dados, ano_dados) or []
    faturamento_cias = db.faturamento_companhia(mes_dados, ano_dados) or []
    faturamento_servico = db.faturamento_servico(mes_dados, ano_dados) or []

    if empresa == 2:  # Portal do Morumbi
        nomes_servicos = {
            'revitalizacao': 'REVITALIZAÇÃO',
            'aditivo': 'AR CONDICIONADO',
            'ar_condicionado': 'AR CONDICIONADO',
            'fluido_sangria': 'LAVAGEM',
            'palheta': 'ALTERNADOR / MOTOR DE ARRANQUE',
            'limpeza_freios': 'FUNILARIA',
            'funilaria': 'FUNILARIA',
            'detergente_parabrisa': 'DETERGENTE PARABRISA',
            'filtro': 'FILTRO E HIGIENIZAÇÃO',
            'pneus': 'PNEUS',
            'bateria': 'BATERIA'
        }
    else:  # Santo Amaro (1) e Vila Andrade / Morumbi (3)
        nomes_servicos = {
            'revitalizacao': 'REVITALIZAÇÃO',
            'aditivo': 'ADITIVO',
            'fluido_sangria': 'FLUIDO E SANGRIA',
            'palheta': 'PALHETA',
            'limpeza_freios': 'LIMPEZA DE FREIOS',
            'detergente_parabrisa': 'DETERGENTE PARABRISA',
            'filtro': 'FILTRO',
            'pneus': 'PNEUS',
            'bateria': 'BATERIA',
            'terceiros': 'TERCEIROS'
        }

    top_servicos = sorted(
        faturamento_servico,
        key=lambda item: moeda_para_float(item[1]),
        reverse=True
    )[:5]

    top_servicos_dashboard = [
        {
            'nome': nomes_servicos.get(servico[0], str(servico[0]).upper()),
            'valor': servico[1]
        }
        for servico in top_servicos
    ]

    top_mecanicos = [
        {
            'nome': mecanico[0],
            'valor': mecanico[1]
        }
        for mecanico in sorted(
            faturamento_mecanicos,
            key=lambda item: moeda_para_float(item[1]),
            reverse=True
        )[:5]
    ]

    top_companhias = [
        {
            'nome': companhia[0],
            'valor': companhia[1]
        }
        for companhia in sorted(
            faturamento_cias,
            key=lambda item: moeda_para_float(item[1]),
            reverse=True
        )[:5]
    ]

    faturamento_diario = db.faturamento_diario_mes(mes_dados, ano_dados) or []
    dias_faturamento = []
    valores_bruto = []
    valores_liquido = []

    for dia, bruto, liquido in faturamento_diario:
        dias_faturamento.append(str(dia))
        valores_bruto.append(float(bruto or 0))
        valores_liquido.append(float(liquido or 0))

    return {
        'dias_faturamento': dias_faturamento,
        'valores_faturamento': valores_bruto,
        'valores_bruto': valores_bruto,
        'valores_liquido': valores_liquido,
        'top_mecanicos': top_mecanicos,
        'top_companhias': top_companhias,
        'top_servicos': top_servicos_dashboard,
    }

def render_gr7_admin(usuario):
    utils = utills.Utills()
    db = faturamento.Faturamento()

    now = datetime.now()
    mes_dados = now.strftime('%m')
    ano_dados = now.strftime('%Y')

    faturamento_liquido = db.faturamento_meta_mes(mes_dados, ano_dados)
    meta_1 = calcular_meta(faturamento_liquido, 180000)
    meta_2 = calcular_meta(faturamento_liquido, 220000)

    dados_faturamento = {
        'faturamento': db.faturamento_total_mes(mes_dados, ano_dados),
        'faturamento_meta': faturamento_liquido,
        'faturamento_pecas': utils.faturamento_pecas(mes_dados, ano_dados),
        'faturamento_servicos': utils.faturamento_servicos(mes_dados, ano_dados),
        'primeira_meta': formatar_moeda(meta_1['restante']),
        'segunda_meta': formatar_moeda(meta_2['restante']),
        'valor_atingido_meta_1': formatar_moeda(meta_1['atingido']),
        'valor_atingido_meta_2': formatar_moeda(meta_2['atingido']),
        'valor_restante_meta_1': formatar_moeda(meta_1['restante']),
        'valor_restante_meta_2': formatar_moeda(meta_2['restante']),
        'percentual_meta_1': meta_1['percentual'],
        'percentual_meta_2': meta_2['percentual'],
        'valor_gastos': utils.gastos(mes_dados, ano_dados),
        'porcentagem_faturamento': utils.porcentagem_faturamento(mes_dados, ano_dados),
        'gastos_pecas': utils.gastos_pecas(mes_dados, ano_dados),
        'porcentagem_pecas': utils.porcentagem_gastos_pecas(mes_dados, ano_dados),
        'ticket': utils.ticket(mes_dados, ano_dados),
        'passagens': utils.passagens(mes_dados, ano_dados),
        **_montar_rankings_e_grafico(db, mes_dados, ano_dados),
    }

    return render_template(
        'index.html',
        empresa=session['empresa'],
        user=usuario,
        **dados_faturamento
    )


def render_portal_admin(usuario):
    utils = utills.Utills()
    db = faturamento.Faturamento()
    now = datetime.now()
    mes_dados = now.strftime('%m')
    ano_dados = now.strftime('%Y')

    faturamento_liquido = db.faturamento_meta_mes(mes_dados, ano_dados)
    meta_1 = calcular_meta(faturamento_liquido, 170000)

    dados_faturamento = {
        'faturamento': db.faturamento_total_mes(mes_dados, ano_dados),
        'faturamento_meta': faturamento_liquido,
        'faturamento_pecas': utils.faturamento_pecas(mes_dados, ano_dados),
        'faturamento_servicos': utils.faturamento_servicos(mes_dados, ano_dados),
        'primeira_meta': formatar_moeda(meta_1['restante']),
        'valor_atingido_meta_1': formatar_moeda(meta_1['atingido']),
        'valor_restante_meta_1': formatar_moeda(meta_1['restante']),
        'percentual_meta_1': meta_1['percentual'],
        'valor_gastos': utils.gastos(mes_dados, ano_dados),
        'porcentagem_faturamento': utils.porcentagem_faturamento(mes_dados, ano_dados),
        'gastos_pecas': utils.gastos_pecas(mes_dados, ano_dados),
        'porcentagem_pecas': utils.porcentagem_gastos_pecas(mes_dados, ano_dados),
        'ticket': utils.ticket(mes_dados, ano_dados),
        'passagens': utils.passagens(mes_dados, ano_dados),
        **_montar_rankings_e_grafico(db, mes_dados, ano_dados, empresa=2),
    }

    return render_template(
        'index_portal_admin.html',
        empresa=session['empresa'],
        user=usuario,
        **dados_faturamento
    )


def render_portal_normal(usuario):
    return render_portal_admin(usuario)


def render_gr7_morumbi_admin(usuario):
    utils = utills.Utills()
    db = faturamento.Faturamento()
    now = datetime.now()
    mes_dados = now.strftime('%m')
    ano_dados = now.strftime('%Y')

    faturamento_liquido = db.faturamento_meta_mes(mes_dados, ano_dados)
    meta_1 = calcular_meta(faturamento_liquido, 180000)
    meta_2 = calcular_meta(faturamento_liquido, 220000)

    dados_faturamento = {
        'faturamento': db.faturamento_total_mes(mes_dados, ano_dados),
        'faturamento_meta': faturamento_liquido,
        'faturamento_pecas': utils.faturamento_pecas(mes_dados, ano_dados),
        'faturamento_servicos': utils.faturamento_servicos(mes_dados, ano_dados),
        'primeira_meta': formatar_moeda(meta_1['restante']),
        'segunda_meta': formatar_moeda(meta_2['restante']),
        'valor_atingido_meta_1': formatar_moeda(meta_1['atingido']),
        'valor_atingido_meta_2': formatar_moeda(meta_2['atingido']),
        'valor_restante_meta_1': formatar_moeda(meta_1['restante']),
        'valor_restante_meta_2': formatar_moeda(meta_2['restante']),
        'percentual_meta_1': meta_1['percentual'],
        'percentual_meta_2': meta_2['percentual'],
        'valor_gastos': utils.gastos(mes_dados, ano_dados),
        'porcentagem_faturamento': utils.porcentagem_faturamento(mes_dados, ano_dados),
        'gastos_pecas': utils.gastos_pecas(mes_dados, ano_dados),
        'porcentagem_pecas': utils.porcentagem_gastos_pecas(mes_dados, ano_dados),
        'ticket': utils.ticket(mes_dados, ano_dados),
        'passagens': utils.passagens(mes_dados, ano_dados),
        **_montar_rankings_e_grafico(db, mes_dados, ano_dados),
    }

    return render_template(
        'index_morumbi_admin.html',
        empresa=session['empresa'],
        user=usuario,
        **dados_faturamento
    )


def render_gr7_morumbi_normal(usuario):
    return render_gr7_morumbi_admin(usuario)


def render_gr7_modulo_admin(usuario):
    utils = utills.Utills()
    db = faturamento.Faturamento()
    now = datetime.now()
    mes_dados = now.strftime('%m')
    ano_dados = now.strftime('%Y')

    dados = {
        'orcamentos_abertos': db.quantidade_os('APROVADO'),
        'orcamentos_andamento': db.quantidade_os('EM_SERVICO'),
        'vendas_mes': db.vendas_mes(mes_dados, ano_dados),
        'custo_mes': 'db.custo_mes(mes_dados, ano_dados)',
        'ultimas_vendas': db.ultimas_movimentacoes(),
    }

    return render_template(
        'index_modulos.html',
        empresa=session['empresa'],
        user=usuario,
        **dados
    )


def render_gr7_modulo_normal(usuario):
    utils = utills.Utills()
    db = faturamento.Faturamento()
    now = datetime.now()
    mes_dados = now.strftime('%m')
    ano_dados = now.strftime('%Y')

    dados = {
        'orcamentos_abertos': db.quantidade_os('ABERTO'),
        'orcamentos_andamento': db.quantidade_os('ANDAMENTO'),
        'vendas_mes': db.vendas_mes(mes_dados, ano_dados),
        'custo_mes': db.custo_mes(mes_dados, ano_dados),
        'ultimas_vendas': db.ultimas_movimentacoes(),
    }

    return render_template(
        'index_modulos.html',
        empresa=session['empresa'],
        user=usuario,
        **dados
    )