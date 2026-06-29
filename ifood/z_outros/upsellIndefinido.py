import pyautogui
import keyboard
import time
import pyperclip
import mouse
import math
#Variaveis
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

# pausa automática de 0.5s após cada ação do pyautogui
pyautogui.PAUSE = 0.45  
def normaliza_preco(texto):
    return texto.replace('\n', '').replace('\xa0', ' ').strip()
def esperaCarregar(y, tentativa=0, max_tentativas=5):
    pyautogui.doubleClick(1543, y)
    pyautogui.hotkey("ctrl", "c")
    
    preco = normaliza_preco(pyperclip.paste())
    print(f"[Tentativa {tentativa}] Preço lido:", repr(preco))

    # Caso especial: preço com R$
    if preco.startswith("R$"):
        print("→ Preço com R$, usando yNormal")
        time.sleep(2)
        return esperaCarregar(yNormal, tentativa + 1)

    # Caso inválido / não carregou
    if "," not in preco or len(preco) > 9:
        if tentativa >= max_tentativas:
            print("⚠ Máx. tentativas atingidas, usando y original")
            return y
        time.sleep(5)
        return esperaCarregar(y, tentativa + 1)

    return y
def horario():
    pyautogui.moveTo(713,680,0.1)
    pyautogui.click()
    pyautogui.moveTo(1358,266,0.1)
    pyautogui.click()
    pyautogui.moveTo(1833,970,0.1)
    pyautogui.click()
def esperaNome():
    pyautogui.click(868,517)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "c")
    decricao = pyperclip.paste()
    if len(decricao) > 80:
        time.sleep(5)
        esperaNome()
def executar(categoria,valorAdd):
    time.sleep(4)
    esperaNome()
    print(categoria)
    if categoria != "":
        pyautogui.click(868,517)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.hotkey("ctrl", "c")
        texto = pyperclip.paste()
        if "-" in texto:
            if  "Coca" not in texto:
                if "+" in texto:
                    partes = [p.strip() for p in texto.split("+")]
                    partes[0] = partes[0] + " " + categoria
                    novo_texto = " + ".join(partes)
                else:
                    #partes = texto.split("-", 1)
                    partes = texto.split("-")
                    esquerda = partes[0].strip()
                    direita = partes[1].strip()
                    #novo_texto = esquerda+" Lanche "+direita+" "+categoria
                    # Adiciona uma palavra antes do "-"
                    esquerda_modificada = esquerda +' '+ categoria
                
                    # Junta de novo
                    novo_texto = esquerda_modificada + " - " + direita# Altera nome da categoria do Produto
            else:
                if "+" in texto:
                    partes = [p.strip() for p in texto.split("+")]
                    partes[0] = partes[0] + " " + categoria
                    novo_texto = " + ".join(partes)
        else:
            if "+" in texto:
                partes = [p.strip() for p in texto.split("+")]
                partes[0] = partes[0] + " " + categoria
                novo_texto = " + ".join(partes)
            elif "Marmita" in texto:
                print("Marmita")
                partes = texto.split("Marmita")
                print(partes)
                novo_texto = partes[0]+" "+categoria+partes[1]
                print(novo_texto)
            else:
                print("else")
                novo_texto =categoria+" "+texto
        pyperclip.copy(novo_texto)
        pyautogui.hotkey("ctrl", "v")
    if valorAdd != 0:
        # Abre aba 'Disponivel em'
        pyautogui.click(947,378)
        time.sleep(2)
        #horario()
        #Descobre precos
        pyautogui.click(1063,688)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.hotkey("ctrl", "c")
        precoDesconto = math.floor(float((pyperclip.paste()).replace(',','.'))+valorAdd)+0.9
        precoOriginal = math.floor(precoDesconto/0.5)+0.9
        precoDesconto=str(precoDesconto).replace('.','')+"0"
        precoOriginal = str(precoOriginal).replace('.','')+"0"
        # Abre aba para trocar preço e desconto
        pyautogui.moveTo(1131,689,0.1)
        pyautogui.doubleClick()
        
        # Clica 2 vezes no preço
        pyautogui.moveTo(1269,425,1.4)
        pyautogui.doubleClick()
        pyautogui.typewrite(precoOriginal)
        
        pyautogui.press('tab')
        pyautogui.typewrite(precoDesconto)
        
        # Clica no botão de salvar
        pyautogui.click(1810,985)
    pyautogui.click(1803,985)
    time.sleep(11)
def defineCoordenadaAlmodega(i):
    #Coordenadas para clicar no botão
    x=xN
    y=yN
    if i  == 0:
        x=x0
        y=y0
    elif i == 1:
        x=x1
        y=y1
    elif i == 2:
        x=x2
        y=y2
    elif i == 3:
        x=x3
        y=y3
    else:
        x=xN
        y=yN
    coordenada = [x,y]
    return coordenada
    
def executaVarias(qtd,i,categoria,valorAdd):
    for j in range(i,qtd):
        
        coordenada = defineCoordenadaAlmodega(j)
        time.sleep(3)
        coordenada[1] = esperaCarregar(coordenada[1])
        pyautogui.click(coordenada[0],coordenada[1])
        pyautogui.press('tab')
        pyautogui.press('enter')
        executar(categoria,valorAdd)
    pyautogui.alert("Pronto")