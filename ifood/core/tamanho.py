import pyautogui
import keyboard
import time
import pyperclip
import mouse
#Variaveis
categoria = 'Grande 8 pedaços'
precoDesconto = '4990'
precoOriginal = '7190'
x0 = 1661
y0 = 522
x1 = 1671
y1 = 604
x2 = 1662
y2 = 653
x3 = 1661
y3 = 644
xN = 1658
yN = 655

# pausa automática de 0.5s após cada ação do pyautogui
pyautogui.PAUSE = 0.5  
def esperaCarregar(y):
    pyautogui.doubleClick(1543,y)
    pyautogui.hotkey("ctrl", "c")
    preco = pyperclip.paste()
    if preco !='29,90':
        time.sleep(5)
        esperaCarregar(y)
    
def esperaNome():
    pyautogui.click(1116,550)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "c")
    decricao = pyperclip.paste()
    if len(decricao) > 80:
        time.sleep(5)
        esperaNome()
def copiarNome():
    pyautogui.click(868,517)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "c")
    return pyperclip.paste()
def executar():
    time.sleep(7)
    texto=copiarNome()
    if len(texto)>80:
        esperaNome()
        texto=copiarNome()
    partes = texto.split("-", 1)
    esquerda = partes[0].strip()
    direita = partes[1].strip()
    
    # Adiciona uma palavra antes do "-"
    novo_texto = esquerda +' - '+ categoria
    
    # Junta de novo
    pyperclip.copy(novo_texto)
    pyautogui.hotkey("ctrl", "v")
    
    # Abre aba 'Disponivel em'
    pyautogui.click(947,378)
    
    # Abre aba para trocar preço e desconto
    pyautogui.doubleClick(1130,679)
    
    # Clica 2 vezes no preço
    pyautogui.moveTo(1269,425)
    pyautogui.doubleClick()
    pyautogui.typewrite(precoOriginal)
    
    pyautogui.press('tab')
    pyautogui.typewrite(precoDesconto)
    
    # Clica no botão de salvar
    pyautogui.click(1810,985)
    pyautogui.click(1803,985)
    time.sleep(18)
def defineCoordenadaAlmodega(i):
    #Coordenadas para clicar no botão
    x=xN
    y=yN
    if i  == 0:
        x=x0
        y=y0
    elif i == 1:
        x=x1
        y=y1
    elif i == 2:
        x=x2
        y=y2
    elif i == 3:
        x=x3
        y=y3
    else:
        x=xN
        y=yN
    coordenada = [x,y]
    return coordenada
    
def executaVarias():
    qtd = int(input("Quantas Pizzas no total?"))
    i  = int(input("Preenche a partir de Qual pizza?"))-1
    for j in range(i,qtd):
        coordenada = defineCoordenadaAlmodega(j)
        esperaCarregar(coordenada[1])
        pyautogui.click(coordenada[0],coordenada[1])
        pyautogui.press('tab')
        pyautogui.press('enter')
        executar()
    pyautogui.alert("Pronto")

keyboard.add_hotkey('shift', executar)  
keyboard.add_hotkey('ctrl',executaVarias)
keyboard.wait('q')