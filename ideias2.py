# Supondo que valor_soma seja um número
valor_soma = 1230.5

# Formatando o valor para o formato desejado
valor_formatado = f'R$ {valor_soma:.2f}'
valor_formatado = valor_formatado.replace('.', ',')  # Substitui o ponto por vírgula

# Verifica se há necessidade de inserir o ponto de milhar
if '.' in valor_formatado:
    partes = valor_formatado.split(',')
    parte_inteira = partes[0].replace('.', '')
    parte_decimal = partes[1]
    valor_formatado = f'R$ {parte_inteira}.{parte_decimal}'

print(valor_formatado)