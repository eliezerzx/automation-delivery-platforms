"""O arquivo contém funções de ações repetidas multiplas vezes feitas pelos arquivos. 
* Dar preferência em usar e criar funções para manter a organização e limpeza do script
Isabelly Faria - 20/01/2026"""
import pyautogui
import pyperclip
import time
def copiar(coordenada_click, qtd=1):
    clickar(coordenada_click, qtd=qtd)
    pyautogui.hotKey('ctrl', 'a')
    pyautogui.hotKey('ctrl', 'c')
    return pyperclip.paste()

def clickar(coordenada_click, y=None, qtd=1, btn='left', duracao=0.1, retries=1, interval=0.1):
    """
    Click at a coordinate.

    Accepts:
      - a tuple/list/object with (x, y): clickar((x,y), ...)
      - separate x and y as first two positional args: clickar(x, y, ...)
      - an object with attributes .x and .y (e.g., Coordenada)

    retries and interval control retry attempts on failure.
    """
    # normalize coordinates
    if y is not None:
        x = coordenada_click
        y_val = y
    else:
        # try object with .x/.y
        try:
            x = coordenada_click.x
            y_val = coordenada_click.y
        except Exception:
            try:
                x = coordenada_click[0]
                y_val = coordenada_click[1]
            except Exception:
                raise ValueError("coordenada_click must be (x, y), separate x,y, or object with .x and .y")

    last_exc = None
    for attempt in range(retries):
        try:
            pyautogui.moveTo(x, y_val, duration=duracao)
            pyautogui.click(clicks=qtd, button=btn)
            return True
        except Exception as e:
            last_exc = e
            if attempt < retries - 1:
                time.sleep(interval)
            else:
                raise

def colar(coordenada_click, texto=None, qtd=1):
    if texto is not None:
        pyperclip.copy(texto)
    clickar(coordenada_click, duracao=0.3, qtd=qtd)
    pyautogui.hotKey('ctrl', 'a')
    pyautogui.hotKey('ctrl', 'v')

def tab(qtd=1):
    for _ in range(qtd):
        pyautogui.press('tab')
