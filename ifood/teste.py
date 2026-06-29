# Dados fornecidos para o teste
dados = [												
    "Calabresa Especial | Molho de tomate, mussarela, calabresa fatiada e cebola | 27.90",		
    "Frango com Catupiry | Molho de tomate, mussarela, frango desfiado e catupiry | 29.90",		
    "Portuguesa | Molho de tomate, mussarela, presunto, ovos, cebola, azeitona e tomate | 39.90",	
    "Quatro Queijos | Molho de tomate, mussarela, provolone, parmesão e catupiry | 44.90 ",		
    "Camarão Premium | Molho de tomate, mussarela, camarão temperado e catupiry | 59.90"	
]

def processar_cardapio(lista_dados):
    cardapio_atualizado = []
    
    for linha in lista_dados:
        # Desestrutura a linha limpando os espaços (.strip()) usando list comprehension
        nome, descricao, preco_str = [item.strip() for item in linha.split('|')]
        preco = float(preco_str)
        
        # Define o tamanho com base no preço (if/elif/else enxuto)
        if preco <= 30.00:
            tamanho = "Broto 4 Pedaços"
        elif preco <= 50.00:
            tamanho = "Média 6 Pedaços"
        else:
            tamanho = "Grande 8 Pedaços"
            
        # Monta a nova string exatamente no formato solicitado pelo negócio
        nova_linha = f"\nPizza {nome} - {tamanho} | {descricao} Foto Ilustrativa | {preco_str}"
        cardapio_atualizado.append(nova_linha)
        
    return cardapio_atualizado

# Executa o processamento e exibe o resultado
for item in processar_cardapio(dados):
    print(item)