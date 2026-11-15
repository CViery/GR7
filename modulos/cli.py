import json
from pathlib import Path

import click
from flask import current_app

from .extensions import db
from .models import CategoriaGasto, Cliente, Faturamento, Gasto, ItemVenda, ProdutoServico, Veiculo, Venda
from .utils import boolean, date, dt, money


FILES = {
    "clientes_modulos.json": Cliente,
    "veiculos_modulos.json": Veiculo,
    "produtos_servicos_modulos.json": ProdutoServico,
    "categorias_gastos_modulos.json": CategoriaGasto,
    "vendas_modulos.json": Venda,
    "itens_venda_modulos.json": ItemVenda,
    "faturamento_modulos.json": Faturamento,
    "gastos_modulos.json": Gasto,
}


def _data_dir(value=None):
    return Path(value) if value else Path(current_app.root_path).parent / "data" / "modulos"


def _load_json(data_dir, name):
    path = Path(data_dir) / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def _clean(model, row):
    allowed = {column.name for column in model.__table__.columns}
    result = {key: value for key, value in row.items() if key in allowed}
    for key in ("id", "cliente_id", "filial_id", "colaborador_id", "venda_id", "produto_servico_id", "categoria_id"):
        if key in result and result[key] not in (None, ""):
            result[key] = int(result[key])
    for key in ("custo_padrao", "valor_padrao", "valor_pecas", "valor_servicos", "desconto", "valor_total", "quantidade", "custo_unitario", "valor_unitario", "custo_total", "valor", "valor_pago"):
        if key in result:
            result[key] = money(result[key])
    if "ativo" in result:
        result["ativo"] = boolean(result["ativo"])
    for key in ("data_cadastro", "data_abertura", "data_aprovacao", "data_inicio_servico", "data_finalizacao"):
        if key in result:
            result[key] = dt(result[key])
    for key in ("data_faturamento", "data_vencimento", "data_pagamento", "data_gasto"):
        if key in result:
            result[key] = date(result[key])
    return result


def import_json(data_dir=None, reset=False):
    if reset:
        db.drop_all()
        db.create_all()
    counts = {}
    for filename, model in FILES.items():
        created = 0
        for row in _load_json(_data_dir(data_dir), filename):
            primary_key = int(row["id"]) if row.get("id") else None
            if primary_key and db.session.get(model, primary_key):
                continue
            db.session.add(model(**_clean(model, row)))
            created += 1
        db.session.commit()
        counts[filename] = created
    return counts


def ensure_seeded():
    """Importa a base entregue somente na primeira execução."""
    if Cliente.query.first() or ProdutoServico.query.first() or Venda.query.first():
        return
    import_json()


def register_cli(app):
    @app.cli.command("modulos-seed-json")
    @click.option("--data-dir", default=None, help="Pasta contendo os JSONs.")
    @click.option("--reset", is_flag=True, help="Recria as tabelas antes de importar.")
    def seed_json(data_dir, reset):
        """Importa os JSONs da área GR7 Módulos."""
        for filename, created in import_json(data_dir, reset).items():
            click.echo(f"{filename}: {created} registro(s) importado(s)")
        click.echo("Importação concluída.")
