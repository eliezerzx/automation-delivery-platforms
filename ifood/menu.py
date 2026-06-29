from services import criar_cardapio
from services import criar_complementos
from services import dois_sabores
from services import aplicar_desconto
from services import remover_desconto
from services import remov_desc_alt_valor
from services import alterar_nome_desc
from services import remov_grp_complementos
from utils import coordenada
from interfaces import interface
import teste

import pytesseract
from PIL import Image
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

    # ---- Executa opção "2" para rodar criaComplementos.py
    elif opcao == "2":
        barra_carregamento()
        criar_complementos.executar()

    # ---- Executa opção "3" para rodar dois_sabores.py
    elif opcao == "3":
        barra_carregamento()
        dois_sabores.executar()

    # ---- Executa opção "4" para rodar aplicar_desconto.py
    elif opcao == "4":
        barra_carregamento()
        aplicar_desconto.apli_desconto()
    
    # ---- Executa opção "5" para rodar remover_desconto.py
    elif opcao == "5":
        barra_carregamento()
        remover_desconto.remover_desconto()

    # ---- Executa opção "6" para rodar remover_desconto.py & alterar valor antigo
    elif opcao == "6":
        barra_carregamento()
        remov_desc_alt_valor.alterar_desconto()

    elif opcao == "7":
        barra_carregamento()
        alterar_nome_desc.editar_produto()

    elif opcao == "8":
        remov_grp_complementos.remov_complementos()

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
