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

# Caminho absoluto para a pasta data/
DATA_PATH = os.path.join(root_path, 'data')

from utils import som  # Agora o Python saberá onde procurar

pyautogui.PAUSE = 0.5


    
def adiciona_item(item, descricao, preco, desconto):
    pyautogui.press('home')

    pyperclip.copy(item)
    # Clica no nome do item
    pyautogui.click(749, 406, duration=0.1) # Coordenadas do campo de nome do item
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)

    # Descrição do item
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyperclip.copy(descricao)
    pyautogui.hotkey("ctrl", "v")

    # Preço do item
    pyautogui.press('tab')
    pyautogui.click(1538, 553, duration=0.1)  # Clica no campo de editar o preço
    pyautogui.click(813, 691, duration=0.1)  # Clica no campo de preço
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('delete')
    pyautogui.write(preco, interval=0.05)
    pyautogui.press('tab')
    pyautogui.press('backspace')
    pyautogui.write(preco, interval=0.05)
    pyautogui.scroll(-600)  # Rola para baixo para garantir
    time.sleep(0.5)

    # Clica em "Concluir"
    pyautogui.moveTo(1530, 823, duration=0.1)
    pyautogui.click()
    time.sleep(1)

    # Clica em "Enviar"
    pyautogui.moveTo(1479, 972, duration=0.1)
    pyautogui.click()
    time.sleep(1)

def criaCardapio():
    try:
        pyautogui.hotkey("alt","tab")
        arquivo_pizza = os.path.join(DATA_PATH, 'pizza.txt')
        with open(arquivo_pizza, 'r', encoding='utf-8') as arquivo:
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