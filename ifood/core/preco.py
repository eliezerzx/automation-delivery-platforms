import pyautogui
import keyboard
import time
import pyperclip
import mouse
#Variaveis
precoDesconto = '7299'
precoOriginal = '14690'
x0 = 1661
y0 = 497
x1 = 1652
y1 = 568
x2 = 1656
y2 = 632
x3 = 1667
y3 = 632
xN = 1660
yN = 636

# pausa automática de 0.5s após cada ação do pyautogui
pyautogui.PAUSE = 0.5 
def esperaCarregar(y):
    pyautogui.doubleClick(1530,y)
    pyautogui.hotkey("ctrl", "c")
    preco = pyperclip.paste()
    if preco !='29,90':
        time.sleep(5)
        esperaCarregar(y)
    
def esperaNome():
    pyautogui.click(1089,640)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "c")
    decricao = pyperclip.paste()
    if len(decricao) > 250:
        time.sleep(5)
        esperaNome()
def executar():
    time.sleep(5)
    esperaNome()
    # Abre aba 'Disponivel em'
    pyautogui.click(930,344)
    
    # Abre aba para trocar preço e desconto
    pyautogui.doubleClick(1138,655)
    
    # Clica 2 vezes no preço
    pyautogui.doubleClick(1285,388)
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