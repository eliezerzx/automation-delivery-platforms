from services import criar_cardapio
from services import cria_cardapioNEW
from services.painel_tkinter import PainelAutomacao
from interfaces import interface
from utils import coordenada

import sys
import time

# ----- BARRA DE CARREGAMENTO PARA TER UM  "TEMPO" DE CANCELAR CASO DIGITE OPCAO ERRADA -----
def barra_carregamento(texto="Carregando", duracao=2):
    total = 30  # tamanho da barra

    print(f"\n{texto}...\n")
    for i in range(total + 1):
        progresso = int((i / total) * 100)
        barra = "█" * i + "-" * (total - i)

        sys.stdout.write(f"\r[{barra}] {progresso}%")
        sys.stdout.flush()
        time.sleep(duracao / total)

    print("\n")
# ----- BARRA DE SAINDO -----
def barra_saindo(texto="Saindo", duracao=2):
    total = 30  # tamanho da barra

    print(f"\n{texto}...\n")
    for i in range(total + 1):
        progresso = int((i / total) * 100)
        barra = "█" * i + "-" * (total - i)

        sys.stdout.write(f"\r[{barra}] {progresso}%")
        sys.stdout.flush()
        time.sleep(duracao / total)

    print("\n")

interface.exibir_menu()

while True:
    interface.exibir_menu()
    opcao = input("Escolha a Opção: ")

    # ---- Executa opção "1" para rodar criaCardapio.py
    if opcao == "1":
        barra_carregamento()
        criar_cardapio.criaCardapio()

    # ---- Executa opção "2" para rodar cria_cardapioNEW.py
    elif opcao == "2":
        barra_carregamento()
        cria_cardapioNEW.criaCardapio()

    elif opcao == "3":
        app = PainelAutomacao()
        app.mainloop()

    # ---- Executa opção "9" para rodar coordenada.py
    elif opcao == "9":
        coordenada.coordenada()
        input("\nClique para Voltar...")

    # ---- Executa opção "0" para sair do programa.py
    elif opcao == "0":
        barra_saindo()
        break

    else:
        print("Opção inválida!")
