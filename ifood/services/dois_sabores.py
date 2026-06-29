import sys
import os
import keyboard
import pyautogui
import pyperclip
import time
import math

# --- BLOCO MÁGICO PARA CORRIGIR O CAMINHO ---
# Pega o caminho da pasta 'services' e sobe um nível para a raiz do projeto
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.append(root_path)
# --------------------------------------------

from utils import somErro  # Agora o Python saberá onde procurar

pyautogui.PAUSE = 0.6

pyautogui.PAUSE=0.6

def adiciona_complemento(item, descricao,preco='0'):
    #Clica em "Criar Novo Complemento"
    pyautogui.click(1341,445)
    time.sleep(3)
    #Clica Em "Selecione o Tipo"
    pyautogui.moveTo(1285,518,duration=0.2)
    pyautogui.click()
    time.sleep(0.4)
    #Clica em "Preparado"
    pyautogui.moveTo(1249,427,duration=0.2)
    pyautogui.click()
    time.sleep(1)
    #Clica no Campo de Nome do Produto
    pyautogui.moveTo(1259, 617, duration=0.2)  
    pyautogui.click()
    pyperclip.copy(item)
    time.sleep(1)
    print(pyperclip.paste())
    time.sleep(0.5)
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press('tab')
    pyperclip.copy(descricao)
    time.sleep(0.5)
    pyautogui.hotkey("ctrl", "v")
    if preco == '0':
        for i in range(4):
            pyautogui.press('tab')
        pyautogui.press('enter')
    else:
        print('Ola')           
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.typewrite(preco)
        for i in range(2):
            pyautogui.press('tab')
        pyautogui.press('enter')

def executar():
    try:
        
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(diretorio_atual, '..', 'data', 'pizza.txt')

        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            linhas = arquivo.readlines()
            linhas = arquivo.readlines()

        time.sleep(2)
        for i, linha in enumerate(linhas, start=1):

            linha = linha.split(' | ')
            item = "" + linha[0].strip()
            preco = f"{(float(linha[2].replace(",","."))):.2f}"
            #preco = linha[1]
            descricao = linha[1]+ " Foto Ilustrativa."

            adiciona_complemento(item, descricao, preco)

        somErro.som_sucesso()
        pyautogui.alert("✅ Complementos finalizados com sucesso!")

    except Exception as e:
        somErro.som_erro()
        pyautogui.alert(f"❌ ERRO:\n{str(e)}")

if __name__ == "__main__":
    executar()