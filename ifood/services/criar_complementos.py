import pyautogui
import pyperclip
import time
import os

pyautogui.PAUSE = 0.6

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_arquivo = os.path.join(diretorio_atual, '..', 'data', 'complemento.txt')


def adiciona_complemento(item, preco):
    # Vai para criar novo complemento
    pyautogui.click(1270, 432)
    time.sleep(0.5)

    # Seleciona o tipo do complemento
    pyautogui.click(1391, 527)
    pyautogui.click(1284, 437)
    time.sleep(0.2)

    # Clica no campo nome e cola o item
    pyautogui.click(1384, 621)
    pyautogui.moveTo(1444, 650, duration=0.3)
    pyautogui.click()
    pyperclip.copy(item)
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('tab')

    # Descricao
    pyautogui.write('Foto Ilustrativa.')
    time.sleep(0.2)

    if preco == '0':
        for _ in range(4):
            pyautogui.press('tab')
        pyautogui.press('enter')
    else:
        pyautogui.press('tab')
        pyautogui.press('tab')
        pyautogui.typewrite(preco)
        for _ in range(2):
            pyautogui.press('tab')
        pyautogui.press('enter')


def executar():
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        linhas = [l for l in arquivo.readlines() if l.strip()]

    for i, linha in enumerate(linhas, start=1):
        partes = linha.strip().split('|')
        if len(partes) != 2:
            print(f'[AVISO] Linha {i} com formato invalido: {linha.strip()}')
            continue

        item  = partes[0].strip()
        preco = partes[1].strip()

        print(f'[{i}] {item} -- R$ {preco}')
        adiciona_complemento(item, preco)

    pyautogui.alert('Pronto')


if __name__ == '__main__':
    executar()
