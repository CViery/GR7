-- Active: 1719254984580@@127.0.0.1@3306

CREATE TABLE IF NOT EXISTS boletos (num_nota, notas, fornecedor, data_vencimento,dia_vencimento, mes_vencimento, ano_vencimento, valor);

CREATE TABLE IF NOT EXISTS notas (emitido_para, status, boleto, num_nota, duplicata, fornecedor, data_emissao, dia_emissao, mes_emissao, ano_emissao,valor, despesa);

CREATE TABLE IF NOT EXISTS fornecedores (cnpj, razao, endereco);

CREATE TABLE IF NOT EXISTS despesas (despesa);

DROP TABLE notas;


UPDATE notas SET despesa = 'Peças'; 

DROP TABLE boletos;
INSERT INTO notas VALUES
('GR7', 'PENDENTE', 'SIM', '155877', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-01','15','1','2024', 564.25, 'Peças'),
('GR7', 'PAGO', 'SIM', '115599978', "", 'VIVO INTERNET - JANEIRO - 2024', '2024-01-01','15','1','2024', 179.99, 'Internet'),
('GR7', 'PAGO', 'NÃO', "", "", 'VALE TRANSPORTE - JAN. 2024', '2024-01-01','15','1','2024', 250.00, 'Vale Transporte'),
('GR7', 'PENDENTE', 'NÃO', "", "", 'FOLHA DE PAGAMENTO - JANEIRO - 24', '2024-01-01','15','1','2024', 33150.20, 'Folha de Pagamento'),
('GR7', 'PENDENTE', 'NÃO', "", "", 'PROVISIONAMENTO', '2024-01-01','15','1','2024', 6630.04, 'Provisão'),
('GR7', 'PENDENTE', 'NÃO', "", "", 'REFLÉXO - JANEIRO - 24', '2024-01-01','15','1','2024', 14000.00, 'Reflexo'),
('GR7', 'PENDENTE', 'SIM', '0720240393054053-8', "", 'DAS - DOCUMENTO DE ARRECADAÇAO DO SIMPLES NACIONAL - 12-2023', '2024-01-01','15','1','2024', 7502.41, 'TRIBUTOS'),
('GR7', 'PENDENTE', 'SIM', '0716240470395890-8', "", 'CONTRIBUIÇÃO PREVIDENCIÁRIA', '2024-01-01','15','1','2024', 1605.05, 'Encargos'),
('DANIEL ROSSETTI', 'PENDENTE', 'SIM', '573973581', "", 'ENEL - 674', '2024-01-01','15','1','2024', 308.33, 'Energia'),
('DANIEL ROSSETTI', 'PENDENTE', 'SIM', "", "", 'ENEL - 664', '2024-01-01','15','1','2024', 272.74, 'Energia'),
('GR7', 'PAGO', 'NÃO', '229095', "", 'FURACAO - F W DISTRIBUIDORA LTDA', '2024-01-02','15','1','2024', 247.32, 'Peças'),
('GR7', 'PAGO', 'NÃO', '229070', "", 'FURACAO - F W DISTRIBUIDORA LTDA', '2024-01-02','15','1','2024', 44.24, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '155718', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-02','15','1','2024', 1176.41, 'Peças'),
('GILBERTO', 'PAGO', 'NÃO', '100823', "", 'MAIS DIST VEIC S/A - JOAO DIAS', '2024-01-03','15','1','2024', 1948.00, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '310496', '025042', 'COMPEL AUTOMOTIVA LTDA', '2024-01-03','15','1','2024', 558.75, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '155876', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-03','15','1','2024', 117.62, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '156050', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-03','15','1','2024', 850.60, 'Peças'),
('GILBERTO', 'PAGO', 'NÃO', '100847', "", 'MAIS DIST VEIC S/A - JOAO DIAS', '2024-01-03','15','1','2024', 159.00, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '23700', "", 'KIKO PEÇAS E SERVIÇOS AUTOMOTIVOS LTDA', '2024-01-03','15','1','2024', 811.00, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '156130', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-03','15','1','2024', 1646.46, 'Peças'),
('DANIEL ROSSETTI', 'PAGO', 'NÃO', '9028', "", 'JJ DE OLIVEIRA AUTOMOTIVOS', '2024-01-03','15','1','2024', 444.99, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '16889', "", 'U. POWEL COMERCIO DE ALIMENTOS - ME', '2024-01-04','15','1','2024', 1140.00, 'Cesta Basica'),
('GR7', 'PENDENTE', 'SIM', '310669', "", 'COMPEL AUTOMOTIVA LTDA', '2024-01-04','15','1','2024', 628.80, 'Peças'),
('GILBERTO', 'PAGO', 'NÃO', '259460', "", 'GRAND MOTORS COMERCIO DE VEICULOS LTDA', '2024-01-05','15','1','2024', 82.80, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '98325', "", 'COBRA ROLAMENTOS E AUTOPEÇAS S/A', '2024-01-05','15','1','2024', 369.06, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '156472', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-05','15','1','2024', 186.17, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '310837', "", 'COMPEL AUTOMOTIVA LTDA', '2024-01-05','15','1','2024', 608.92, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '156627', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-05','15','1','2024', 501.23, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '156698', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-05','15','1','2024', 399.46, 'Peças'),
('GR7', 'PAGO', 'NÃO', '100986', "", 'MAIS DIST VEIC S/A - JOAO DIAS', '2024-01-05','15','1','2024', 125.51, 'Peças'),
('GR7', 'PAGO', 'NÃO', '25505', "", 'NAPRO ELETRONICA INDL LTDA', '2024-01-05','15','1','2024', 282.00, 'Peças'),
('CONSUMIDOR', 'PENDENTE', 'SIM', '823', "", 'LINO AUTO PEÇAS LTDA', '2024-01-05','15','1','2024', 768.51, 'Peças'),
('GR7', 'PENDENTE', 'SIM', "", "", 'ALUGUEL DO GALPÃO', '2024-01-05','15','1','2024', 18020.00, 'Aluguel'),
('GR7', 'PENDENTE', 'SIM', '310918', '251093', 'COMPEL AUTOMOTIVA LTDA', '2024-01-06','15','1','2024', 1352.55, 'Peças'),
('GR7', 'PAGO', 'SIM', '155758', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-06','15','1','2024', 19.30, 'Peças'),
('GR7', 'PAGO', 'SIM', '156204', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-06','15','1','2024', 350.00, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '057028', '237828', 'MARCO A. A. ALVES AUTOPECAS', '2024-01-06','15','1','2024', 524.00, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '177', "", 'JDC PNEUS LTDA', '2024-01-06','15','1','2024', 1080.00, 'Pneus'),
('GR7', 'PENDENTE', 'SIM', '156790', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-06','15','1','2024', 392.74, 'Peças'),
('GR7', 'PAGO', 'SIM', '156869', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-06','15','1','2024', 235.06, 'Peças'),
('GR7', 'PAGO', 'SIM', '100827', "", 'MAIS DIST VEIC S/A - JOAO DIAS', '2024-01-06','15','1','2024', 1948.00, 'Peças'),
('GR7', 'PAGO', 'SIM', '100903', "", 'MAIS DIST VEIC S/A - JOAO DIAS', '2024-01-06','15','1','2024', 44.24, 'Peças'),
('GR7', 'PAGO', 'SIM', '100905', "", 'MAIS DIST VEIC S/A - JOAO DIAS', '2024-01-06','15','1','2024', 625.00, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '156896', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-06','15','1','2024', 1504.86, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '156897', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-06','15','1','2024', 1380.57, 'Peças'),
('GR7', 'PAGO', 'SIM', '100910', "", 'MAIS DIST VEIC S/A - JOAO DIAS', '2024-01-06','15','1','2024', 86.51, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '156896', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-07','15','1','2024', 180.25, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '156897', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-07','15','1','2024', 105.54, 'Peças'),
('GR7', 'PAGO', 'SIM', '100926', "", 'MAIS DIST VEIC S/A - JOAO DIAS', '2024-01-07','15','1','2024', 185.00, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '157004', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-07','15','1','2024', 405.00, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '100927', "", 'MAIS DIST VEIC S/A - JOAO DIAS', '2024-01-07','15','1','2024', 200.00, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '157103', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-07','15','1','2024', 350.00, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '157104', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-07','15','1','2024', 125.00, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '157105', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-07','15','1','2024', 50.00, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '157106', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-07','15','1','2024', 150.00, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '157107', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-07','15','1','2024', 200.00, 'Peças'),
('GR7', 'PAGO', 'SIM', '100929', "", 'MAIS DIST VEIC S/A - JOAO DIAS', '2024-01-07','15','1','2024', 250.00, 'Peças'),
('GR7', 'PAGO', 'SIM', '100931', "", 'MAIS DIST VEIC S/A - JOAO DIAS', '2024-01-07','15','1','2024', 300.00, 'Peças'),
('GR7', 'PAGO', 'SIM', '100932', "", 'MAIS DIST VEIC S/A - JOAO DIAS', '2024-01-07','15','1','2024', 400.00, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '157201', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-07','15','1','2024', 75.00, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '157202', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-07','15','1','2024', 125.00, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '157203', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-07','15','1','2024', 150.00, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '157204', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-07','15','1','2024', 50.00, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '157205', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-07','15','1','2024', 100.00, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '157206', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-07','15','1','2024', 200.00, 'Peças'),
('GR7', 'PAGO', 'SIM', '100935', "", 'MAIS DIST VEIC S/A - JOAO DIAS', '2024-01-07','15','1','2024', 150.00, 'Peças'),
('GR7', 'PAGO', 'SIM', '100937', "", 'MAIS DIST VEIC S/A - JOAO DIAS', '2024-01-07','15','1','2024', 175.00, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '157208', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-07','15','1','2024', 125.00, 'Peças'),
('GR7', 'PENDENTE', 'SIM', '157209', "", 'PTD COMERCIO DE PEÇAS LTDA', '2024-01-07','15','1','2024', 100.00, 'Peças');





