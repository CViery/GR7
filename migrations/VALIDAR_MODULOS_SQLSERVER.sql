SET NOCOUNT ON;

SELECT
    DB_NAME() AS banco_atual,
    SUSER_SNAME() AS login_sql,
    @@SERVERNAME AS servidor;

SELECT 'dbo.clientes_modulos' AS tabela, COUNT_BIG(*) AS registros FROM dbo.clientes_modulos
UNION ALL SELECT 'dbo.veiculos_modulos', COUNT_BIG(*) FROM dbo.veiculos_modulos
UNION ALL SELECT 'dbo.produtos_servicos_modulos', COUNT_BIG(*) FROM dbo.produtos_servicos_modulos
UNION ALL SELECT 'dbo.categorias_gastos_modulos', COUNT_BIG(*) FROM dbo.categorias_gastos_modulos
UNION ALL SELECT 'dbo.vendas_modulos', COUNT_BIG(*) FROM dbo.vendas_modulos
UNION ALL SELECT 'dbo.itens_venda_modulos', COUNT_BIG(*) FROM dbo.itens_venda_modulos
UNION ALL SELECT 'dbo.faturamento_modulos', COUNT_BIG(*) FROM dbo.faturamento_modulos
UNION ALL SELECT 'dbo.gastos_modulos', COUNT_BIG(*) FROM dbo.gastos_modulos
ORDER BY tabela;
