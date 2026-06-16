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

from utils import som  # Agora o Python saberá onde procurar

pyautogui.PAUSE = 0.5


def duplicar(): 

    # Clica nas 3 bolinhas para abrir o menu de opções do primeiro item
    pyautogui.click(1764, 655) # Coordenadas das 3 bolinhas
    time.sleep(0.2)

    # Clica no botão de copiar "duplicar" (ícone de duas folhas)
    pyautogui.click(1716, 835) # Coordenadas do botão de duplicar
    time.sleep(2)
    
def adiciona_item(item, descricao, preco, desconto):
    pyautogui.press('home')

    # Clica em duplicar item
    duplicar()

    pyperclip.copy(item)
    # Clica no nome do item
    pyautogui.moveTo(1407, 237, duration=0.1) # Coordenadas do campo de nome do item
    pyautogui.tripleClick()
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)

    # Descrição do item
    pyautogui.press('tab')
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyperclip.copy(descricao)
    pyautogui.hotkey("ctrl", "v")

    # Preço do item
    pyautogui.press('tab')
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.write(preco, interval=0.05)
    time.sleep(0.5)

    # Clica em "Enviar"
    pyautogui.moveTo(1827, 993, duration=0.1)
    pyautogui.click()
    time.sleep(3)

def criaCardapio():
    try:
        pyautogui.hotkey("alt","tab")
        with open('data/pizza.txt', 'r', encoding='utf-8') as arquivo:
            linhas = arquivo.readlines()

        print("Iniciando")

        for i, linha in enumerate(linhas, start=1):
            # Remove linhas vazias se houverem
            if not linha.strip():
                continue
                
            # CORREÇÃO AQUI: Agora divide a linha em 3 partes
            nome, descricao, preco_txt = linha.strip().split('|')
            
            descricao = descricao.strip() + " Foto Ilustrativa."
            
            # Converte o preço do arquivo (ex: "37,90") para float (ex: 37.90)
            preco_base = float(preco_txt.strip().replace(',', '.'))

            # Mantive a lógica matemática que estava no seu código original, 
            # mas agora usando o preço dinâmico vindo do arquivo txt
            desconto_valor = math.floor((preco_base + 0)) + 0.9 
            preco_valor = preco_base 

            item = f"{nome.strip()}"

            adiciona_item(
                item,
                descricao.strip(),
                f"{preco_valor:.2f}",
                f"{desconto_valor:.2f}"
            )

        som.som_sucesso()
        pyautogui.alert("✅ Cardápio finalizado com sucesso!")

    except Exception as e:
        som.som_erro()
        pyautogui.alert(f"❌ ERRO:\n{str(e)}")

if __name__ == "__main__":
    criaCardapio()