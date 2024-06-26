-- Active: 1719254984580@@127.0.0.1@3306

CREATE TABLE IF NOT EXISTS boletos (num_nota, notas, fornecedor, data_vencimento,dia_vencimento, mes_vencimento, ano_vencimento, valor);

CREATE TABLE IF NOT EXISTS notas (emitido_para, status, boleto, num_nota, duplicata, fornecedor, data_emissao, dia_emissao, mes_emissao, ano_emissao, despesa, valor);

CREATE TABLE IF NOT EXISTS fornecedores (cnpj, razao, endereco);

CREATE TABLE IF NOT EXISTS despesas (despesa);

DROP TABLE notas;


UPDATE notas SET despesa = 'Peças'; 

DROP TABLE boletos;