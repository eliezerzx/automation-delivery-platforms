"""
Manipula produtos na tela da lista de produtos do cardápio.

Responsabilidades:
- esperar carregamento da lista
- selecionar produto pela posição
- abrir ação de editar ou duplicar
- validar preço na linha do produto

Regras:
- produto criado: sempre posição 0
- produto editado: posição varia entre 0 e n
- n2: segurança para quando estiver em outra posição/listagem
"""

import time
import pyautogui
import pyperclip
import atalhosPyautogui
import Coordenada

from Grupo import Grupo
from Botao import Botao
from Texto import Texto


class GrupoProdutoLista(Grupo):
    def __init__(self, callback_falha_coordenada=None):
        super().__init__(
            usar_som=True,
            falhar_com_excecao=True,
            callback_falha_coordenada=callback_falha_coordenada
        )
        self.coordenadas = Coordenada.carregarCoordenadas()
        self._montar_componentes()


    def _montar_componentes(self):
        c = self.coordenadas

        # Botões de 3 pontos por posição
        self.adicionar_componente("btn_3pontos_n2", Botao(c["btn_3Pontos_n2_lista"]))
        self.adicionar_componente("btn_3pontos_0", Botao(c["btn_3Pontos_0_lista"]))
        self.adicionar_componente("btn_3pontos_1", Botao(c["btn_3Pontos_1_lista"]))
        self.adicionar_componente("btn_3pontos_2", Botao(c["btn_3Pontos_2_lista"]))
        self.adicionar_componente("btn_3pontos_3", Botao(c["btn_3Pontos_3_lista"]))
        self.adicionar_componente("btn_3pontos_n1", Botao(c["btn_3Pontos_n1_lista"]))

        # Outros elementos
        self.adicionar_componente("btn_confirmar_duplicar", Botao(c["btn_confirmar_duplicar_lista"]))
        self.adicionar_componente("campo_pesquisa_produto", Texto(c["campo_pesquisa_produto"]))

    # =========================================================
    # UTILITÁRIOS
    # =========================================================

    def _nome_botao_por_posicao(self, posicao_produto):
        match posicao_produto:
            case -1:
                return "btn_3pontos_n2"
            case 0:
                return "btn_3pontos_0"
            case 1:
                return "btn_3pontos_1"
            case 2:
                return "btn_3pontos_2"
            case 3:
                return "btn_3pontos_3"
            case _:
                return "btn_3pontos_n1"

    def _chave_coordenada_3pontos(self, posicao_produto):
        match posicao_produto:
            case -1:
                return "btn_3Pontos_n2_lista"
            case 0:
                return "btn_3Pontos_0_lista"
            case 1:
                return "btn_3Pontos_1_lista"
            case 2:
                return "btn_3Pontos_2_lista"
            case 3:
                return "btn_3Pontos_3_lista"
            case _:
                return "btn_3Pontos_n1_lista"

    def _copiar_texto_na_coordenada(self, coordenada):
        atalhosPyautogui.copiar(coordenada)
        return pyperclip.paste().strip()

    def _obter_coordenada_preco_da_linha(self, posicao_produto=0):
        chave_3pontos = self._chave_coordenada_3pontos(posicao_produto)

        cord_ponto = self.coordenadas[chave_3pontos].getXY()
        x = cord_ponto[0]

        coord_preco = self.coordenadas["campo_preco_lista"].getXY()
        y = coord_preco[1]

        return (x, y)

    # =========================================================
    # VALIDAÇÃO DA LISTA
    # =========================================================

    def conferir_preco_na_lista(self, preco_esperado="10,00", posicao_produto=0):
        coord_preco_produto = self._obter_coordenada_preco_da_linha(posicao_produto)
        conteudo = self._copiar_texto_na_coordenada(coord_preco_produto)
        return conteudo == str(preco_esperado).strip()

    def esperar_carregamento_pagina(
        self,
        esperar_segundos=5,
        repeticao=0,
        preco="10,00",
        posicao_produto=0
    ):
        if repeticao >= 5:
            mensagem = "A página demorou muito para carregar. Verifique sua conexão ou se o site está fora do ar."
            print(mensagem)

            if self.usar_som:
                import alertas
                alertas.problema()

            if self.falhar_com_excecao:
                raise RuntimeError(mensagem)

            return False

        time.sleep(esperar_segundos)

        if self.conferir_preco_na_lista(preco, posicao_produto):
            print("✅ Lista carregada corretamente")
            return True

        return self.esperar_carregamento_pagina(
            esperar_segundos=esperar_segundos,
            repeticao=repeticao + 1,
            preco=preco,
            posicao_produto=posicao_produto
        )

    # =========================================================
    # AÇÕES NA LISTA
    # =========================================================

    def abrir_menu_produto(self, posicao_produto=0):
        nome_botao = self._nome_botao_por_posicao(posicao_produto)
        self.executar_etapa(nome_botao, f"Abrir menu do produto na posição {posicao_produto}")

    def selecionar_acao_menu(self, qtd_tab=1):
        atalhosPyautogui.tab(qtd_tab)
        time.sleep(0.1)
        pyautogui.press("enter")
        time.sleep(0.2)

    def selecionar_produto_na_lista(self, posicao_produto=0, qtd_tab=1, confirmar=False):
        """
        Abre o menu do produto e escolhe a ação com base na quantidade de TABs.

        Exemplos:
        - editar: qtd_tab conforme posição da opção "Editar"
        - duplicar: qtd_tab conforme posição da opção "Duplicar"

        confirmar=True é útil para duplicação.
        """
        self.abrir_menu_produto(posicao_produto)
        self.selecionar_acao_menu(qtd_tab=qtd_tab)

        if confirmar:
            self.executar_etapa("btn_confirmar_duplicar", "Confirmar duplicação")

    def editar_produto_da_lista(self, posicao_produto=0, qtd_tab_editar=1):
        self.selecionar_produto_na_lista(
            posicao_produto=posicao_produto,
            qtd_tab=qtd_tab_editar,
            confirmar=False
        )

    def duplicar_produto_da_lista(self, posicao_produto=0, qtd_tab_duplicar=2):
        self.selecionar_produto_na_lista(
            posicao_produto=posicao_produto,
            qtd_tab=qtd_tab_duplicar,
            confirmar=True
        )