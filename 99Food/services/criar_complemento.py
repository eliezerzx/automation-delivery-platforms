import pyautogui
import time
import os
import sys
import pyperclip
import keyboard
import math

pyautogui.PAUSE = 0.5

pyautogui.click(924, 775, duration=0.1) # Coordenadas do campo de novo item

pyautogui.click(721, 388, duration=0.1) # Coordenadas do nome do item
pyautogui.write("Coca-cola", interval=0.05)

# Categoria do item
pyautogui.press('tab')
pyautogui.press('tab')
pyautogui.press('enter')
pyautogui.press('up')
pyautogui.press('enter')

# Preço do item
pyautogui.press('tab')
pyautogui.write("10.00", interval=0.05)

pyautogui.click(1232, 908, duration=0.1) # Coordenadas do botão de Confirmar
