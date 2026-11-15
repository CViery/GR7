SET XACT_ABORT ON;
SET NOCOUNT ON;

BEGIN TRY
BEGIN TRANSACTION;

/* Dados necessários para notificações e controle de usuários. */
IF COL_LENGTH('dbo.usuarios', 'email') IS NULL
    ALTER TABLE dbo.usuarios ADD email NVARCHAR(255) NULL;
IF COL_LENGTH('dbo.usuarios', 'ativo') IS NULL
    ALTER TABLE dbo.usuarios ADD ativo BIT NOT NULL CONSTRAINT DF_usuarios_ativo DEFAULT 1;

/* Catálogo normalizado: um serviço mantém o mesmo significado em qualquer filial. */
IF OBJECT_ID('dbo.servicos_catalogo', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.servicos_catalogo (
        id INT IDENTITY(1,1) PRIMARY KEY,
        codigo VARCHAR(60) NOT NULL UNIQUE,
        nome NVARCHAR(160) NOT NULL,
        categoria VARCHAR(40) NOT NULL,
        unidade_medida VARCHAR(20) NOT NULL CONSTRAINT DF_servico_unidade DEFAULT 'UN',
        aceita_quantidade BIT NOT NULL CONSTRAINT DF_servico_quantidade DEFAULT 0,
        aceita_detalhe BIT NOT NULL CONSTRAINT DF_servico_detalhe DEFAULT 0,
        ativo BIT NOT NULL CONSTRAINT DF_servico_ativo DEFAULT 1,
        criado_em DATETIME2 NOT NULL CONSTRAINT DF_servico_criado DEFAULT SYSUTCDATETIME()
    );
END;

IF OBJECT_ID('dbo.servicos_filiais', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.servicos_filiais (
        id INT IDENTITY(1,1) PRIMARY KEY,
        filial_id INT NOT NULL REFERENCES dbo.filiais(id),
        servico_id INT NOT NULL REFERENCES dbo.servicos_catalogo(id),
        nome_exibicao NVARCHAR(160) NOT NULL,
        ordem_exibicao INT NOT NULL CONSTRAINT DF_servico_filial_ordem DEFAULT 0,
        obrigatorio BIT NOT NULL CONSTRAINT DF_servico_filial_obrig DEFAULT 0,
        desconta_meta BIT NOT NULL CONSTRAINT DF_servico_filial_meta DEFAULT 0,
        ativo BIT NOT NULL CONSTRAINT DF_servico_filial_ativo DEFAULT 1,
        CONSTRAINT UQ_servicos_filiais UNIQUE (filial_id, servico_id)
    );
END;

IF OBJECT_ID('dbo.faturamento_servicos', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.faturamento_servicos (
        id BIGINT IDENTITY(1,1) PRIMARY KEY,
        faturamento_id INT NOT NULL REFERENCES dbo.faturamento_novo(id),
        servico_id INT NOT NULL REFERENCES dbo.servicos_catalogo(id),
        quantidade DECIMAL(18,4) NOT NULL CONSTRAINT DF_fat_serv_qtd DEFAULT 1,
        valor_unitario DECIMAL(18,2) NOT NULL CONSTRAINT DF_fat_serv_unit DEFAULT 0,
        valor_total DECIMAL(18,2) NOT NULL CONSTRAINT DF_fat_serv_total DEFAULT 0,
        detalhe NVARCHAR(255) NULL,
        criado_em DATETIME2 NOT NULL CONSTRAINT DF_fat_serv_criado DEFAULT SYSUTCDATETIME(),
        CONSTRAINT CK_fat_serv_qtd CHECK (quantidade >= 0),
        CONSTRAINT CK_fat_serv_valores CHECK (valor_unitario >= 0 AND valor_total >= 0),
        CONSTRAINT UQ_fat_servico UNIQUE (faturamento_id, servico_id)
    );
END;

MERGE dbo.servicos_catalogo AS destino
USING (VALUES
    ('REVITALIZACAO','Revitalização','ADICIONAL',0,0),
    ('ADITIVO','Aditivo','ADICIONAL',1,0),
    ('AR_CONDICIONADO','Ar-condicionado','ADICIONAL',0,0),
    ('FLUIDO_SANGRIA','Fluido/Sangria','ADICIONAL',0,0),
    ('LAVAGEM','Lavagem','ADICIONAL',0,0),
    ('PALHETA','Palheta','ADICIONAL',0,1),
    ('ALTERNADOR','Alternador/Motor de arranque','ADICIONAL',0,0),
    ('DETERGENTE_PARABRISA','Detergente de para-brisa','ADICIONAL',0,0),
    ('FILTRO_HIGIENIZACAO','Filtro e higienização','ADICIONAL',0,0),
    ('LIMPEZA_FREIOS','Limpeza dos freios','ADICIONAL',0,0),
    ('FUNILARIA','Funilaria','ADICIONAL',0,0),
    ('PNEUS','Pneus','PRODUTO',1,1),
    ('TERCEIROS','Terceiros','TERCEIRO',0,1),
    ('BATERIA','Bateria','PRODUTO',1,1),
    ('OLEO','Óleo','PRODUTO',1,1),
    ('FREIOS','Freios','GRUPO_SERVICO',0,0),
    ('SUSPENSAO','Suspensão','GRUPO_SERVICO',0,0),
    ('INJECAO_IGNICAO','Injeção/Ignição','GRUPO_SERVICO',0,0),
    ('CABECOTE_MOTOR_ARREFECIMENTO','Cabeçote/Motor/Arrefecimento','GRUPO_SERVICO',0,0),
    ('OUTROS','Outros','GRUPO_SERVICO',0,0),
    ('TRANSMISSAO','Transmissão','GRUPO_SERVICO',0,0)
) AS origem(codigo,nome,categoria,aceita_quantidade,aceita_detalhe)
ON destino.codigo = origem.codigo
WHEN NOT MATCHED THEN
    INSERT (codigo,nome,categoria,aceita_quantidade,aceita_detalhe)
    VALUES (origem.codigo,origem.nome,origem.categoria,origem.aceita_quantidade,origem.aceita_detalhe);

INSERT INTO dbo.servicos_filiais
    (filial_id, servico_id, nome_exibicao, ordem_exibicao, obrigatorio, desconta_meta)
SELECT configuracao.filial_id, catalogo.id, configuracao.nome_exibicao,
       configuracao.ordem_exibicao, 0, configuracao.desconta_meta
FROM (VALUES
    (1,'REVITALIZACAO','Revitalização',10,0),(1,'ADITIVO','Aditivo',20,0),
    (1,'FLUIDO_SANGRIA','Fluido/Sangria',30,0),(1,'PALHETA','Palheta',40,0),
    (1,'LIMPEZA_FREIOS','Limpeza dos freios',50,0),(1,'DETERGENTE_PARABRISA','Detergente de para-brisa',60,0),
    (1,'FILTRO_HIGIENIZACAO','Filtro e higienização',70,0),(1,'PNEUS','Pneus',80,1),
    (1,'TERCEIROS','Terceiros',90,1),(1,'BATERIA','Bateria',100,1),(1,'OLEO','Óleo',110,0),
    (2,'REVITALIZACAO','Revitalização',10,0),(2,'AR_CONDICIONADO','Ar-condicionado',20,1),
    (2,'LAVAGEM','Lavagem',30,0),(2,'ALTERNADOR','Alternador/Motor de arranque',40,1),
    (2,'FUNILARIA','Funilaria',50,1),(2,'DETERGENTE_PARABRISA','Detergente de para-brisa',60,0),
    (2,'FILTRO_HIGIENIZACAO','Filtro e higienização',70,0),(2,'PNEUS','Pneus',80,1),
    (2,'BATERIA','Bateria',100,1),(2,'OLEO','Óleo',110,0),
    (3,'REVITALIZACAO','Revitalização',10,0),(3,'ADITIVO','Aditivo',20,0),
    (3,'FLUIDO_SANGRIA','Fluido/Sangria',30,0),(3,'PALHETA','Palheta',40,0),
    (3,'LIMPEZA_FREIOS','Limpeza dos freios',50,0),(3,'DETERGENTE_PARABRISA','Detergente de para-brisa',60,0),
    (3,'FILTRO_HIGIENIZACAO','Filtro e higienização',70,0),(3,'PNEUS','Pneus',80,1),
    (3,'TERCEIROS','Terceiros',90,1),(3,'BATERIA','Bateria',100,1),(3,'OLEO','Óleo',110,0)
) AS configuracao(filial_id,codigo,nome_exibicao,ordem_exibicao,desconta_meta)
JOIN dbo.filiais filial ON filial.id = configuracao.filial_id
JOIN dbo.servicos_catalogo catalogo ON catalogo.codigo = configuracao.codigo
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.servicos_filiais existente
    WHERE existente.filial_id = configuracao.filial_id
      AND existente.servico_id = catalogo.id
);

IF EXISTS (
    SELECT 1
    FROM dbo.faturamento_novo
    GROUP BY filial_id, num_os
    HAVING COUNT(*) > 1
)
BEGIN
    THROW 51001, 'Existem OS duplicadas por filial em dbo.faturamento_novo. Corrija-as antes de executar esta migração.', 1;
END;

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'UX_faturamento_novo_filial_os'
      AND object_id = OBJECT_ID('dbo.faturamento_novo')
)
    CREATE UNIQUE INDEX UX_faturamento_novo_filial_os
        ON dbo.faturamento_novo(filial_id, num_os);
IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = 'IX_faturamento_novo_filial_data'
      AND object_id = OBJECT_ID('dbo.faturamento_novo')
)
    CREATE INDEX IX_faturamento_novo_filial_data ON dbo.faturamento_novo(filial_id, data_faturamento);

/* Quem pode aprovar alterações por filial. Filial nula permite aprovação global. */
IF OBJECT_ID('dbo.aprovadores_edicao', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.aprovadores_edicao (
        id INT IDENTITY(1,1) PRIMARY KEY,
        usuario_id INT NOT NULL REFERENCES dbo.usuarios(id),
        filial_id INT NULL REFERENCES dbo.filiais(id),
        recebe_email BIT NOT NULL CONSTRAINT DF_aprovador_email DEFAULT 1,
        ativo BIT NOT NULL CONSTRAINT DF_aprovador_ativo DEFAULT 1,
        CONSTRAINT UQ_aprovador_filial UNIQUE (usuario_id, filial_id)
    );
END;

IF OBJECT_ID('dbo.solicitacoes_edicao', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.solicitacoes_edicao (
        id BIGINT IDENTITY(1,1) PRIMARY KEY,
        faturamento_id INT NOT NULL REFERENCES dbo.faturamento_novo(id),
        filial_id INT NOT NULL REFERENCES dbo.filiais(id),
        solicitante_id INT NOT NULL REFERENCES dbo.usuarios(id),
        motivo NVARCHAR(1000) NOT NULL,
        campos_solicitados NVARCHAR(MAX) NULL,
        status VARCHAR(20) NOT NULL CONSTRAINT DF_solicitacao_status DEFAULT 'PENDENTE',
        solicitado_em DATETIME2 NOT NULL CONSTRAINT DF_solicitacao_data DEFAULT SYSUTCDATETIME(),
        decidido_por INT NULL REFERENCES dbo.usuarios(id),
        decidido_em DATETIME2 NULL,
        justificativa_decisao NVARCHAR(1000) NULL,
        liberado_ate DATETIME2 NULL,
        utilizado_em DATETIME2 NULL,
        cancelado_em DATETIME2 NULL,
        CONSTRAINT CK_solicitacao_status CHECK (status IN ('PENDENTE','APROVADA','RECUSADA','UTILIZADA','EXPIRADA','CANCELADA'))
    );
    CREATE INDEX IX_solicitacao_pendente ON dbo.solicitacoes_edicao(status, filial_id, solicitado_em);
    CREATE INDEX IX_solicitacao_usuario ON dbo.solicitacoes_edicao(solicitante_id, status);
END;

IF OBJECT_ID('dbo.notificacoes', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.notificacoes (
        id BIGINT IDENTITY(1,1) PRIMARY KEY,
        usuario_id INT NOT NULL REFERENCES dbo.usuarios(id),
        tipo VARCHAR(40) NOT NULL,
        titulo NVARCHAR(200) NOT NULL,
        mensagem NVARCHAR(1000) NOT NULL,
        url NVARCHAR(500) NULL,
        lida_em DATETIME2 NULL,
        criada_em DATETIME2 NOT NULL CONSTRAINT DF_notificacao_criada DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_notificacoes_usuario ON dbo.notificacoes(usuario_id, lida_em, criada_em DESC);
END;

IF OBJECT_ID('dbo.auditoria_faturamento', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.auditoria_faturamento (
        id BIGINT IDENTITY(1,1) PRIMARY KEY,
        faturamento_id INT NOT NULL REFERENCES dbo.faturamento_novo(id),
        solicitacao_id BIGINT NOT NULL REFERENCES dbo.solicitacoes_edicao(id),
        usuario_id INT NOT NULL REFERENCES dbo.usuarios(id),
        filial_id INT NOT NULL REFERENCES dbo.filiais(id),
        dados_anteriores NVARCHAR(MAX) NOT NULL,
        dados_novos NVARCHAR(MAX) NOT NULL,
        alterado_em DATETIME2 NOT NULL CONSTRAINT DF_auditoria_alterado DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_auditoria_faturamento ON dbo.auditoria_faturamento(faturamento_id, alterado_em DESC);
END;

/* Estrutura da futura importação Porto - Custos e Compras. */
IF OBJECT_ID('dbo.importacoes_custos', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.importacoes_custos (
        id BIGINT IDENTITY(1,1) PRIMARY KEY,
        filial_id INT NOT NULL REFERENCES dbo.filiais(id),
        usuario_id INT NOT NULL REFERENCES dbo.usuarios(id),
        nome_arquivo NVARCHAR(255) NOT NULL,
        hash_arquivo CHAR(64) NOT NULL UNIQUE,
        periodo_inicio DATE NOT NULL,
        periodo_fim DATE NOT NULL,
        quantidade_compras INT NOT NULL CONSTRAINT DF_import_qtd_compras DEFAULT 0,
        quantidade_itens INT NOT NULL CONSTRAINT DF_import_qtd_itens DEFAULT 0,
        valor_total_informado DECIMAL(18,2) NOT NULL CONSTRAINT DF_import_total_info DEFAULT 0,
        valor_total_calculado DECIMAL(18,2) NOT NULL CONSTRAINT DF_import_total_calc DEFAULT 0,
        status VARCHAR(20) NOT NULL CONSTRAINT DF_import_status DEFAULT 'PROCESSANDO',
        mensagem_validacao NVARCHAR(1000) NULL,
        importado_em DATETIME2 NOT NULL CONSTRAINT DF_import_data DEFAULT SYSUTCDATETIME()
    );
END;

IF OBJECT_ID('dbo.fornecedores_custos', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.fornecedores_custos (
        id BIGINT IDENTITY(1,1) PRIMARY KEY,
        nome NVARCHAR(255) NOT NULL,
        nome_normalizado NVARCHAR(255) NOT NULL,
        cpf_cnpj VARCHAR(20) NULL,
        ativo BIT NOT NULL CONSTRAINT DF_fornecedor_custo_ativo DEFAULT 1,
        criado_em DATETIME2 NOT NULL CONSTRAINT DF_fornecedor_custo_criado DEFAULT SYSUTCDATETIME(),
        alterado_em DATETIME2 NULL,
        CONSTRAINT UQ_fornecedor_custo_nome UNIQUE (nome_normalizado)
    );
END;

IF OBJECT_ID('dbo.categorias_custos', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.categorias_custos (
        id INT IDENTITY(1,1) PRIMARY KEY,
        codigo VARCHAR(50) NOT NULL UNIQUE,
        nome NVARCHAR(150) NOT NULL,
        tipo VARCHAR(30) NOT NULL,
        ativo BIT NOT NULL CONSTRAINT DF_categoria_custo_ativo DEFAULT 1,
        criado_em DATETIME2 NOT NULL CONSTRAINT DF_categoria_custo_criado DEFAULT SYSUTCDATETIME(),
        CONSTRAINT CK_categoria_custo_tipo CHECK (
            tipo IN ('PECA_OS','ESTOQUE','INSUMO','SERVICO_TERCEIRO','ADMINISTRATIVO','FRETE','IMPOSTO','OUTRO')
        )
    );
END;

MERGE dbo.categorias_custos AS destino
USING (VALUES
    ('PECA_OS','Peça vinculada à OS','PECA_OS'),
    ('ESTOQUE','Compra para estoque','ESTOQUE'),
    ('INSUMO','Insumo operacional','INSUMO'),
    ('SERVICO_TERCEIRO','Serviço terceirizado','SERVICO_TERCEIRO'),
    ('ADMINISTRATIVO','Despesa administrativa','ADMINISTRATIVO'),
    ('FRETE','Frete','FRETE'),
    ('IMPOSTO','Imposto','IMPOSTO'),
    ('OUTRO','Não classificado','OUTRO')
) AS origem(codigo,nome,tipo)
ON destino.codigo = origem.codigo
WHEN NOT MATCHED THEN INSERT (codigo,nome,tipo)
VALUES (origem.codigo,origem.nome,origem.tipo);

IF OBJECT_ID('dbo.compras', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.compras (
        id BIGINT IDENTITY(1,1) PRIMARY KEY,
        importacao_id BIGINT NOT NULL REFERENCES dbo.importacoes_custos(id),
        filial_id INT NOT NULL REFERENCES dbo.filiais(id),
        fornecedor_id BIGINT NULL REFERENCES dbo.fornecedores_custos(id),
        codigo_compra VARCHAR(30) NOT NULL,
        situacao VARCHAR(20) NULL,
        numero_nota VARCHAR(60) NULL,
        data_lancamento DATE NULL,
        data_emissao DATE NOT NULL,
        fornecedor_original NVARCHAR(255) NOT NULL,
        valor_bruto DECIMAL(18,2) NOT NULL CONSTRAINT DF_compra_bruto DEFAULT 0,
        desconto DECIMAL(18,2) NOT NULL CONSTRAINT DF_compra_desconto DEFAULT 0,
        valor_itens DECIMAL(18,2) NOT NULL CONSTRAINT DF_compra_itens DEFAULT 0,
        valor_frete DECIMAL(18,2) NOT NULL CONSTRAINT DF_compra_frete DEFAULT 0,
        valor_despesas DECIMAL(18,2) NOT NULL CONSTRAINT DF_compra_despesas DEFAULT 0,
        valor_ipi DECIMAL(18,2) NOT NULL CONSTRAINT DF_compra_ipi DEFAULT 0,
        substituicao_tributaria DECIMAL(18,2) NOT NULL CONSTRAINT DF_compra_st DEFAULT 0,
        icms_desonerado DECIMAL(18,2) NOT NULL CONSTRAINT DF_compra_icms DEFAULT 0,
        fcp_st DECIMAL(18,2) NOT NULL CONSTRAINT DF_compra_fcp DEFAULT 0,
        valor_devolucao DECIMAL(18,2) NOT NULL CONSTRAINT DF_compra_devolucao DEFAULT 0,
        valor_total DECIMAL(18,2) NOT NULL CONSTRAINT DF_compra_total DEFAULT 0,
        criado_em DATETIME2 NOT NULL CONSTRAINT DF_compra_criado DEFAULT SYSUTCDATETIME(),
        CONSTRAINT UQ_compra_filial_codigo UNIQUE (filial_id, codigo_compra),
        CONSTRAINT CK_compra_valores CHECK (
            valor_bruto >= 0 AND desconto >= 0 AND valor_frete >= 0
            AND valor_despesas >= 0 AND valor_total >= 0
        )
    );
    CREATE INDEX IX_compras_filial_emissao ON dbo.compras(filial_id, data_emissao);
    CREATE INDEX IX_compras_fornecedor ON dbo.compras(fornecedor_id, data_emissao);
    CREATE INDEX IX_compras_nota ON dbo.compras(filial_id, numero_nota);
END;

IF OBJECT_ID('dbo.itens_compras', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.itens_compras (
        id BIGINT IDENTITY(1,1) PRIMARY KEY,
        compra_id BIGINT NOT NULL REFERENCES dbo.compras(id),
        filial_id INT NOT NULL REFERENCES dbo.filiais(id),
        categoria_id INT NULL REFERENCES dbo.categorias_custos(id),
        faturamento_id INT NULL REFERENCES dbo.faturamento_novo(id),
        numero_os_origem INT NULL,
        placa VARCHAR(15) NULL,
        veiculo NVARCHAR(180) NULL,
        tipo_cliente NVARCHAR(80) NULL,
        codigo_item VARCHAR(80) NULL,
        descricao NVARCHAR(500) NOT NULL,
        quantidade DECIMAL(18,4) NOT NULL CONSTRAINT DF_item_compra_qtd DEFAULT 0,
        valor_bruto DECIMAL(18,2) NOT NULL CONSTRAINT DF_item_compra_bruto DEFAULT 0,
        percentual_desconto DECIMAL(9,4) NOT NULL CONSTRAINT DF_item_compra_desc DEFAULT 0,
        valor_liquido DECIMAL(18,2) NOT NULL CONSTRAINT DF_item_compra_liq DEFAULT 0,
        cfop VARCHAR(10) NULL,
        valor_devolucao DECIMAL(18,2) NOT NULL CONSTRAINT DF_item_compra_dev DEFAULT 0,
        valor_venda_bruto DECIMAL(18,2) NOT NULL CONSTRAINT DF_item_venda_bruto DEFAULT 0,
        percentual_desconto_venda DECIMAL(9,4) NOT NULL CONSTRAINT DF_item_venda_desc DEFAULT 0,
        valor_venda_liquido DECIMAL(18,2) NOT NULL CONSTRAINT DF_item_venda_liq DEFAULT 0,
        diferenca_bruta DECIMAL(18,2) NOT NULL CONSTRAINT DF_item_dif_bruta DEFAULT 0,
        diferenca_liquida DECIMAL(18,2) NOT NULL CONSTRAINT DF_item_dif_liq DEFAULT 0,
        destino VARCHAR(30) NOT NULL CONSTRAINT DF_item_destino DEFAULT 'NAO_CLASSIFICADO',
        status_conciliacao VARCHAR(30) NOT NULL CONSTRAINT DF_item_conciliacao DEFAULT 'PENDENTE',
        criado_em DATETIME2 NOT NULL CONSTRAINT DF_item_compra_criado DEFAULT SYSUTCDATETIME(),
        CONSTRAINT CK_item_compra_qtd CHECK (quantidade >= 0),
        CONSTRAINT CK_item_compra_destino CHECK (
            destino IN ('OS','ESTOQUE','INSUMO','ADMINISTRATIVO','SERVICO_TERCEIRO','NAO_CLASSIFICADO')
        ),
        CONSTRAINT CK_item_compra_conciliacao CHECK (
            status_conciliacao IN ('PENDENTE','AUTOMATICA','MANUAL','OS_NAO_ENCONTRADA','DIVERGENCIA','NAO_APLICAVEL')
        )
    );
    CREATE INDEX IX_itens_compras_os ON dbo.itens_compras(filial_id, numero_os_origem);
    CREATE INDEX IX_itens_compras_faturamento ON dbo.itens_compras(faturamento_id);
    CREATE INDEX IX_itens_compras_status ON dbo.itens_compras(status_conciliacao, filial_id);
    CREATE INDEX IX_itens_compras_codigo ON dbo.itens_compras(codigo_item);
END;

IF OBJECT_ID('dbo.parcelas_compras', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.parcelas_compras (
        id BIGINT IDENTITY(1,1) PRIMARY KEY,
        compra_id BIGINT NOT NULL REFERENCES dbo.compras(id),
        numero_parcela INT NOT NULL,
        data_vencimento DATE NOT NULL,
        valor DECIMAL(18,2) NOT NULL,
        status_pagamento VARCHAR(20) NOT NULL CONSTRAINT DF_parcela_status DEFAULT 'PENDENTE',
        data_pagamento DATE NULL,
        valor_pago DECIMAL(18,2) NOT NULL CONSTRAINT DF_parcela_pago DEFAULT 0,
        forma_pagamento VARCHAR(40) NULL,
        criado_em DATETIME2 NOT NULL CONSTRAINT DF_parcela_criado DEFAULT SYSUTCDATETIME(),
        CONSTRAINT UQ_parcela_compra UNIQUE (compra_id, numero_parcela),
        CONSTRAINT CK_parcela_valor CHECK (valor >= 0 AND valor_pago >= 0),
        CONSTRAINT CK_parcela_status CHECK (
            status_pagamento IN ('PENDENTE','PARCIAL','PAGO','VENCIDO','CANCELADO')
        )
    );
    CREATE INDEX IX_parcelas_vencimento ON dbo.parcelas_compras(status_pagamento, data_vencimento);
END;

/* Camada temporária: relatórios antigos passam a enxergar registros antigos e
   novos sem duplicar uma OS já migrada. Pode ser removida ao fim da migração. */
EXEC(N'
CREATE OR ALTER VIEW dbo.vw_faturamento_compat AS
SELECT id,placa,modelo_veiculo,data_orcamento,data_faturamento,mes_faturamento,
       ano_faturamento,dias,num_os,cia,conversao_pneustore,pecas,servicos,valor_os,
       revitalizacao,aditivo,quantidade_aditivo,fluido_sangria,palheta,limpeza_freios,
       detergente_parabrisa,filtro,pneus,bateria,modelo_bateria,quantidade_oleo,
       valor_oleo,tipo_marca_oleo,valor_meta,mecanico,filtro_mecanico,valor_dinheiro,
       freios,suspensao,injecao_ignicao,cabecote_motor_arrefecimento,outros,oleos,
       transmissao,usuario,CAST(observacoes AS varchar(max)) AS observacoes,terceiros,CAST(1 AS int) AS filial_id,CAST(0 AS bit) AS origem_novo
FROM dbo.faturamento
UNION ALL
SELECT id,placa,modelo_veiculo,data_orcamento,data_faturamento,mes_faturamento,
       ano_faturamento,dias,num_os,cia,conversao_pneustore,pecas,servicos,valor_os,
       revitalizacao,aditivo,quantidade_aditivo,fluido_sangria,palheta,limpeza_freios,
       detergente_parabrisa,filtro,CAST(pneus AS decimal(18,2)),bateria,modelo_bateria,
       quantidade_oleo,valor_oleo,tipo_marca_oleo,valor_meta,mecanico,filtro_mecanico,
       valor_dinheiro,freios,suspensao,injecao_ignicao,cabecote_motor_arrefecimento,
       outros,oleos,transmissao,usuario,CAST(observacoes AS varchar(max)),terceiros,CAST(2 AS int),CAST(0 AS bit)
FROM dbo.faturamento_portal
UNION ALL
SELECT id,placa,modelo_veiculo,data_orcamento,data_faturamento,mes_faturamento,
       ano_faturamento,dias,num_os,cia,conversao_pneustore,pecas,servicos,valor_os,
       revitalizacao,aditivo,quantidade_aditivo,fluido_sangria,palheta,limpeza_freios,
       detergente_parabrisa,filtro,pneus,bateria,modelo_bateria,quantidade_oleo,
       valor_oleo,tipo_marca_oleo,valor_meta,mecanico,filtro_mecanico,valor_dinheiro,
       freios,suspensao,injecao_ignicao,cabecote_motor_arrefecimento,outros,oleos,
       transmissao,usuario,CAST(observacoes AS varchar(max)),terceiros,CAST(3 AS int),CAST(0 AS bit)
FROM dbo.faturamento_morumbi
UNION ALL
SELECT n.id,n.placa,CAST(n.modelo_veiculo AS varchar(255)),
       CONVERT(varchar(10),n.data_orcamento,23),CONVERT(varchar(10),n.data_faturamento,23),
       RIGHT(''0'' + CAST(n.mes_faturamento AS varchar(2)),2),CAST(n.ano_faturamento AS varchar(4)),
       n.dias,n.num_os,CAST(n.cia AS varchar(255)),CAST(n.conversao_pneustore AS varchar(255)),
       n.pecas,n.servicos,n.valor_os,n.revitalizacao,n.aditivo,n.quantidade_aditivo,
       n.fluido_sangria,n.palheta,n.limpeza_freios,n.detergente_parabrisa,n.filtro,
       n.pneus,n.bateria,CAST(n.modelo_bateria AS varchar(255)),n.quantidade_oleo,
       n.valor_oleo,CAST(n.tipo_marca_oleo AS varchar(255)),n.valor_meta,
       CAST(m.nome AS varchar(255)),CAST(mf.nome AS varchar(255)),n.valor_dinheiro,
       n.freios,n.suspensao,n.injecao_ignicao,n.cabecote_motor_arrefecimento,n.outros,
       n.oleos,n.transmissao,CAST(u.usuario AS varchar(255)),CAST(n.observacoes AS varchar(max)),
       n.terceiros,n.filial_id,CAST(1 AS bit)
FROM dbo.faturamento_novo n
LEFT JOIN dbo.colaboradores m ON m.id = n.mecanico_id
LEFT JOIN dbo.colaboradores mf ON mf.id = n.mecanico_filtro_id
LEFT JOIN dbo.usuarios u ON u.id = n.usuario_id
WHERE
    (n.filial_id = 1 AND NOT EXISTS (SELECT 1 FROM dbo.faturamento x WHERE x.num_os=n.num_os))
 OR (n.filial_id = 2 AND NOT EXISTS (SELECT 1 FROM dbo.faturamento_portal x WHERE x.num_os=n.num_os))
 OR (n.filial_id = 3 AND NOT EXISTS (SELECT 1 FROM dbo.faturamento_morumbi x WHERE x.num_os=n.num_os));
');

COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF XACT_STATE() <> 0
        ROLLBACK TRANSACTION;
    THROW;
END CATCH;
