# GR7 — Sistema Unificado

O sistema Gerencial e o GR7 Módulos agora executam no mesmo aplicativo Flask,
com um único login e uma única sessão.

## Acesso por filial

- Filial 1: GR7 Santo Amaro
- Filial 2: Portal
- Filial 3: GR7 Vila Andrade
- Filial 4: GR7 Módulos

Ao autenticar com a filial 4, o usuário é encaminhado para /modulos/. O
blueprint de Módulos também valida a sessão em todas as suas rotas.

## Instalação

    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    python app.py

No Linux ou macOS, ative o ambiente com: source venv/bin/activate

Configure as credenciais do SQL Server conforme .env.example. Gerencial e
Módulos usam a mesma DB_CONNECTION_STRING. A área de Módulos acessa as oito
tabelas com sufixo _modulos já existentes no SQL Server.

No Windows, copie o arquivo .env.example para .env, abra o novo arquivo e
substitua SERVIDOR, BANCO, USUARIO e SENHA pelos dados reais. O aplicativo
carrega esse arquivo automaticamente. Depois instale novamente as dependências:

    pip install -r requirements.txt

## Fluxo de Módulos

1. Orçamento
2. Inclusão de peças e serviços
3. Aprovação
4. Ordem de serviço
5. Finalização e faturamento
6. Relatórios

Para importar os JSONs manualmente em uma base vazia:

    flask --app app modulos-seed-json

O parâmetro --reset apaga e recria todas as tabelas de Módulos; use somente em
uma base de testes e após backup.

## Migração do faturamento e aprovação de edições

Antes de ativar os novos cadastros, execute no SQL Server:

    migrations/001_faturamento_custos_aprovacoes.sql

Se a migração ainda não tiver sido executada, o sistema detectará a ausência
da view nova e continuará lendo e gravando nas tabelas antigas. Nesse modo,
aprovações e edição controlada ainda não estarão disponíveis.

Depois, cadastre o e-mail do aprovador e vincule-o às filiais desejadas:

    UPDATE dbo.usuarios
    SET email = 'aprovador@empresa.com.br'
    WHERE usuario = 'USUARIO_APROVADOR';

    INSERT INTO dbo.aprovadores_edicao (usuario_id, filial_id, recebe_email)
    SELECT id, NULL, 1
    FROM dbo.usuarios
    WHERE usuario = 'USUARIO_APROVADOR';

Filial nula permite aprovar solicitações de todas as unidades. O e-mail é
opcional; mesmo sem SMTP, as solicitações aparecem na Central de Aprovações.

O fluxo de edição é:

1. Usuário solicita alteração e informa motivo e campos.
2. Aprovador aceita ou recusa dentro do GR7.
3. A aprovação libera somente a OS e o usuário solicitante por 30 minutos.
4. A autorização é consumida no primeiro salvamento.
5. Os valores anteriores e novos ficam na auditoria.

O solicitante nunca pode aprovar a própria solicitação.
