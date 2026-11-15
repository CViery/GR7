from decimal import Decimal, InvalidOperation
import secrets

from flask import flash, redirect, render_template, request, session, url_for

from app import app
from services.aprovacoes import AprovacoesEdicao


def _login_required():
    if "usuario" not in session or "usuario_id" not in session:
        flash("Faça login para continuar.")
        return redirect(url_for("show_login"))
    return None


def _context():
    return {
        "empresa": session.get("empresa"),
        "usuario": session.get("usuario"),
        "permission": session.get("permission"),
    }


def _csrf_token():
    token = session.get("approval_csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["approval_csrf_token"] = token
    return token


def _valid_csrf():
    expected = session.get("approval_csrf_token", "")
    received = request.form.get("csrf_token", "")
    return bool(expected and secrets.compare_digest(expected, received))


@app.context_processor
def approval_template_helpers():
    return {"approval_csrf_token": _csrf_token}


def _money(value):
    text = str(value or "0").replace("R$", "").replace(" ", "")
    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    try:
        return Decimal(text)
    except InvalidOperation as error:
        raise ValueError(f"Valor monetário inválido: {value}") from error


@app.route("/faturamentos/novo/<int:faturamento_id>/solicitar-edicao", methods=["GET", "POST"])
def solicitar_edicao_faturamento(faturamento_id):
    guard = _login_required()
    if guard:
        return guard
    service = AprovacoesEdicao()
    record = service.obter_faturamento(faturamento_id, session["empresa"])
    if not record:
        flash("OS não encontrada nesta filial.")
        return redirect(url_for("consultar_faturamentos"))

    if request.method == "POST":
        if not _valid_csrf():
            flash("A sessão do formulário expirou. Tente novamente.")
            return redirect(request.url)
        try:
            fields = request.form.getlist("campos")
            request_id = service.solicitar(
                faturamento_id,
                session["empresa"],
                session["usuario_id"],
                request.form.get("motivo", ""),
                fields,
            )
            flash("Solicitação enviada. Você receberá a resposta no GR7.")
            return redirect(url_for("detalhe_aprovacao", solicitacao_id=request_id))
        except ValueError as error:
            flash(str(error))

    return render_template(
        "solicitar_edicao.html",
        faturamento=record,
        **_context(),
    )


@app.route("/aprovacoes")
def listar_aprovacoes():
    guard = _login_required()
    if guard:
        return guard
    service = AprovacoesEdicao()
    requests = service.listar(session["usuario_id"], session.get("permission"))
    return render_template("aprovacoes.html", solicitacoes=requests, **_context())


@app.route("/aprovacoes/<int:solicitacao_id>")
def detalhe_aprovacao(solicitacao_id):
    guard = _login_required()
    if guard:
        return guard
    service = AprovacoesEdicao()
    approval = service.obter_solicitacao(solicitacao_id)
    if not approval:
        flash("Solicitação não encontrada.")
        return redirect(url_for("listar_aprovacoes"))

    is_owner = approval["solicitante_id"] == session["usuario_id"]
    can_approve = (
        not is_owner
        and service.pode_aprovar(session["usuario_id"], approval["filial_id"])
    )
    if not is_owner and not can_approve:
        flash("Você não possui acesso a esta solicitação.")
        return redirect(url_for("home"))
    return render_template(
        "aprovacao_detalhe.html",
        solicitacao=approval,
        pode_aprovar=can_approve,
        **_context(),
    )


@app.route("/aprovacoes/<int:solicitacao_id>/decidir", methods=["POST"])
def decidir_aprovacao(solicitacao_id):
    guard = _login_required()
    if guard:
        return guard
    if not _valid_csrf():
        flash("A sessão do formulário expirou. Tente novamente.")
        return redirect(url_for("detalhe_aprovacao", solicitacao_id=solicitacao_id))
    service = AprovacoesEdicao()
    approval = service.obter_solicitacao(solicitacao_id)
    if (
        not approval
        or approval["solicitante_id"] == session["usuario_id"]
        or not service.pode_aprovar(session["usuario_id"], approval["filial_id"])
    ):
        flash("Você não possui permissão para decidir esta solicitação.")
        return redirect(url_for("listar_aprovacoes"))
    try:
        service.decidir(
            solicitacao_id,
            session["usuario_id"],
            request.form.get("decisao") == "APROVAR",
            request.form.get("justificativa", ""),
        )
        flash("Decisão registrada e enviada ao solicitante.")
    except ValueError as error:
        flash(str(error))
    return redirect(url_for("detalhe_aprovacao", solicitacao_id=solicitacao_id))


@app.route("/faturamentos/novo/<int:faturamento_id>/editar", methods=["GET", "POST"])
def editar_faturamento_autorizado(faturamento_id):
    guard = _login_required()
    if guard:
        return guard
    service = AprovacoesEdicao()
    record = service.obter_faturamento(faturamento_id, session["empresa"])
    if not record:
        flash("OS não encontrada nesta filial.")
        return redirect(url_for("consultar_faturamentos"))
    authorization = service.autorizacao_ativa(faturamento_id, session["usuario_id"])
    if not authorization:
        flash("Solicite autorização antes de editar esta OS.")
        return redirect(url_for("solicitar_edicao_faturamento", faturamento_id=faturamento_id))

    if request.method == "POST":
        if not _valid_csrf():
            flash("A sessão do formulário expirou. Tente novamente.")
            return redirect(request.url)
        try:
            data = {
                "placa": request.form.get("placa", "").upper().strip(),
                "modelo_veiculo": request.form.get("modelo_veiculo", "").strip(),
                "data_orcamento": request.form.get("data_orcamento") or None,
                "data_faturamento": request.form.get("data_faturamento") or None,
                "pecas": _money(request.form.get("pecas")),
                "servicos": _money(request.form.get("servicos")),
                "valor_os": _money(request.form.get("valor_os")),
                "valor_dinheiro": _money(request.form.get("valor_dinheiro")),
                "observacoes": request.form.get("observacoes", "").strip(),
                "_servicos": [],
            }
            service_ids = request.form.getlist("servico_id")
            quantities = request.form.getlist("servico_quantidade")
            values = request.form.getlist("servico_valor")
            details = request.form.getlist("servico_detalhe")
            for index, service_id in enumerate(service_ids):
                data["_servicos"].append({
                    "servico_id": int(service_id),
                    "quantidade": _money(quantities[index] if index < len(quantities) else 0),
                    "valor_total": _money(values[index] if index < len(values) else 0),
                    "detalhe": details[index].strip() if index < len(details) else "",
                })
            service.salvar_edicao(
                faturamento_id,
                session["empresa"],
                session["usuario_id"],
                data,
            )
            flash("OS alterada. A autorização foi consumida e a auditoria foi registrada.")
            return redirect(url_for("listar_aprovacoes"))
        except (ValueError, PermissionError) as error:
            flash(str(error))

    services = service.obter_servicos_faturamento(faturamento_id, session["empresa"])
    return render_template(
        "editar_faturamento.html",
        faturamento=record,
        servicos_adicionais=services,
        campos_permitidos=authorization["campos"],
        **_context(),
    )


@app.route("/notificacoes")
def listar_notificacoes():
    guard = _login_required()
    if guard:
        return guard
    notifications = AprovacoesEdicao().notificacoes(session["usuario_id"])
    return render_template("notificacoes.html", notificacoes=notifications, **_context())
