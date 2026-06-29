import time
import pyautogui
import pyperclip
import atalhosPyautogui
import Coordenada

from Grupo import Grupo
from Botao import Botao
from Campo import Campo
from Texto import Texto
from GrupoProdutoLista import GrupoProdutoLista


class GrupoProduto(Grupo):
    def __init__(self, callback_falha_coordenada=None):
        super().__init__(
            usar_som=True,
            falhar_com_excecao=True,
            callback_falha_coordenada=callback_falha_coordenada
        )
        self.coordenadas = Coordenada.carregarCoordenadas()
        self.lista = GrupoProdutoLista(callback_falha_coordenada=callback_falha_coordenada)
        self._montar_componentes()
        
    def _montar_componentes(self):
        c = self.coordenadas

        self.adicionar_componente("campo_nome_criar", Campo(c["campo_nome_criar_produto"]))
        self.adicionar_componente("campo_descricao_criar", Campo(c["campo_descricao_criar_produto"]))
        self.adicionar_componente("texto_categoria_criar", Botao(c["texto_nome_categoria_criar_produto"]))

        self.adicionar_componente("campo_nome_editar_1", Campo(c["campo_nome_editar_produto_1"]))
        self.adicionar_componente("campo_descricao_editar_1", Campo(c["campo_descricao_editar_produto_1"]))
        self.adicionar_componente("texto_categoria_editar_1", Botao(c["texto_nome_categoria_editar_produto_1"]))

        self.adicionar_componente("campo_nome_editar_2", Campo(c["campo_nome_editar_produto_2"]))
        self.adicionar_componente("campo_descricao_editar_2", Campo(c["campo_descricao_editar_produto_2"]))
        self.adicionar_componente("texto_categoria_editar_2", Botao(c["texto_nome_categoria_editar_produto_2"]))

        self.adicionar_componente("btn_prosseguir", Botao(c["btn_prosseguir_produto"]))
        self.adicionar_componente("btn_concluir", Botao(c["btn_concluir_produto"]))
        self.adicionar_componente("texto_nome_produto", Texto(c["texto_nome_produto"]))
        self.adicionar_componente("campo_preco", Campo(c["campo_preco_criar_produto"]))
        self.adicionar_componente("campo_desconto", Campo(c["campo_desconto_criar_produto"]))

    # ---------------------------------------------------------
    # UTILITÁRIOS
    # ---------------------------------------------------------

    def _copiar_texto_da_coordenada(self, chave_coordenada):
        atalhosPyautogui.copiar(self.coordenadas[chave_coordenada])
        return pyperclip.paste().strip()

    def _preencher_campo(self, nome_campo, valor, descricao=None):
        campo = self.obter_componente(nome_campo)

        campo.clicar()
        time.sleep(0.2)
        campo.preencher(valor)
        time.sleep(0.2)

        try:
            atalhosPyautogui.copiar(campo.coordenada_validacao)
            texto_copiado = pyperclip.paste().strip()

            if str(texto_copiado) != str(valor).strip():
                print(f"Valor esperado: {valor}")
                print(f"Valor copiado : {texto_copiado}")
                self._tratar_falha(nome_campo)
        except Exception:
            pass

        print(f"✅ Campo preenchido: {descricao or nome_campo}")

    def _pressionar_tab(self, quantidade=1):
        for _ in range(quantidade):
            pyautogui.press("tab")
            time.sleep(0.1)

    def _copiar_campo_atual(self):
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.2)
        return pyperclip.paste().strip()

    def _selecionar_todo_campo(self):
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.1)

    def _chave_coordenada_nome_por_acao(self, acao):
        mapa = {
            0: "campo_nome_criar_produto",
            1: "campo_nome_editar_produto_1",
            2: "campo_nome_editar_produto_2",
        }
        return mapa[acao]

    def _mapear_campos_por_acao(self, acao):
        mapa = {
            0: {
                "campo_nome": "campo_nome_criar",
                "campo_descricao": "campo_descricao_criar",
                "texto_categoria": "texto_categoria_criar",
                "chave_descricao": "campo_descricao_criar_produto",
            },
            1: {
                "campo_nome": "campo_nome_editar_1",
                "campo_descricao": "campo_descricao_editar_1",
                "texto_categoria": "texto_categoria_editar_1",
                "chave_descricao": "campo_descricao_editar_produto_1",
            },
            2: {
                "campo_nome": "campo_nome_editar_2",
                "campo_descricao": "campo_descricao_editar_2",
                "texto_categoria": "texto_categoria_editar_2",
                "chave_descricao": "campo_descricao_editar_produto_2",
            }
        }
        return mapa[acao]

    # ---------------------------------------------------------
    # DETECÇÃO DE AÇÃO
    # ---------------------------------------------------------

    def validar_acao(self, tipo_operacao):
        if tipo_operacao == 0:
            return 0

        self.clicar("texto_nome_produto")
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "c")
        texto = pyperclip.paste().strip()

        if texto == "Produto preparado":
            return 1

        return 2

    # ---------------------------------------------------------
    # CARREGAMENTO
    # ---------------------------------------------------------

    def esperar_carregamento_pagina(
        self,
        acao=0,
        descricao_esperada="Descrição do produto",
        esperar_segundos=5,
        max_tentativas=5
    ):
        dados = self._mapear_campos_por_acao(acao)

        for _ in range(max_tentativas):
            time.sleep(esperar_segundos)
            conteudo = self._copiar_texto_da_coordenada(dados["chave_descricao"])

            if conteudo == descricao_esperada:
                print("✅ Página carregada corretamente")
                return True

        mensagem = "Falha ao reconhecer carregamento da página do produto."
        print(mensagem)

        if self.usar_som:
            import alertas
            alertas.problema()

        if self.falhar_com_excecao:
            raise RuntimeError(mensagem)

        return False

    # ---------------------------------------------------------
    # REGRAS DE NOME
    # ---------------------------------------------------------

    def editar_nome(self, nome_atual, adicao, tipo_alteracao, separador=" - "):
        match tipo_alteracao:
            case 0:
                novo_nome = f"{nome_atual} {adicao}"
            case 1:
                partes = nome_atual.split(separador)
                if len(partes) > 1:
                    novo_nome = partes[0] + " " + adicao + separador + separador.join(partes[1:])
                else:
                    novo_nome = f"{nome_atual} {adicao}"
            case 2:
                novo_nome = f"{adicao} {nome_atual}"
            case 3:
                novo_nome = nome_atual.replace(separador, f" {adicao} ")
            case 4:
                novo_nome = adicao
            case _:
                novo_nome = nome_atual

        return novo_nome.strip()

    # ---------------------------------------------------------
    # CAMPOS
    # ---------------------------------------------------------

    def preencher_nome_descricao(
        self,
        nome_produto,
        descricao_produto,
        acao=0,
        tipo_alteracao=0,
        separador=" - "
    ):
        dados = self._mapear_campos_por_acao(acao)
        nome_final = nome_produto

        if acao != 0:
            nome_atual = self._copiar_texto_da_coordenada(self._chave_coordenada_nome_por_acao(acao))
            nome_final = self.editar_nome(nome_atual, nome_produto, tipo_alteracao, separador)

        self._preencher_campo(dados["campo_nome"], nome_final, "Nome do produto")
        self._preencher_campo(dados["campo_descricao"], descricao_produto, "Descrição do produto")

    def prosseguir_pagina(self):
        self.executar_etapa("btn_prosseguir", "Prosseguir para próxima etapa")

    def finalizar_produto(self):
        self.executar_etapa("btn_concluir", "Concluir produto", alertar_sucesso=True)

    # ---------------------------------------------------------
    # PREÇO
    # ---------------------------------------------------------

    def _obter_preco_calculado(self, preco_produto, soma=0):
        if soma == 0:
            return f"{float(preco_produto):.2f}".replace(".", ",")

        valor_copiado = self._copiar_campo_atual()
        valor_copiado = float(valor_copiado.replace(",", "."))

        if soma == 1:
            valor_final = valor_copiado + float(preco_produto)
        elif soma == 2:
            valor_final = valor_copiado * float(preco_produto)
        else:
            valor_final = float(preco_produto)

        return f"{valor_final:.2f}".replace(".", ",")

    def adicionar_preco(self, preco_produto, desconto_produto="0", acao=0, soma=0):
        dados = self._mapear_campos_por_acao(acao)

        time.sleep(2)
        self.executar_etapa(dados["texto_categoria"], "Abrir seção de preço")

        self._pressionar_tab(2)
        preco_final = self._obter_preco_calculado(preco_produto, soma=soma)

        self._pressionar_tab(1)
        pyautogui.press("enter")

        if soma != 0:
            pyautogui.press("enter")

        self._preencher_campo("campo_preco", preco_final, "Preço")

        campo_desconto = self.obter_componente("campo_desconto")
        campo_desconto.clicar()
        time.sleep(0.2)
        self._selecionar_todo_campo()
        pyperclip.copy(str(desconto_produto))
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.2)

        try:
            atalhosPyautogui.copiar(campo_desconto.coordenada_validacao)
            desconto_copiado = pyperclip.paste().strip()

            if desconto_copiado != str(desconto_produto).strip():
                print(f"Desconto esperado: {desconto_produto}")
                print(f"Desconto copiado : {desconto_copiado}")
                self._tratar_falha("campo_desconto")
        except Exception:
            pass

        print("✅ Campo preenchido: Desconto")

    # ---------------------------------------------------------
    # FLUXOS DE FORMULÁRIO
    # ---------------------------------------------------------

    def criar_produto(self, nome_produto, descricao_produto, preco_produto, desconto_produto="0"):
        acao = 0
        self.esperar_carregamento_pagina(acao=acao)
        self.preencher_nome_descricao(nome_produto, descricao_produto, acao=acao)
        self.prosseguir_pagina()
        self.adicionar_preco(preco_produto, desconto_produto, acao=acao)
        self.finalizar_produto()

    def editar_produto(
        self,
        nome_produto,
        descricao_produto,
        preco_produto,
        desconto_produto="0",
        tipo_alteracao=0,
        separador=" - ",
        tipo_operacao=1,
        soma=0
    ):
        acao = self.validar_acao(tipo_operacao)
        self.esperar_carregamento_pagina(acao=acao)
        self.preencher_nome_descricao(
            nome_produto,
            descricao_produto,
            acao=acao,
            tipo_alteracao=tipo_alteracao,
            separador=separador
        )
        self.prosseguir_pagina()
        self.adicionar_preco(preco_produto, desconto_produto, acao=acao, soma=soma)
        self.finalizar_produto()