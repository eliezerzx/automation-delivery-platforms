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
    precoDesconto=str(round(precoDesconto,2)).replace('.','')
    pyautogui.doubleClick()
    pyautogui.typewrite(precoDesconto+"0")
keyboard.add_hotkey('shift', executar)
keyboard.wait('q')