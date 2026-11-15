/*
   Execute depois de 001_faturamento_custos_aprovacoes.sql.

   @filial_id = NULL: o usuário aprova alterações de todas as filiais.
   @filial_id = 1, 2 ou 3: o usuário aprova somente a filial informada.
*/
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @usuario NVARCHAR(50) = N'INFORME_O_USUARIO';
DECLARE @email NVARCHAR(255) = N'INFORME_O_EMAIL';
DECLARE @filial_id INT = NULL;
DECLARE @usuario_id INT;

IF @usuario = N'INFORME_O_USUARIO' OR @email = N'INFORME_O_EMAIL'
BEGIN
    THROW 51010, 'Preencha @usuario e @email antes de executar.', 1;
END;

IF @filial_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM dbo.filiais WHERE id = @filial_id)
BEGIN
    THROW 51011, 'A filial informada não existe.', 1;
END;

SELECT @usuario_id = id
FROM dbo.usuarios
WHERE usuario = @usuario;

IF @usuario_id IS NULL
BEGIN
    THROW 51012, 'O usuário aprovador não foi encontrado em dbo.usuarios.', 1;
END;

BEGIN TRY
    BEGIN TRANSACTION;

    UPDATE dbo.usuarios
    SET email = @email,
        ativo = 1
    WHERE id = @usuario_id;

    IF NOT EXISTS (
        SELECT 1
        FROM dbo.aprovadores_edicao
        WHERE usuario_id = @usuario_id
          AND ((filial_id = @filial_id) OR (filial_id IS NULL AND @filial_id IS NULL))
    )
    BEGIN
        INSERT INTO dbo.aprovadores_edicao (usuario_id, filial_id, recebe_email, ativo)
        VALUES (@usuario_id, @filial_id, 1, 1);
    END
    ELSE
    BEGIN
        UPDATE dbo.aprovadores_edicao
        SET recebe_email = 1,
            ativo = 1
        WHERE usuario_id = @usuario_id
          AND ((filial_id = @filial_id) OR (filial_id IS NULL AND @filial_id IS NULL));
    END;

    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF XACT_STATE() <> 0
        ROLLBACK TRANSACTION;
    THROW;
END CATCH;

SELECT u.id, u.usuario, u.email, a.filial_id, a.recebe_email, a.ativo
FROM dbo.aprovadores_edicao a
JOIN dbo.usuarios u ON u.id = a.usuario_id
WHERE a.usuario_id = @usuario_id
ORDER BY a.filial_id;
