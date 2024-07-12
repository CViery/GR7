-- Active: 1719254984580@@127.0.0.1@3306

CREATE TABLE IF NOT EXISTS boletos (num_nota, notas, fornecedor, data_vencimento,dia_vencimento, mes_vencimento, ano_vencimento, valor);

CREATE TABLE IF NOT EXISTS notas (emitido_para, status, boleto, num_nota, duplicata, fornecedor, data_emissao, dia_emissao, mes_emissao, ano_emissao, vencimentos ,valor, despesa);

CREATE TABLE IF NOT EXISTS fornecedores (cnpj, razao, endereco);

CREATE TABLE IF NOT EXISTS despesas (despesa);

DROP TABLE notas;


UPDATE notas SET despesa = 'Peças'; 

DROP TABLE boletos;




DROP TABLE faturamento;

CREATE TABLE faturamento (placa, modelo_veiculo, data_orcamento, data_faturamento,mes_faturamento, ano_faturamento, dias, num_os, cia, conversao_pneustore, pecas, servicos, valor_os, revitalizacao,aditivo, quantidade_aditivo, fluido_sangria, palheta ,limpeza_freios ,detergente_parabrisa, filtro,pneus ,bateria ,modelo_bateria,quantidade_oleo ,valor_oleo ,
tipo_marca_oleo,mecanico ,filtro_mecanico,valor_meta,valor_dinheiro ,freios ,suspensao ,injecao_ignicao ,cabecote_motor_arrefecimento ,outros ,
oleos ,transmissao);


CREATE TABLE IF NOT EXISTS funcionarios (id, nome);


INSERT INTO funcionarios VALUES (10, 'NATANAEL')


DELETE FROM funcionarios WHERE id = 7;

SELECT filtro_mecanico FROM faturamento WHERE filtro_mecanico = 'JUCIMAR'


CREATE TABLE companhias (cia);


INSERT INTO companhias VALUES ('PORTO'), ('AZUL'), ('ITAU'), ('ARVAL BRASIL'), ('ALD'), ('LETS');




CREATE TABLE servicos (servicos);

INSERT INTO servicos VALUES ('revitalizacao'), ('aditivo'), ('fluido_sangria'), ('palheta'), ('limpeza_freios'), ('detergente_parabrisa'), ('filtro'), ('pneus'), ('bateria');


CREATE TABLE funcionarios (id int, nome VARCHAR(50))