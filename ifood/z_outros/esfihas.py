import keyboard
import pyautogui
import pyperclip
pyautogui.PAUSE=0.5
def adiciona_complemento(item,descricao, preco):
    pyautogui.click(1270,432)
    pyautogui.click(1391,527)
    pyautogui.click(1284,437)
    pyautogui.click(1384,621)
    pyperclip.copy(item)
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press('tab')
    pyperclip.copy(descricao)
    pyautogui.hotkey("ctrl", "v")
    if preco == 0:
        for i in range(5):
            pyautogui.press('tab')
        pyautogui.press('enter')
    else:
        for i in range(2):              
            pyautogui.press('tab')
        pyautogui.typewrite(preco)
        for i in range(2):
            pyautogui.press('tab')
        pyautogui.press('enter')


with open('lista.txt', 'r', encoding='utf-8') as arquivo:
    linhas = arquivo.readlines()

for i, linha in enumerate(linhas, start=1):
    preco = '698'                         # Valor padrão, altere conforme necessário
    linha = linha.split('|')
    item  = linha[0].strip()
    descricao = linha[1].strip()
    adiciona_complemento(item, descricao, preco) 

keyboard.wait('q')