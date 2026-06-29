import pyautogui
import keyboard
import time
import pyperclip
import mouse
import math
#Variaveis
valorMult = 6
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

def esperaCarregar(y):
    pyautogui.doubleClick(1543,y)
    pyautogui.hotkey("ctrl", "c")
    preco = pyperclip.paste()
    if len(preco)>5:
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
    else:
        print(decricao)
# pausa automática de 0.5s após cada ação do pyautogui
pyautogui.PAUSE = 0.5  

def executar():
    # Abre aba 'Disponivel em'
    pyautogui.click(947,378)

    #Descobre precos
    pyautogui.click(1080,688)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "c")
    precoDesconto = math.floor(float((pyperclip.paste()).replace(',','.'))+valorMult)+0.9
    precoOriginal = math.floor(precoDesconto/0.7)+0.9
    precoDesconto=str(precoDesconto).replace('.','')+'0'
    precoOriginal = str(precoOriginal).replace('.','')+'0'
    
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
    time.sleep(9)
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