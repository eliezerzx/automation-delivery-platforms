"""O arquivo contem o conjunto de funções que manipula produtos na tela da lista de produtos do cardápio.
* Essas funções são usadas para esperar o carregamento da página e selecionar produtos para editar ou duplicar.
* Favor, não colocar numeros de coordenadas fixas no código, usar o arquivo coordenada.json para tal.
* Dar preferência em usar e criar funções para manter a organização e limpeza do script.
Isabelly Faria - 04/02/2026 """
import atalhosPyautogui
import Coordenada
import time
import pyperclip
coordenadas = Coordenada.carregarCoordenadas()
def esperarCarregamentoPagina(esperar_segundos=5,coordenada_verificacao='campo_pesquisa_produto',repeticao=0,preco="10,00"):
    if repeticao >= 5:
        print("A página demorou muito para carregar. Verifique sua conexão ou se o site está fora do ar.")
        return
    time.sleep(esperar_segundos)  # Espera 5 segundos para o carregamento da página
    
    if not conferirPreco(preco,coordenada_verificacao):
        esperarCarregamentoPagina(esperar_segundos,coordenada_verificacao,repeticao + 1,preco)
def selecionarProdutoNaLista(posicao_produto=0,qtd_tab=1):
    match posicao_produto:
        case -1:
            atalhosPyautogui.clickar(coordenadas['btn_3Pontos_n2_lista'])
        case 0:
            atalhosPyautogui.clickar(coordenadas['btn_3Pontos_0_lista'])
        case 1:
            atalhosPyautogui.clickar(coordenadas['btn_3Pontos_1_lista'])
        case 2:
            atalhosPyautogui.clickar(coordenadas['btn_3Pontos_2_lista'])
        case 3:
            atalhosPyautogui.clickar(coordenadas['btn_3Pontos_3_lista'])
        case _:
            atalhosPyautogui.clickar(coordenadas['btn_3Pontos_n1_lista'])
    atalhosPyautogui.tab(qtd_tab)
    pyautogui.press('enter')
    time.sleep(0.1)
    atalhosPyautogui.clickar(coordenadas['btn_confirmar_duplicar_lista'])            

def conferirPreco(preco_esperado="10,00",coordenada_preco_produto='btn_3Pontos_0_lista'):
    cord_Ponto = coordenadas[coordenada_preco_produto].getXY()
    x = cord_Ponto[0]
    coord_preco = coordenadas['campo_preco_lista'].getXY()
    y = coord_preco[1]
    coord_preco_produto = (x,y)
    atalhosPyautogui.copiar(coord_preco_produto)
    conteudo = pyperclip.paste()
    if conteudo.strip() == preco_esperado:
        return True
    else:
        return False