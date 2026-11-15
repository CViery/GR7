SELECT
    objeto,
    CASE WHEN object_id IS NULL THEN 'FALTANDO' ELSE 'OK' END AS situacao
FROM (VALUES
    ('dbo.faturamento_novo', OBJECT_ID('dbo.faturamento_novo', 'U')),
    ('dbo.servicos_catalogo', OBJECT_ID('dbo.servicos_catalogo', 'U')),
    ('dbo.servicos_filiais', OBJECT_ID('dbo.servicos_filiais', 'U')),
    ('dbo.faturamento_servicos', OBJECT_ID('dbo.faturamento_servicos', 'U')),
    ('dbo.solicitacoes_edicao', OBJECT_ID('dbo.solicitacoes_edicao', 'U')),
    ('dbo.aprovadores_edicao', OBJECT_ID('dbo.aprovadores_edicao', 'U')),
    ('dbo.notificacoes', OBJECT_ID('dbo.notificacoes', 'U')),
    ('dbo.auditoria_faturamento', OBJECT_ID('dbo.auditoria_faturamento', 'U')),
    ('dbo.importacoes_custos', OBJECT_ID('dbo.importacoes_custos', 'U')),
    ('dbo.fornecedores_custos', OBJECT_ID('dbo.fornecedores_custos', 'U')),
    ('dbo.categorias_custos', OBJECT_ID('dbo.categorias_custos', 'U')),
    ('dbo.compras', OBJECT_ID('dbo.compras', 'U')),
    ('dbo.itens_compras', OBJECT_ID('dbo.itens_compras', 'U')),
    ('dbo.parcelas_compras', OBJECT_ID('dbo.parcelas_compras', 'U')),
    ('dbo.vw_faturamento_compat', OBJECT_ID('dbo.vw_faturamento_compat', 'V'))
) verificacao(objeto, object_id)
ORDER BY objeto;

SELECT 'servicos_catalogo' AS tabela, COUNT(*) AS registros FROM dbo.servicos_catalogo
UNION ALL SELECT 'servicos_filiais', COUNT(*) FROM dbo.servicos_filiais
UNION ALL SELECT 'aprovadores_edicao', COUNT(*) FROM dbo.aprovadores_edicao
UNION ALL SELECT 'categorias_custos', COUNT(*) FROM dbo.categorias_custos;
