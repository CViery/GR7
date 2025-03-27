from flask import render_template, session
from services import  faturamento, utills
from datetime import datetime

def render_gr7_admin(usuario):
    utils = utills.Utills()
    db = faturamento.Faturamento()
    now = datetime.now()
    mes_dados = now.strftime('%m')
    ano_dados = now.strftime('%Y')

    # Obter os dados de faturamento
    dados_faturamento = {
        'faturamento': db.faturamento_total_mes(mes_dados, ano_dados),
        'faturamento_meta': db.faturamento_meta_mes(mes_dados, ano_dados),
        'faturamento_pecas': utils.faturamento_pecas(mes_dados, ano_dados),
        'faturamento_servicos': utils.faturamento_servicos(mes_dados, ano_dados),
        'primeira_meta': utils.primeira_meta(mes_dados, ano_dados),
        'segunda_meta': utils.segunda_meta(mes_dados, ano_dados),
        'valor_gastos': utils.gastos(mes_dados, ano_dados),
        'porcentagem_faturamento': utils.porcentagem_faturamento(mes_dados, ano_dados),
        'gastos_pecas': utils.gastos_pecas(mes_dados, ano_dados),
        'porcentagem_pecas': utils.porcentagem_gastos_pecas(mes_dados, ano_dados),
        'ticket': utils.ticket(mes_dados, ano_dados),
        'passagens': utils.passagens(mes_dados, ano_dados)
    }
    print(dados_faturamento)
    return render_template('index.html', empresa=session['empresa'], user=usuario, **dados_faturamento)


def render_portal_admin(usuario):
    utils = utills.Utills_portal()
    db = faturamento.FaturamentoPortal()
    now = datetime.now()
    mes_dados = now.strftime('%m')
    ano_dados = now.strftime('%Y')

    # Obter os dados de faturamento
    dados_faturamento = {
        'faturamento': db.faturamento_total_mes(mes_dados, ano_dados),
        'faturamento_meta': db.faturamento_meta_mes(mes_dados, ano_dados),
        'faturamento_pecas': utils.faturamento_pecas(mes_dados, ano_dados),
        'faturamento_servicos': utils.faturamento_servicos(mes_dados, ano_dados),
        'primeira_meta': utils.primeira_meta(mes_dados, ano_dados),
        'segunda_meta': utils.segunda_meta(mes_dados, ano_dados),
        'valor_gastos': utils.gastos(mes_dados, ano_dados),
        'porcentagem_faturamento': utils.porcentagem_faturamento(mes_dados, ano_dados),
        'gastos_pecas': utils.gastos_pecas(mes_dados, ano_dados),
        'porcentagem_pecas': utils.porcentagem_gastos_pecas(mes_dados, ano_dados),
        'ticket': utils.ticket(mes_dados, ano_dados),
        'passagens': utils.passagens(mes_dados, ano_dados)
    }

    return render_template('index_portal_admin.html', empresa=session['empresa'], user=usuario, **dados_faturamento)


def render_portal_normal(usuario):
    utils = utills.Utills_portal()
    db = faturamento.FaturamentoPortal()
    now = datetime.now()
    mes_dados = now.strftime('%m')
    ano_dados = now.strftime('%Y')

    # Obter os dados de faturamento
    dados_faturamento = {
        'faturamento': db.faturamento_total_mes(mes_dados, ano_dados),
        'faturamento_meta': db.faturamento_meta_mes(mes_dados, ano_dados),
        'primeira_meta': utils.primeira_meta(mes_dados, ano_dados),
        'segunda_meta': utils.segunda_meta(mes_dados, ano_dados),
    }

    return render_template('index_portal_normal.html', empresa=session['empresa'], user=usuario, **dados_faturamento)