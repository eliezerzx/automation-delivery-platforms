import pyautogui
import time
import os
from utils import somErro

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

NOME_IMAGEM = os.path.join(BASE_DIR, "image", "botao_verde.png")
IMG_VALOR = os.path.join(BASE_DIR, "image", "valor_antigo.png")


def box_valido(box):

    #  Valida se o tamanho encontrado é parecido com o ícone esperado.

    return (
        10 <= box.width <= 40 and
        10 <= box.height <= 40
    )


def alterar_desconto():
    print("--- INICIANDO AUTOMAÇÃO ---")
    time.sleep(2)

    region = None
    tentativas_vazias = 0

    while True:
        print("\n🔍 Escaneando a tela em busca do ícone exato...")
        encontrou_neste_ciclo = False

        try:
            tags = list(pyautogui.locateAllOnScreen(
                NOME_IMAGEM,
                confidence=0.99,
                grayscale=False,
                region=region
            ))
        except Exception as e:
            print(f"Erro ao buscar imagem: {e}")
            tags = []

        if tags:
            print(f"Foram encontrados {len(tags)} ícones.")
        else:
            print("Nenhum ícone encontrado.")

        for box in tags:
            if not box_valido(box):
                print(f"❌ Ignorado: tamanho fora do padrão ({box.width}x{box.height})")
                continue

            x, y = pyautogui.center(box)
            print(f"✅ Ícone encontrado em ({x}, {y}) | tamanho: {box.width}x{box.height}")

            # Clica no ícone
            pyautogui.click(x, y)
            time.sleep(1)

            # Clica em remover
            pyautogui.click(1776, 985)
            time.sleep(5)

            # Altera o valor antigo
            try:
                print("\n🔍 Procurando campo valor_antigo.png...")
                campo = pyautogui.locateCenterOnScreen(
                    IMG_VALOR,
                    confidence=0.99
                )

                if campo:
                    print(f"✅ Campo valor encontrado em {campo}")
                    pyautogui.click(campo)
                    time.sleep(0.5)

                    pyautogui.hotkey("ctrl", "a")
                    time.sleep(0.5)

                    # Altera para valor novo
                    pyautogui.write("149,90", interval=0.05)
                    print("💰 Valor alterado")
                else:
                    print("❌ Campo valor não encontrado.")

            except Exception as e:
                print(f"Erro ao localizar valor_antigo.png: {e}")

            encontrou_neste_ciclo = True
            tentativas_vazias = 0

            time.sleep(1)
            break

        if not encontrou_neste_ciclo:
            tentativas_vazias += 1

            if tentativas_vazias == 1:
                print("⏬ Nenhum ícone encontrado. Rolando página...")
                pyautogui.scroll(-800)
                time.sleep(1)

            else:
                print("💤 Nenhum ícone pendente após scroll.")
                somErro.som_sucesso()
                pyautogui.alert("✅ Descontos removidos com sucesso!")
                break


if __name__ == "__main__":
    try:
        alterar_desconto()
    except KeyboardInterrupt:
        print("\n🛑 Programa encerrado pelo usuário.")
        somErro.som_erro()
        pyautogui.alert("❌ Programa encerrado pelo usuário.")
