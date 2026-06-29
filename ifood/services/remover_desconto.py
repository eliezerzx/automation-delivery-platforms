import pyautogui
import time
import os
from utils import somErro

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
NOME_IMAGEM = os.path.join(BASE_DIR, "image", "botao_verde.png")


def box_valido(box):
    """
    Valida se o tamanho encontrado é parecido com o ícone esperado.
    """
    return (
        10 <= box.width <= 40 and
        10 <= box.height <= 40
    )


def remover_desconto():
    print("--- INICIANDO AUTOMAÇÃO ---")
    time.sleep(3)

    region = None

    # ✅ CORREÇÃO: inicializa variável antes do loop
    tentativas_vazias = 0

    while True:
        print("\n🔍 Escaneando a tela em busca do ícone exato...")
        encontrou_neste_ciclo = False

        try:
            tags = list(pyautogui.locateAllOnScreen(
                NOME_IMAGEM,
                confidence=0.90,
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
            time.sleep(0.5)

            encontrou_neste_ciclo = True

            # ✅ Resetar tentativas vazias quando encontrar algo
            tentativas_vazias = 0

            time.sleep(2)
            break

        if not encontrou_neste_ciclo:
            tentativas_vazias += 1

            if tentativas_vazias == 1:
                print("⏬ Nenhuma ícone encontrada. Rolando página...")
                pyautogui.scroll(-800)
                time.sleep(2)

            else:
                print("💤 Nenhuma tag pendente após scroll.")
                somErro.som_sucesso()
                pyautogui.alert("✅ Descontos removidos com sucesso!")
                break


if __name__ == "__main__":
    try:
        remover_desconto()
    except KeyboardInterrupt:
        print("\n🛑 Programa encerrado pelo usuário.")
        somErro.som_erro()
        pyautogui.alert("❌ Programa encerrado pelo usuário.")
