# Auditoria e otimização do sistema GR7

Data: 22/08/2026

## Resultado executivo

O pacote recebido ocupava aproximadamente **289 MB** quando extraído. O código útil, sem ambiente virtual, histórico Git, caches e logs, ocupava menos de **1 MB**. A versão otimizada mantém apenas os arquivos necessários para instalar e executar o sistema.

A lista de dependências foi reduzida de **100 pacotes declarados para 5 dependências diretas**. As dependências internas desses cinco pacotes continuam sendo instaladas automaticamente pelo `pip`.

## Escopo analisado

Foram revisados:

- 17 arquivos Python da aplicação original;
- 36 templates HTML/Jinja;
- 12 arquivos CSS e o JavaScript global;
- configuração Flask e sessões;
- camada de serviços;
- acesso ao SQL Server;
- exportações PDF e Excel;
- rotas de faturamento, gastos, cadastros, relatórios, Gerencial e Módulos;
- dois fluxos de implantação no Azure;
- dependências, ambiente virtual, logs, caches e arquivos de distribuição.

## Melhorias implementadas

### Peso e implantação

- Removidos da entrega: `venv`, `.git`, `__pycache__`, arquivos `.pyc`, log acumulado e instalador `.deb`.
- Removidos templates duplicados/sem rota e arquivos CSS vazios ou não referenciados; o arquivo original permanece preservado no pacote recebido.
- Corrigidos os workflows do Azure, que anteriormente incluíam o ambiente virtual dentro do `release.zip`.
- Adicionada validação de sintaxe e smoke tests antes de cada implantação.
- Atualizado `actions/setup-python` para a versão atual nos dois workflows.

### Dependências e memória

- Removidos Django, Selenium, Eel, PyInstaller, PostgreSQL, MySQL, Telegram, bibliotecas Azure não utilizadas e outros pacotes sem importação no código.
- Removidos Flask-Session e Redis, que estavam configurados mas nunca eram inicializados.
- Eliminado o uso de `pandas` e `numpy` para exportação simples de Excel.
- Exportação Excel reescrita com `openpyxl` em modo `write_only`, reduzindo consumo de memória.
- `xhtml2pdf` passou a ser carregado apenas quando um PDF é solicitado.

### Flask e inicialização

- `debug=True` deixou de ser fixo e agora depende de `FLASK_DEBUG`.
- Host, porta, chave secreta e cookie seguro podem ser configurados por ambiente.
- Adicionado cache de 24 horas para arquivos estáticos.
- Adicionado limite de 16 MB para requisições recebidas.
- Criado `.env.example` com as configurações necessárias.

### Banco de dados e desempenho

- Uma conexão SQL Server agora é reutilizada durante toda a requisição Flask e fechada automaticamente no final.
- Mantido o pooling nativo do `pyodbc`.
- Serviços auxiliares passaram a criar seus acessos ao banco somente quando realmente utilizados.
- Removida uma consulta duplicada de faturamento diário no dashboard.
- O resumo de Gastos deixou de executar uma consulta por categoria e subcategoria; agora usa uma única consulta agregada.
- Consultas de notas e boletos agora respeitam a unidade selecionada.
- Corrigido o uso incorreto de tabelas fixas no cadastro de notas.
- Corrigido `LIMIT 6`, incompatível com SQL Server, para `TOP 6`.
- Corrigida a consulta inválida `SELECT * FROM CREATE TABLE veiculos_modulos`.

### Funcionalidades corrigidas

- Reconstruído e registrado o módulo de Gastos, que estava fora da inicialização e possuía erros de sintaxe.
- Restauradas rotas de notas, boletos, duplicatas, despesas e consultas.
- Restauradas rotas de cadastros de fornecedores, companhias, funcionários, baterias e óleos.
- Corrigida a rota de novo orçamento, que apontava para um template inexistente.
- Corrigido erro de sintaxe Jinja em `cadastrar_faturamento.html`.
- Corrigida a exportação Excel: os filtros ficam na sessão e os dados são consultados apenas no momento da exportação.
- Corrigidas as rotas do Gerencial para Santo Amaro, Portal do Morumbi e Vila Andrade.
- Corrigido o formato de profissionais e serviços retornado ao JavaScript do Gerencial.
- Adicionadas proteções de autenticação nas rotas restauradas.

## Testes executados

- Compilação de todos os arquivos Python.
- Análise AST de todos os módulos Python.
- Parse dos 36 templates Jinja.
- Validação do JavaScript global.
- Importação da aplicação Flask sem abrir conexão com o banco.
- Verificação do registro de 53 rotas.
- Smoke tests das rotas críticas e dos redirecionamentos sem login.
- Verificação do conteúdo e da integridade do pacote final.

## Melhorias recomendadas para uma segunda etapa

Estas mudanças não foram aplicadas automaticamente porque dependem de validação no banco ou podem alterar regras de negócio:

1. Criar índices no SQL Server após medir o plano de execução, principalmente em:
   - faturamento por `ano_faturamento` e `mes_faturamento`;
   - faturamento por `mecanico` e `ano_faturamento`;
   - notas por `mes_emissao`, `ano_emissao`, `despesa` e `sub_categorias`;
   - boletos por data e número da nota.
2. Remover definitivamente a conexão legada do código depois de cadastrar `DB_CONNECTION_STRING` no Azure.
3. Migrar senhas de texto puro para hash seguro.
4. Dividir `app/routes.py`, `database/conection.py` e `database/gastos_db.py` em Blueprints e repositórios menores.
5. Criar testes de integração contra uma base Azure de homologação.
6. Consolidar CSS repetido e mover JavaScript/CSS inline dos templates maiores para arquivos estáticos com cache.
7. Hospedar localmente os recursos atualmente carregados por CDN para evitar dependência externa.

## Execução

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

Em produção, configure pelo menos `SECRET_KEY` e `DB_CONNECTION_STRING` conforme o arquivo `.env.example`.
