import pyautogui
import pyperclip
import keyboard
import time
from utils import somErro


# Tempo de segurança: se o código der loucura, jogue o mouse para o canto superior esquerdo da tela para parar.
pyautogui.FAILSAFE = True

def editar_produto():

    # Defina aqui quantas abas/páginas de produtos você quer alterar
    total_de_produtos = int(input("Digite o total de abas/páginas de produtos que deseja alterar: "))
    time.sleep(1)

    for i in range(total_de_produtos):
        print(f"Editando produto {i+1} de {total_de_produtos}...")

        # ----------------------------------------------------
        # PASSO 1: EDITAR O NOME DO PRODUTO
        # ----------------------------------------------------

        pyautogui.click(x=571, y=483) # clique no campo Nome
        
        # selecionar tudo no campo Nome, copiar, e reescrever adicionando o sufixo.
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.1)
        
        nome_atual = pyperclip.paste()
        novo_nome = f"{nome_atual} + Guaraná 1,5l"
        
        pyperclip.copy(novo_nome)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.2)

        # ----------------------------------------------------
        # PASSO 2: EDITAR A DESCRIÇÃO
        # ----------------------------------------------------
        # Pressiona TAB duas vezes para sair do campo Nome e ir para o campo Descrição
        pyautogui.press('tab')
        time.sleep(0.1)

        # Copia o texto atual da descrição
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.1)

        descricao_atual = pyperclip.paste()

        # Limpa o "Foto ilustrativa." antigo se ele existir para não duplicar
        if "Foto ilustrativa." in descricao_atual:
            descricao_limpa = descricao_atual.replace("Foto ilustrativa", "").strip()
        else:
            descricao_limpa = descricao_atual.strip()

        # Monta a nova descrição inserindo o texto antes de "Foto ilustrativa."
        nova_descricao = f"{descricao_limpa} Acompanha guaraná 1,5l. Foto ilustrativa."
        
        pyperclip.copy(nova_descricao)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.2)

        # ----------------------------------------------------
        # PASSO 3: SALVAR AS ALTERAÇÕES
        # ----------------------------------------------------
        pyautogui.click(x=1772, y=982) 
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
    editar_produto()