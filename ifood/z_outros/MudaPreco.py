import pyautogui
import keyboard
import time
import pyperclip
import mouse
import math
#Variaveis
valorMult= 1.18

def executar():
    preco=float(input("Digite o preço:").replace(',','.'))
    precoDesconto = math.floor(preco*valorMult)+0.90
    precoOriginal = math.floor(precoDesconto/0.5)+0.90
    precoDesconto=str(round(precoDesconto,2)).replace('.','')
    precoOriginal = str(round(precoOriginal,2)).replace('.','')
    pyautogui.doubleClick(1285,388)
    pyautogui.typewrite(precoOriginal+"0")
    
    pyautogui.press('tab')
    pyautogui.typewrite(precoDesconto+"0")

    pyautogui.click(1810,985)
    pyautogui.click(1803,985)

keyboard.add_hotkey('shift', executar)
keyboard.wait('q')