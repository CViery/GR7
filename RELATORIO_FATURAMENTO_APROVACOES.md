# Faturamento novo e aprovação de edições

## Mudança de origem

Novas OS das filiais 1, 2 e 3 passam a ser gravadas em `faturamento_novo`.
A view `vw_faturamento_compat` permite que os relatórios atuais leiam os
registros antigos e os novos durante a migração, sem duplicar uma OS já
migrada.

A chave operacional passa a ser `(filial_id, num_os)`, pois números de OS
podem se repetir entre filiais.

## Serviços do Portal

O cadastro mantém compatibilidade com o formulário atual, mas grava cada
serviço com significado próprio em `faturamento_servicos`:

| Coluna legada | Filiais 1 e 3 | Filial 2 - Portal |
|---|---|---|
| aditivo | Aditivo | Ar-condicionado |
| fluido_sangria | Fluido/Sangria | Lavagem |
| palheta | Palheta | Alternador/Motor de arranque |
| limpeza_freios | Limpeza dos freios | Funilaria |

## Aprovação de edição

1. O usuário seleciona a OS e solicita a edição.
2. Informa o motivo e os grupos de campos que pretende alterar.
3. Aprovadores recebem notificação interna e, opcionalmente, e-mail.
4. A decisão exige login no GR7; links de e-mail não aprovam diretamente.
5. A aprovação vale por 30 minutos, para a OS, o usuário e os campos pedidos.
6. O solicitante realiza um único salvamento.
7. A autorização é consumida e os dados anteriores e novos são auditados.

O solicitante não pode aprovar o próprio pedido. Registros antigos exibem a
identificação "Registro antigo" e serão editáveis somente depois da migração.

## Segurança

- Formulários de solicitação, decisão e edição possuem token contra CSRF.
- A permissão é validada novamente no servidor no momento do salvamento.
- Campos não solicitados são preservados mesmo se forem manipulados no HTML.
- Credenciais de banco foram removidas do código-fonte; use
  `DB_CONNECTION_STRING` no ambiente.
- Recomenda-se trocar a credencial que esteve anteriormente incorporada no
  código antes da implantação desta versão.

## Ativação

1. Faça backup do SQL Server.
2. Execute `migrations/001_faturamento_custos_aprovacoes.sql` em homologação.
3. Configure o e-mail dos usuários aprovadores.
4. Cadastre os aprovadores em `aprovadores_edicao`.
5. Configure as variáveis SMTP se desejar e-mail.
6. Valide cadastro, consulta, aprovação, edição e relatórios.
7. Somente então execute a migração em produção.
