import pyperclip
import atalhosPyautogui

from Componente import Componente


class Campo(Componente):
    """
    Representa um campo editável.

    Pode:
    - clicar no campo
    - preencher o campo
    - validar o texto preenchido
    """

    def __init__(
        self,
        coordenada_clique,
        coordenada_validacao=None,
        texto_validacao=None,
        texto_inserido=None
    ):
        super().__init__(coordenada_clique, coordenada_validacao)
        self.texto_validacao = texto_validacao
        self.texto_inserido = texto_inserido

    def clicar(self):
        atalhosPyautogui.clickar(self.coordenada_clique)

    def preencher(self, texto=None):
        texto_final = self.texto_inserido if texto is None else texto

        if texto_final is None:
            return

        pyperclip.copy(str(texto_final))
        atalhosPyautogui.colar(self.coordenada_clique)

    def validar(self):
        if self.texto_validacao is None:
            return True

        atalhosPyautogui.copiar(self.coordenada_validacao)
        texto_copiado = pyperclip.paste()
        return texto_copiado == self.texto_validacao