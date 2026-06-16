import pyautogui
#pega o retorno da posicao atual de x e y do mouse e passa o valor da tupla para as duas variaveis
def coordenada():
    x, y = pyautogui.position()
    print ("Posicao atual do mouse:")
    print ("x = "+str(x)+" y = "+str(y))

    #retorna True se x & y estiverem dentro da tela
    print ("\nEsta dentro da tela?")
    resp = pyautogui.onScreen(x, y)
    print (str(resp))