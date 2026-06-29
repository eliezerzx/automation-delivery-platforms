import pyperclip
import atalhosPyautogui

from Componente import Componente


class Botao(Componente):
    """
    Representa um botão clicável.

    A validação pode ser feita por texto, quando houver
    texto de conferência configurado.
    """

    def __init__(self, coordenada_clique, coordenada_validacao=None, texto_validacao=None):
        super().__init__(coordenada_clique, coordenada_validacao)
        self.texto_validacao = texto_validacao

    def clicar(self):
        atalhosPyautogui.clickar(self.coordenada_clique)

    def validar(self):
        if self.texto_validacao is None:
            return True

        atalhosPyautogui.copiar(self.coordenada_validacao)
        texto_copiado = pyperclip.paste()
        return texto_copiado == self.texto_validacao