from decimal import Decimal
from .extensions import db


class Cliente(db.Model):
    __tablename__ = "clientes_modulos"
    __table_args__ = {"schema": "dbo"}
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(160), nullable=False)
    filial_id = db.Column(db.Integer)
    cpf_cnpj = db.Column(db.String(30))
    telefone = db.Column(db.String(30))
    email = db.Column(db.String(160))
    contato = db.Column(db.String(160))
    endereco = db.Column(db.String(180))
    numero = db.Column(db.String(30))
    complemento = db.Column(db.String(100))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    uf = db.Column(db.String(2))
    cep = db.Column(db.String(20))
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime)


class Veiculo(db.Model):
    __tablename__ = "veiculos_modulos"
    __table_args__ = {"schema": "dbo"}
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("dbo.clientes_modulos.id"), nullable=False)
    placa = db.Column(db.String(15), index=True, nullable=False)
    fabricante = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(150), nullable=False)
    cliente = db.relationship("Cliente", backref=db.backref("veiculos", lazy=True))

    @property
    def veiculo(self):
        return " ".join(part for part in (self.fabricante, self.modelo) if part)

    @property
    def ano(self):
        # A tabela atual não possui ano; mantém compatibilidade com a API.
        return None


class ProdutoServico(db.Model):
    __tablename__ = "produtos_servicos_modulos"
    __table_args__ = {"schema": "dbo"}
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30))
    descricao = db.Column(db.String(180), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    custo_padrao = db.Column(db.Numeric(12, 2), default=0)
    valor_padrao = db.Column(db.Numeric(12, 2), default=0)
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime)


class Venda(db.Model):
    __tablename__ = "vendas_modulos"
    __table_args__ = {"schema": "dbo"}
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("dbo.clientes_modulos.id"), nullable=False)
    data_abertura = db.Column(db.DateTime)
    data_aprovacao = db.Column(db.DateTime)
    data_inicio_servico = db.Column(db.DateTime)
    data_finalizacao = db.Column(db.DateTime)
    status = db.Column(db.String(30), default="ORCAMENTO", index=True)
    placa = db.Column(db.String(15), index=True)
    veiculo = db.Column(db.String(120))
    ano_veiculo = db.Column(db.String(10))
    chassi = db.Column(db.String(30))
    modulo = db.Column(db.String(160))
    codigo_modulo = db.Column(db.String(80))
    numero_serie_modulo = db.Column(db.String(100))
    defeito_relatado = db.Column(db.Text)
    diagnostico = db.Column(db.Text)
    servico_realizado = db.Column(db.Text)
    valor_pecas = db.Column(db.Numeric(12, 2), default=0)
    valor_servicos = db.Column(db.Numeric(12, 2), default=0)
    desconto = db.Column(db.Numeric(12, 2), default=0)
    valor_total = db.Column(db.Numeric(12, 2), default=0)
    colaborador_id = db.Column(db.Integer)
    observacao = db.Column(db.Text)
    data_cadastro = db.Column(db.DateTime)
    data_alteracao = db.Column(db.DateTime)
    cliente = db.relationship("Cliente", backref=db.backref("vendas", lazy=True))

    @property
    def numero(self):
        return f"OS {self.id:05d}"


class ItemVenda(db.Model):
    __tablename__ = "itens_venda_modulos"
    __table_args__ = {"schema": "dbo"}
    id = db.Column(db.Integer, primary_key=True)
    venda_id = db.Column(db.Integer, db.ForeignKey("dbo.vendas_modulos.id"), nullable=False)
    produto_servico_id = db.Column(db.Integer, db.ForeignKey("dbo.produtos_servicos_modulos.id"))
    descricao = db.Column(db.String(180), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    quantidade = db.Column(db.Numeric(12, 2), default=1)
    custo_unitario = db.Column(db.Numeric(12, 2), default=0)
    valor_unitario = db.Column(db.Numeric(12, 2), default=0)
    desconto = db.Column(db.Numeric(12, 2), default=0)
    custo_total = db.Column(db.Numeric(12, 2), default=0)
    valor_total = db.Column(db.Numeric(12, 2), default=0)
    observacao = db.Column(db.String(500))
    data_cadastro = db.Column(db.DateTime)
    venda = db.relationship("Venda", backref=db.backref("itens", lazy=True, cascade="all, delete-orphan"))
    produto_servico = db.relationship("ProdutoServico")


class CategoriaGasto(db.Model):
    __tablename__ = "categorias_gastos_modulos"
    __table_args__ = {"schema": "dbo"}
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.String(255))
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime)


class Gasto(db.Model):
    __tablename__ = "gastos_modulos"
    __table_args__ = {"schema": "dbo"}
    id = db.Column(db.Integer, primary_key=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey("dbo.categorias_gastos_modulos.id"))
    data_gasto = db.Column(db.Date)
    descricao = db.Column(db.String(200), nullable=False)
    fornecedor = db.Column(db.String(160))
    valor = db.Column(db.Numeric(12, 2), default=0)
    forma_pagamento = db.Column(db.String(40))
    status = db.Column(db.String(30))
    data_vencimento = db.Column(db.Date)
    data_pagamento = db.Column(db.Date)
    observacao = db.Column(db.Text)
    data_cadastro = db.Column(db.DateTime)
    categoria = db.relationship("CategoriaGasto")


class Faturamento(db.Model):
    __tablename__ = "faturamento_modulos"
    __table_args__ = {"schema": "dbo"}
    id = db.Column(db.Integer, primary_key=True)
    venda_id = db.Column(db.Integer, db.ForeignKey("dbo.vendas_modulos.id"), nullable=False)
    data_faturamento = db.Column(db.Date)
    valor_servicos = db.Column(db.Numeric(12, 2), default=0)
    valor_pecas = db.Column(db.Numeric(12, 2), default=0)
    desconto = db.Column(db.Numeric(12, 2), default=0)
    valor_total = db.Column(db.Numeric(12, 2), default=0)
    forma_pagamento = db.Column(db.String(40))
    status_pagamento = db.Column(db.String(30))
    data_vencimento = db.Column(db.Date)
    data_pagamento = db.Column(db.Date)
    valor_pago = db.Column(db.Numeric(12, 2), default=0)
    observacao = db.Column(db.Text)
    data_cadastro = db.Column(db.DateTime)
    venda = db.relationship("Venda", backref=db.backref("faturamentos", lazy=True))
