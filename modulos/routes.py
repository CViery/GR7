from datetime import datetime
from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from sqlalchemy import func, or_

from .extensions import db
from .models import CategoriaGasto, Cliente, Faturamento, Gasto, ItemVenda, ProdutoServico, Venda


bp = Blueprint("modulos", __name__, url_prefix="/modulos", template_folder="templates", static_folder="static")


@bp.before_request
def proteger_area_modulos():
    if "usuario" not in session:
        flash("Faça login para acessar o sistema.", "warning")
        return redirect(url_for("show_login"))
    if session.get("empresa") != 4:
        flash("Selecione a filial GR7 Módulos para acessar esta área.", "warning")
        return redirect(url_for("home"))
    return None


def d(value):
    try:
        return Decimal(str(value or 0))
    except (TypeError, ValueError, ArithmeticError):
        return Decimal("0")


@bp.app_template_filter("brl")
def brl(value):
    number = float(value or 0)
    return f"R$ {number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


@bp.route("/")
def dashboard():
    abertas = Venda.query.filter(Venda.status.in_(["ORCAMENTO", "APROVADO"])).count()
    andamento = Venda.query.filter(Venda.status == "EM_SERVICO").count()
    today = datetime.now().date()
    month_start = today.replace(day=1)
    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)
    faturado_mes = db.session.query(
        func.coalesce(func.sum(Faturamento.valor_total), 0)
    ).filter(
        Faturamento.data_faturamento >= month_start,
        Faturamento.data_faturamento < next_month,
    ).scalar()
    custo_mes = db.session.query(
        func.coalesce(func.sum(Gasto.valor), 0)
    ).filter(
        Gasto.data_gasto >= month_start,
        Gasto.data_gasto < next_month,
    ).scalar()
    ultimas = Venda.query.order_by(Venda.data_abertura.desc()).limit(8).all()
    return render_template("modulos/dashboard.html", abertas=abertas, andamento=andamento, faturado_mes=faturado_mes, custo_mes=custo_mes, ultimas=ultimas)


@bp.route("/clientes")
def clientes():
    query_text = request.args.get("q", "").strip()
    query = Cliente.query
    if query_text:
        like = f"%{query_text}%"
        query = query.filter(or_(Cliente.nome.ilike(like), Cliente.telefone.ilike(like), Cliente.cpf_cnpj.ilike(like)))
    return render_template("modulos/clientes.html", clientes=query.order_by(Cliente.nome).all(), q=query_text)


@bp.route("/clientes/novo", methods=["GET", "POST"])
def cliente_novo():
    if request.method == "POST":
        cliente = Cliente(nome=request.form["nome"].strip(), filial_id=4, cpf_cnpj=request.form.get("cpf_cnpj"), telefone=request.form.get("telefone"), email=request.form.get("email"), contato=request.form.get("contato"), endereco=request.form.get("endereco"), numero=request.form.get("numero"), bairro=request.form.get("bairro"), cidade=request.form.get("cidade"), uf=request.form.get("uf"), cep=request.form.get("cep"), ativo=True, data_cadastro=datetime.now())
        db.session.add(cliente)
        db.session.commit()
        flash("Cliente cadastrado com sucesso.", "success")
        return redirect(url_for("modulos.clientes"))
    return render_template("modulos/cliente_form.html")


def _vendas_query(statuses=None):
    status = request.args.get("status", "")
    query_text = request.args.get("q", "").strip()
    query = Venda.query.join(Cliente)
    if statuses:
        query = query.filter(Venda.status.in_(statuses))
    elif status:
        query = query.filter(Venda.status == status)
    if query_text:
        like = f"%{query_text}%"
        query = query.filter(or_(Cliente.nome.ilike(like), Venda.placa.ilike(like), Venda.veiculo.ilike(like), Venda.modulo.ilike(like)))
    return query.order_by(Venda.data_abertura.desc()).all(), status, query_text


@bp.route("/orcamentos")
def orcamentos():
    records, _, query_text = _vendas_query(["ORCAMENTO", "APROVADO"])
    return render_template("modulos/vendas.html", vendas=records, status="", q=query_text, titulo="Orçamentos", subtitulo="Propostas em elaboração ou aguardando aprovação.", acao="+ Novo orçamento", somente_orcamentos=True)


@bp.route("/vendas")
def vendas():
    records, status, query_text = _vendas_query()
    return render_template("modulos/vendas.html", vendas=records, status=status, q=query_text, titulo="Vendas / OS", subtitulo="Ordens em execução, finalizadas e faturadas.", acao="+ Nova OS / venda", somente_orcamentos=False)


@bp.route("/vendas/nova", methods=["GET", "POST"])
def venda_nova():
    clientes_ativos = Cliente.query.filter_by(ativo=True).order_by(Cliente.nome).all()
    produtos_ativos = ProdutoServico.query.filter_by(ativo=True).order_by(ProdutoServico.tipo, ProdutoServico.descricao).all()
    if request.method == "POST":
        venda = Venda(cliente_id=int(request.form["cliente_id"]), data_abertura=datetime.now(), status=request.form.get("status", "ORCAMENTO"), placa=request.form.get("placa", "").upper(), veiculo=request.form.get("veiculo"), ano_veiculo=request.form.get("ano_veiculo"), modulo=request.form.get("modulo"), codigo_modulo=request.form.get("codigo_modulo"), defeito_relatado=request.form.get("defeito_relatado"), diagnostico=request.form.get("diagnostico"), valor_pecas=0, valor_servicos=0, desconto=d(request.form.get("desconto")), valor_total=0, data_cadastro=datetime.now())
        db.session.add(venda)
        db.session.flush()
        pecas, servicos = Decimal("0"), Decimal("0")
        quantities = request.form.getlist("quantidade")
        unit_prices = request.form.getlist("valor_unitario")

        for index, product_id in enumerate(request.form.getlist("produto_id")):
            if not product_id:
                continue
            product = db.session.get(ProdutoServico, int(product_id))
            if not product:
                continue

            quantity = d(quantities[index] if index < len(quantities) else 1)
            raw_price = unit_prices[index].replace(",", ".") if index < len(unit_prices) and unit_prices[index].strip() else None
            unit_price = d(raw_price) if raw_price is not None else product.valor_padrao

            total = unit_price * quantity
            cost_total = product.custo_padrao * quantity

            db.session.add(
                ItemVenda(
                    venda_id=venda.id,
                    produto_servico_id=product.id,
                    descricao=product.descricao,
                    tipo=product.tipo,
                    quantidade=quantity,
                    custo_unitario=product.custo_padrao,
                    valor_unitario=unit_price,
                    desconto=0,
                    custo_total=cost_total,
                    valor_total=total,
                    data_cadastro=datetime.now(),
                )
            )
            if product.tipo == "PECA":
                pecas += total
            else:
                servicos += total
        venda.valor_pecas = pecas
        venda.valor_servicos = servicos
        venda.valor_total = pecas + servicos - venda.desconto
        db.session.commit()
        flash(f"{venda.numero} criada com sucesso.", "success")
        return redirect(url_for("modulos.venda_detalhe", venda_id=venda.id))
    return render_template("modulos/venda_form.html", clientes=clientes_ativos, produtos=produtos_ativos)


@bp.route("/vendas/<int:venda_id>")
def venda_detalhe(venda_id):
    return render_template("modulos/venda_detalhe.html", venda=db.get_or_404(Venda, venda_id))


@bp.route("/vendas/<int:venda_id>/status", methods=["POST"])
def venda_status(venda_id):
    venda = db.get_or_404(Venda, venda_id)
    new_status = request.form.get("status")
    if new_status in {"ORCAMENTO", "APROVADO", "EM_SERVICO", "FINALIZADO", "FATURADO", "CANCELADO"}:
        venda.status = new_status
        now = datetime.now()
        if new_status == "APROVADO":
            venda.data_aprovacao = venda.data_aprovacao or now
        if new_status == "EM_SERVICO":
            venda.data_inicio_servico = venda.data_inicio_servico or now
        if new_status in {"FINALIZADO", "FATURADO"}:
            venda.data_finalizacao = venda.data_finalizacao or now

        if new_status == "FATURADO":
            forma_pagamento = request.form.get("forma_pagamento", "").strip() or "NÃO INFORMADO"
            status_pagamento = request.form.get("status_pagamento", "PAGO").strip() or "PAGO"
            fat = Faturamento.query.filter_by(venda_id=venda.id).first()
            if not fat:
                fat = Faturamento(
                    venda_id=venda.id,
                    data_faturamento=now.date(),
                    data_cadastro=now,
                )
                db.session.add(fat)
            fat.valor_servicos = venda.valor_servicos
            fat.valor_pecas = venda.valor_pecas
            fat.desconto = venda.desconto
            fat.valor_total = venda.valor_total
            fat.forma_pagamento = forma_pagamento
            fat.status_pagamento = status_pagamento
            if status_pagamento == "PAGO":
                fat.data_pagamento = fat.data_pagamento or now.date()
                fat.valor_pago = venda.valor_total

        db.session.commit()
        flash("Status atualizado.", "success")
    return redirect(url_for("modulos.venda_detalhe", venda_id=venda.id))

@bp.route("/produtos")
def produtos():
    query_text = request.args.get("q", "").strip()
    query = ProdutoServico.query
    if query_text:
        like = f"%{query_text}%"
        query = query.filter(
            or_(ProdutoServico.descricao.ilike(like), ProdutoServico.codigo.ilike(like))
        )
    records = query.order_by(ProdutoServico.tipo, ProdutoServico.descricao).all()
    return render_template("modulos/produtos.html", produtos=records, q=query_text)


@bp.route("/produtos/novo", methods=["GET", "POST"])
def produto_novo():
    if request.method == "POST":
        item = ProdutoServico(
            codigo=request.form.get("codigo", "").strip() or None,
            descricao=request.form["descricao"].strip(),
            tipo=request.form["tipo"],  # "PECA" ou "SERVICO"
            custo_padrao=d(request.form.get("custo_padrao", "").replace(",", ".")),
            valor_padrao=d(request.form.get("valor_padrao", "").replace(",", ".")),
            ativo="ativo" in request.form,
            data_cadastro=datetime.now(),
        )
        db.session.add(item)
        db.session.commit()
        flash("Peça/serviço cadastrado com sucesso.", "success")
        return redirect(url_for("modulos.produtos"))
    return render_template("modulos/produto_form.html", produto=None)


@bp.route("/produtos/<int:produto_id>/editar", methods=["GET", "POST"])
def produto_editar(produto_id):
    item = db.get_or_404(ProdutoServico, produto_id)
    if request.method == "POST":
        item.codigo = request.form.get("codigo", "").strip() or None
        item.descricao = request.form["descricao"].strip()
        item.tipo = request.form["tipo"]
        item.custo_padrao = d(request.form.get("custo_padrao", "").replace(",", "."))
        item.valor_padrao = d(request.form.get("valor_padrao", "").replace(",", "."))
        item.ativo = "ativo" in request.form
        db.session.commit()
        flash("Peça/serviço atualizado com sucesso.", "success")
        return redirect(url_for("modulos.produtos"))
    return render_template("modulos/produto_form.html", produto=item)


@bp.route("/gastos", methods=["GET", "POST"])
def gastos():
    categorias = CategoriaGasto.query.filter_by(ativo=True).order_by(CategoriaGasto.nome).all()
    if request.method == "POST":
        gasto = Gasto(categoria_id=int(request.form["categoria_id"]), data_gasto=datetime.strptime(request.form["data_gasto"], "%Y-%m-%d").date(), descricao=request.form["descricao"], fornecedor=request.form.get("fornecedor"), valor=d(request.form["valor"]), forma_pagamento=request.form.get("forma_pagamento"), status=request.form.get("status", "PENDENTE"), data_cadastro=datetime.now())
        db.session.add(gasto)
        db.session.commit()
        flash("Gasto lançado.", "success")
        return redirect(url_for("modulos.gastos"))
    records = Gasto.query.order_by(Gasto.data_gasto.desc()).all()
    return render_template("modulos/gastos.html", gastos=records, categorias=categorias)


@bp.route("/faturamento")
def faturamento():
    records = Faturamento.query.order_by(Faturamento.data_faturamento.desc()).all()
    return render_template("modulos/faturamento.html", faturamentos=records)


@bp.route("/relatorios")
def relatorios():
    mes_selecionado = request.args.get("mes", "").strip()  # formato YYYY-MM (ex: 2026-11)

    q_vendas = db.session.query(func.coalesce(func.sum(Venda.valor_total), 0))
    q_gastos = db.session.query(func.coalesce(func.sum(Gasto.valor), 0))
    q_faturado = db.session.query(func.coalesce(func.sum(Faturamento.valor_total), 0))
    q_status = db.session.query(
        Venda.status,
        func.count(Venda.id),
        func.coalesce(func.sum(Venda.valor_total), 0),
    )
    q_cliente = (
        db.session.query(
            Cliente.nome,
            func.count(Venda.id),
            func.coalesce(func.sum(Venda.valor_total), 0),
        )
        .join(Venda)
    )
    q_pagamentos = db.session.query(
        func.coalesce(Faturamento.forma_pagamento, "NÃO INFORMADO"),
        func.count(Faturamento.id),
        func.coalesce(func.sum(Faturamento.valor_total), 0),
    )

    if mes_selecionado and len(mes_selecionado) == 7:
        try:
            ano, mes = map(int, mes_selecionado.split("-"))
            q_vendas = q_vendas.filter(
                func.year(Venda.data_abertura) == ano,
                func.month(Venda.data_abertura) == mes,
            )
            q_gastos = q_gastos.filter(
                func.year(Gasto.data_gasto) == ano,
                func.month(Gasto.data_gasto) == mes,
            )
            q_faturado = q_faturado.filter(
                func.year(Faturamento.data_faturamento) == ano,
                func.month(Faturamento.data_faturamento) == mes,
            )
            q_status = q_status.filter(
                func.year(Venda.data_abertura) == ano,
                func.month(Venda.data_abertura) == mes,
            )
            q_cliente = q_cliente.filter(
                func.year(Venda.data_abertura) == ano,
                func.month(Venda.data_abertura) == mes,
            )
            q_pagamentos = q_pagamentos.filter(
                func.year(Faturamento.data_faturamento) == ano,
                func.month(Faturamento.data_faturamento) == mes,
            )
        except ValueError:
            mes_selecionado = ""

    total_vendas = q_vendas.scalar()
    total_gastos = q_gastos.scalar()
    total_faturado = q_faturado.scalar()
    resultado_liquido = (total_faturado or 0) - (total_gastos or 0)

    por_status = q_status.group_by(Venda.status).all()
    por_cliente = (
        q_cliente.group_by(Cliente.id, Cliente.nome)
        .order_by(func.sum(Venda.valor_total).desc())
        .all()
    )
    por_pagamento = (
        q_pagamentos.group_by(Faturamento.forma_pagamento)
        .order_by(func.sum(Faturamento.valor_total).desc())
        .all()
    )

    # Visão consolidada mês a mês (independente do filtro, para comparação)
    vendas_mes = {
        (int(y), int(m)): float(v or 0)
        for y, m, v in db.session.query(
            func.year(Venda.data_abertura),
            func.month(Venda.data_abertura),
            func.coalesce(func.sum(Venda.valor_total), 0),
        )
        .filter(Venda.data_abertura.isnot(None))
        .group_by(func.year(Venda.data_abertura), func.month(Venda.data_abertura))
        .all()
    }
    faturado_mes = {
        (int(y), int(m)): float(v or 0)
        for y, m, v in db.session.query(
            func.year(Faturamento.data_faturamento),
            func.month(Faturamento.data_faturamento),
            func.coalesce(func.sum(Faturamento.valor_total), 0),
        )
        .filter(Faturamento.data_faturamento.isnot(None))
        .group_by(func.year(Faturamento.data_faturamento), func.month(Faturamento.data_faturamento))
        .all()
    }
    gastos_mes = {
        (int(y), int(m)): float(v or 0)
        for y, m, v in db.session.query(
            func.year(Gasto.data_gasto),
            func.month(Gasto.data_gasto),
            func.coalesce(func.sum(Gasto.valor), 0),
        )
        .filter(Gasto.data_gasto.isnot(None))
        .group_by(func.year(Gasto.data_gasto), func.month(Gasto.data_gasto))
        .all()
    }

    todos_meses = sorted(
        set(vendas_mes.keys()) | set(faturado_mes.keys()) | set(gastos_mes.keys()),
        reverse=True,
    )
    evolucao_mensal = []
    for ano, mes in todos_meses:
        v_os = vendas_mes.get((ano, mes), 0.0)
        v_fat = faturado_mes.get((ano, mes), 0.0)
        v_gas = gastos_mes.get((ano, mes), 0.0)
        evolucao_mensal.append({
            "chave": f"{ano:04d}-{mes:02d}",
            "label": f"{mes:02d}/{ano:04d}",
            "vendas": v_os,
            "faturado": v_fat,
            "gastos": v_gas,
            "saldo": v_fat - v_gas,
        })

    return render_template(
        "modulos/relatorios.html",
        mes_selecionado=mes_selecionado,
        total_vendas=total_vendas,
        total_gastos=total_gastos,
        total_faturado=total_faturado,
        resultado_liquido=resultado_liquido,
        por_status=por_status,
        por_cliente=por_cliente,
        por_pagamento=por_pagamento,
        evolucao_mensal=evolucao_mensal,
    )