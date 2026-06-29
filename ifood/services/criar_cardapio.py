import pyautogui
import time
import os
import sys
import pyperclip
import keyboard
import math

# --- BLOCO MÁGICO PARA CORRIGIR O CAMINHO ---
# Pega o caminho da pasta 'services' e sobe um nível para a raiz do projeto
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.append(root_path)
# --------------------------------------------

from utils import somErro  # Agora o Python saberá onde procurar

pyautogui.PAUSE = 0.5


def duplicar(): 

    #Clica nas 3 bolinhas do 1º item
    pyautogui.moveTo(1644, 480, duration=0.1)
    pyautogui.click()
    for i in range(2):
        pyautogui.press('tab')
        time.sleep(0.1)
    pyautogui.press('enter')
    time.sleep(4)
    # Confirma duplicação (Botão confirmar duplicação)
    pyautogui.moveTo(1124, 633, duration=0.1)
    pyautogui.click()
    time.sleep(2)

def esperaCarregar(sucess=0, tentativas=5): 
    print(sucess)
    pyautogui.press('home')
    pyperclip.copy('')
    # Clica no preço do 1º item
    pyautogui.moveTo(1501, 484, duration=0.1)
    pyautogui.doubleClick()
    print(pyautogui.position())  
    pyautogui.hotkey("ctrl", "c")
    preco = pyperclip.paste()
    if preco != "10,00":
        time.sleep(3)
        esperaCarregar()
    elif sucess < 2:
        sucess += 1
        esperaCarregar(sucess)
def esperaNome(tentativa = 0):
    # Clica no nome do 1º item
    pyautogui.moveTo(1025, 625, duration=0.1)
    pyautogui.click()
    
    if tentativa > 3:
        #Clica em (Cadápio), no canto superior esquerdo
        pyautogui.moveTo(501, 187, duration=0.1)
        pyautogui.click()
        time.sleep(1)
        #Confirmar que deseja sair da criação
        pyautogui.moveTo(1137, 569, duration=0.1)
        pyautogui.click()
        esperaCarregar()
        duplicar()
        esperaNome()
    pyperclip.copy('')
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "c")
    descricao = pyperclip.paste()
    if descricao != 'Teste1':
        time.sleep(3)
        esperaNome(tentativa+1)
    
def adiciona_item(item, descricao, preco, desconto):
    pyautogui.press('home')
    esperaCarregar()

    # Clica em duplicar item
    duplicar()

    esperaNome()
    pyperclip.copy(item)
    # Clica no nome do item
    pyautogui.moveTo(613, 507, duration=0.1)
    pyautogui.click()
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)

    # Descrição
    pyautogui.press('tab')
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyperclip.copy(descricao)
    pyautogui.hotkey("ctrl", "v")

    # Clicar em "Prosseguir"
    pyautogui.moveTo(1796, 979, duration=0.1)
    pyautogui.click()
    pyautogui.click()

    # Abre preço
    time.sleep(1)
    #Clicar no Nome da categoria (Na linha do preço)
    pyautogui.moveTo(569, 648, duration=0.1)
    pyautogui.click()
    for _ in range(2):
        pyautogui.press('tab')
    pyautogui.typewrite(str(preco))

    '''pyautogui.press("enter")

    # Clica no primeiro campo
    pyautogui.moveTo(1283, 414, duration=0.1)
    pyautogui.click()
    
    pyautogui.press('tab')
    pyautogui.typewrite(str(desconto))
    for i in range(2):
        pyautogui.press('tab')
    pyautogui.press('enter')'''

    # Clica em Salvar
    pyautogui.moveTo(1796, 979, duration=0.1)
    pyautogui.click()
    time.sleep(3)

def criaCardapio():
    try:
        pyautogui.hotkey("alt","tab")
        with open('data/pizza.txt', 'r', encoding='utf-8') as arquivo:
            linhas = arquivo.readlines()

        print("Iniciando")

        for i, linha in enumerate(linhas, start=1):
            nome, descricao = linha.strip().split('|')
            descricao = descricao.strip() +""
            #desconto_valor = float(preco)
            #preco.replace(",",".").strip()
            desconto_valor = math.floor((float(4.90)+0))+0.9 
            preco_valor = math.floor(desconto_valor/0.5)+0.9

            item = f"{nome.strip()}"

            adiciona_item(
                item,
                descricao.strip(),
                f"{preco_valor:.2f}".replace('.', ','),
                f"{desconto_valor:.2f}".replace('.', ',')
            )

        somErro.som_sucesso()
        pyautogui.alert("✅ Cardápio finalizado com sucesso!")

    except Exception as e:
        somErro.som_erro()
        pyautogui.alert(f"❌ ERRO:\n{str(e)}")

if __name__ == "__main__":
    criaCardapio()