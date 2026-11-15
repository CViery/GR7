# Relatório de integração — Gerencial + GR7 Módulos

## Resultado

Os dois projetos foram consolidados em um único aplicativo Flask. O Gerencial
continua atendendo as filiais existentes e a filial 4 — GR7 Módulos abre o
painel operacional de módulos após o mesmo processo de autenticação.

## Alterações principais

- Registro da área de Módulos como blueprint /modulos.
- Proteção central das telas por usuário autenticado e filial 4.
- Redirecionamento de /home para o painel correto conforme a filial.
- Inclusão automática de GR7 Módulos no seletor de filiais caso o cadastro
  ainda não exista na tabela legada.
- Reutilização do usuário, perfil e logout do sistema Gerencial.
- Separação de Orçamentos e Vendas/OS na navegação.
- Preservação do fluxo Orçamento → Aprovação → OS → Finalização → Faturamento.
- Importação dos JSONs disponível somente por comando ou opção explícita.
- Compatibilidade do endereço legado /orcamentos/novo com a nova tela.
- Remoção da dependência funcional da camada inexistente modulos_db.

## Bancos de dados

Gerencial e GR7 Módulos usam o mesmo SQL Server configurado em
DB_CONNECTION_STRING. Os modelos do módulo foram vinculados às tabelas
clientes_modulos, veiculos_modulos, produtos_servicos_modulos,
categorias_gastos_modulos, vendas_modulos, itens_venda_modulos,
faturamento_modulos e gastos_modulos. Uma configuração SQLite antiga é
ignorada para evitar que o sistema volte a gravar dados localmente.

## Validação

- Compilação sintática de todos os arquivos Python: aprovada.
- Referências antigas main.* nos templates de Módulos: eliminadas.
- Arquivos JSON: mantidos apenas como carga inicial opcional.
- Testes de fumaça ampliados para login, filial e rotas de Módulos.

O teste HTTP completo requer a instalação das dependências de requirements.txt
e acesso ao ambiente de banco usado na implantação.
