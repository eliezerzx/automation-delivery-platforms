import pyautogui
import pyperclip
import keyboard
import time
from utils import somErro


# Tempo de segurança: se o código der loucura, jogue o mouse para o canto superior esquerdo da tela para parar.
pyautogui.FAILSAFE = True

def remov_complementos():

    # Defina aqui quantas abas/páginas de produtos você quer alterar
    total_de_produtos = int(input("Digite o total de abas/páginas de produtos que deseja alterar: "))
    time.sleep(3)

    for i in range(total_de_produtos):
        print(f"Editando produto {i+1} de {total_de_produtos}...")

        pyautogui.click(x=683, y=326) # Grupo de complementos
        time.sleep(0.2)

        pyautogui.click(x=1369, y=641) # Abrir Seta
        pyautogui.sleep(0.2)
        pyautogui.click(x=1328, y=653) # Remover grupo de complementos
        pyautogui.sleep(0.2)
        pyautogui.click(x=1099, y=587) # Confirmar remoção

        pyautogui.click(x=1369, y=641) # Abrir Seta
        pyautogui.sleep(0.2)
        pyautogui.click(x=1328, y=653) # Remover grupo de complementos
        pyautogui.sleep(0.2)
        pyautogui.click(x=1099, y=587) # Confirmar remoção

        pyautogui.click(x=1369, y=641) # Abrir Seta
        pyautogui.sleep(0.2)
        pyautogui.click(x=1328, y=653) # Remover grupo de complementos
        pyautogui.sleep(0.2)
        pyautogui.click(x=1099, y=587) # Confirmar remoção
        pyautogui.sleep(0.2)

        pyautogui.click(x=564, y=571) # adicionar novo grupo de complementos
        pyautogui.click(x=1725, y=285) # Copiar grupo
        pyautogui.click(x=1824, y=968) # Continuar
        time.sleep(0.2)

        pyautogui.click(x=1258, y=359)# Buscar grupo para copiar
        pyautogui.write("Escolha Sua Borda:") # Nome do grupo a ser copiado
        pyautogui.sleep(2)
        pyautogui.click(x=1284, y=437) # Selecionar grupo encontrado
        pyautogui.click(x=1821, y=972) # Continuar
        pyautogui.sleep(0.2)
        pyautogui.click(x=1821, y=972) # Concluir
        pyautogui.sleep(0.7)

        pyautogui.click(x=1769, y=978) #salvar
        print("Aguardando salvar...")
        time.sleep(0.5)

        # ----------------------------------------------------
        # PASSO 4: IR PARA A PRÓXIMA ABA/PÁGINA DO NAVEGADOR
        # ----------------------------------------------------
        pyautogui.hotkey('ctrl', 'pgdn') # Ctrl + Page Down muda para a próxima aba
        time.sleep(0.5)
        
    somErro.som_sucesso()
    pyautogui.alert("✅ Cardápio finalizado com sucesso!")


# Executa a função
if __name__ == "__main__":
    remov_complementos()