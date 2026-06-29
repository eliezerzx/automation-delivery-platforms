"""O arquivo contem o conjunto de funções que estrutura a criação e edição de um produto no iFood com a automação.
* Essa função cria apenas o produto, para que os adicionais sejam criados, usar em colaboração com o arquivo 'criarAdicional.py'.
* Nesse caso, criar um produto colocar nome, descrição e preço.
* Editar um produto, alterar o nome, descrição e preço.
* Favor, não colocar numeros de coordenadas fixas no código, usar o arquivo coordenada.json para tal.
* Dar preferência em usar e criar funções para manter a organização e limpeza do script.
Isabelly Faria - 05/02/2026 """
import atalhosPyautogui
import Coordenada
import time
import pyperclip
import pyautogui
coordenadas = Coordenada.carregarCoordenadas()

#Função para esperar o carregamento da página e verificar se a descrição do produto está presente
def esperarCarregamentoPagina(esperar_segundos=5,descricao_esperada="Descrição do produto",repeticao=0, acao=0):
    time.sleep(5)  # Espera 5 segundos para o carregamento da página
    match acao:
        case 0:
            coordenada = 'campo_descricao_criar_produto'
        case 1:
            coordenada = 'campo_descricao_editar_produto_1'
        case 2:
            coordenada = 'campo_descricao_editar_produto_2'
    atalhosPyautogui.copiar(coordenadas[coordenada])
    conteudo = pyperclip.paste()
    if conteudo.strip() == descricao_esperada:
        return True
    else:
        if repeticao >= 5:
            print("Não foi possivel reconhecer a descrição do produto, iremos recalibrar!")
            return False
        esperarCarregamentoPagina(esperar_segundos,descricao_esperada,repeticao + 1, acao)
        
def criarNomeDecricao(nome_produto,descricao_produto,preco_produto,acao=0,tipo_alteracao=0, separador=" - "):
    match acao:
        case 0:
            coordenada_nome = ['campo_nome_criar_produto','campo_descricao_criar_produto']
        case 1:
            coordenada_nome = ['campo_nome_editar_produto_1','campo_descricao_editar_produto_1']
        case 2:
            coordenada_nome = ['campo_nome_editar_produto_2','campo_descricao_editar_produto_2']
    if acao != 0:
        #Clica no campo de nome para ativar o campo de descrição
        atalhosPyautogui.copiar(coordenadas[coordenada_nome[0]])
        nome_produto = editar_nome(pyperclip.paste(), nome_produto, tipo_alteracao)
    #adiciona o nome do produto
    pyperclip.copy(nome_produto)
    print(pyperclip.paste())
    time.sleep(0.5)
    atalhosPyautogui.colar(coordenadas[coordenada_nome[0]])
    
    #adiciona a descrição do produto
    pyperclip.copy(descricao_produto)
    time.sleep(0.5)
    atalhosPyautogui.colar(coordenadas[coordenada_nome[1]])

#Função para clicar no botão de prosseguir para a próxima etapa da criação/edição do produto
def prosseguirPagina():
    #Clica no botão de prosseguir
    atalhosPyautogui.clickar(coordenadas['btn_prosseguir_produto'])

#Função para adicionar o preço do produto e o desconto
def adicionarPreco(preco_produto,desconto_produto,acao=0,soma=0):
    match acao:
        case 0:
            coordenada_nome = ['texto_nome_categoria_criar_produto']
        case 1:
            coordenada_nome = ['texto_nome_categoria_editar_produto_1']
        case 2:
            coordenada_nome = ['texto_nome_categoria_editar_produto_2']

    #Abre a seção de preço
    time.sleep(2)
    atalhosPyautogui.clickar(coordenadas[coordenada_nome[0]])

    #Dá respectivos tabs para chegar no preço
    for _ in range(2):
        pyautogui.press('tab')
    if soma == 1:
        pyautogui.hotkey('ctrl', 'c')
        valor_copiado = pyperclip.paste()
        valor_copiado = float(valor_copiado.replace(",", "."))
        preco_produto = valor_copiado + preco_produto
        preco_produto = f"{preco_produto:.2f}".replace(".", ",")
    elif soma == 2:
        pyautogui.hotkey('ctrl', 'c')
        valor_copiado = pyperclip.paste()
        valor_copiado = float(valor_copiado.replace(",", "."))
        preco_produto = valor_copiado * preco_produto
        preco_produto = f"{preco_produto:.2f}".replace(".", ",")
    else:
        preco_produto = f"{preco_produto:.2f}".replace(".", ",")
    pyautogui.press('tab')
    pyautogui.press('enter')
    if soma != 0:
        pyautogui.press('enter')

    #Adiciona o preço
    pyperclip.copy(preco_produto)
    time.sleep(0.5)
    atalhosPyautogui.colar(coordenadas['campo_preco_criar_produto'])

    #Adiciona o desconto
    pyperclip.copy(desconto_produto)
    time.sleep(0.5)
    pyautogui.press('tab')
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.hotkey('ctrl', 'v')

#Função para conferir se o preço do produto foi adicionado corretamente, para evitar erros de digitação, copiando o valor do campo de preço e comparando com o valor esperado
def conferirPreco(preco_esperado="10,00",coordenada_preco_produto='campo_desconto_criar_produto'):
    atalhosPyautogui.copiar(coordenadas[coordenada_preco_produto])
    conteudo = pyperclip.paste()
    if conteudo.strip() == preco_esperado:
        return True
    else:
        return False
    
#Função para clicar no botão de concluir a criação/edição do produto
def finalizarProduto():
    #Clica no botão de concluir
    atalhosPyautogui.clickar(coordenadas['btn_concluir_produto'])

#Função para validar qual ação o usuário deseja realizar, criar ou editar um produto, e se for editar, qual opção de edição escolher
def validarAcao(tipo_operacao):
    match tipo_operacao:
        case 0:
            return 0 #criar produto
        case 1:
            atalhosPyautogui.clickar(coordenadas['texto_nome_produto'],qtd=3)
            pyautogui.hotkey('ctrl', 'c')
            texto = pyperclip.paste()
            if texto == "Produto preparado":
                return 1  #editar produto - primeira opção
            else:
                return 2  #editar produto - segunda opção

def editar_nome(nome_atual, adicao, tipo_alteracao, separador):
    match tipo_alteracao:
        #Poe a adição no final do nome (Ex: X-Burger -> X-Burger Gourmet)
        case 0:
            novo_nome = nome_atual + " " + adicao
        #Poe adição após a primeira parte (Ex: Pizza Calabresa - Grande -> Pizza Calabresa Gourmet - Grande)    
        case 1:
            nomes = nome_atual.split(separador)
            if len(nomes) > 1:
                novo_nome = nomes[0] + " " + adicao + " - " + separador.join(nomes[1:])
            else:
                novo_nome = nome_atual + " " + adicao
        #Poe a adição no início do nome (Ex: Smash -> Burguer Smash)
        case 2:
            novo_nome = adicao + " " + nome_atual
        #substitui um termo (separador) por outro (Ex: X-Burger - Grande -> X-Burger - Gigante)
        case 3:
            novo_nome = nome_atual.replace(separador, " " + adicao + " ")
        #Substitui o nome atual pelo novo nome (Ex: X-Burger -> X-Burger Gourmet)
        case 4:
            novo_nome = adicao
    pyperclip.copy(novo_nome)
    time.sleep(0.5)