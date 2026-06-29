import pyautogui
import keyboard
import time
import pyperclip
import mouse
import math

# ===============================
# VARIÁVEIS DE COORDENADAS
# ===============================
x0 = 1664
y0 = 567
x1 = 1666
y1 = 635
x2 = 1669
y2 = 704
x3 = 1665
y3 = 703
xN = 1669
yN = 700
yNormal = 655

pyautogui.PAUSE = 0.45


# ===============================
# FUNÇÕES DE PREÇO
# ===============================
def arredonda_para_09(valor):
    return math.floor(valor) + 0.9


def calcula_precos(valor_base):
    preco_desconto = valor_base
    preco_original = arredonda_para_09(valor_base * 2)
    return preco_original, preco_desconto


# ===============================
# FUNÇÕES AUXILIARES
# ===============================
def normaliza_preco(texto):
    return texto.replace('\n', '').replace('\xa0', ' ').strip()


def esperaCarregar(y, tentativa=0, max_tentativas=5):
    # alterna o Y a cada 2 tentativas
    y_atual = y if (tentativa // 2) % 2 == 0 else yNormal

    pyautogui.doubleClick(1543, y_atual)
    pyautogui.hotkey("ctrl", "c")

    preco = normaliza_preco(pyperclip.paste())
    print(f"[Tentativa {tentativa}] y={y_atual} | Preço lido:", repr(preco))

    if "," in preco and len(preco) <= 9 and not preco.startswith("R$"):
        return y_atual

    if tentativa >= max_tentativas:
        print("⚠ Máx. tentativas atingidas, retornando último y usado")
        return y_atual

    time.sleep(3)
    return esperaCarregar(y, tentativa + 1, max_tentativas)
def esperaNome():
    pyautogui.click(868, 517)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "c")
    descricao = pyperclip.paste()

    if len(descricao) > 80:
        time.sleep(5)
        esperaNome()


# ===============================
# FUNÇÃO PRINCIPAL
# ===============================
def executar(categoria, valor_base):
    time.sleep(4)
    esperaNome()

    if categoria != "":
        pyautogui.click(868, 517)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.hotkey("ctrl", "c")
        texto = pyperclip.paste()

        if "-" in texto and "Coca" not in texto:
            if "+" in texto:
                partes = [p.strip() for p in texto.split("+")]
                partes[0] += " " + categoria
                novo_texto = " + ".join(partes)
            else:
                esquerda, direita = texto.split("-", 1)
                novo_texto = esquerda.strip() + " " + categoria + " - " + direita.strip()
        elif "+" in texto:
            partes = [p.strip() for p in texto.split("+")]
            partes[0] += " " + categoria
            novo_texto = " + ".join(partes)
        elif "Marmita" in texto:
            partes = texto.split("Marmita")
            novo_texto = partes[0] + " " + categoria + partes[1]
        else:
            novo_texto = categoria + " " + texto

        pyperclip.copy(novo_texto)
        pyautogui.hotkey("ctrl", "v")

    # ===============================
    # PREÇO FIXO CORRETO
    # ===============================
    if valor_base > 0:
        pyautogui.click(947, 378)
        time.sleep(2)

        precoOriginal, precoDesconto = calcula_precos(valor_base)

        precoDesconto = str(precoDesconto).replace('.', '') + "0"
        precoOriginal = str(precoOriginal).replace('.', '') + "0"

        pyautogui.moveTo(1131, 689, 0.1)
        pyautogui.doubleClick()

        pyautogui.moveTo(1269, 425, 1.4)
        pyautogui.doubleClick()
        pyautogui.typewrite(precoOriginal)

        pyautogui.press('tab')
        pyautogui.typewrite(precoDesconto)

        pyautogui.click(1810, 985)

    pyautogui.click(1803, 985)
    time.sleep(17)


# ===============================
# COORDENADAS
# ===============================
def defineCoordenadaAlmodega(i):
    if i == 0:
        return [x0, y0]
    elif i == 1:
        return [x1, y1]
    elif i == 2:
        return [x2, y2]
    elif i == 3:
        return [x3, y3]
    else:
        return [xN, yN]


# ===============================
# EXECUÇÃO EM LOTE
# ===============================
def executaVarias(qtd, inicio, categoria, valor_base):
    for j in range(inicio, qtd):
        coordenada = defineCoordenadaAlmodega(j)
        time.sleep(3)

        coordenada[1] = esperaCarregar(coordenada[1])
        pyautogui.click(coordenada[0], coordenada[1])

        pyautogui.press('tab')
        pyautogui.press('enter')

        executar(categoria, valor_base)

    pyautogui.alert("Pronto")


# ===============================
# CHAMADA
# ===============================
#executaVarias(42, 0, '', 44.9)