import pyperclip
import atalhosPyautogui

from Componente import Componente


class Texto(Componente):
    """
    Representa um bloco de texto da tela.

    Normalmente é usado para copiar/ler e validar.
    """

    def __init__(self, coordenada_clique, coordenada_validacao=None, texto_validacao=None):
        super().__init__(coordenada_clique, coordenada_validacao)
        self.texto_validacao = texto_validacao

    def clicar(self):
        atalhosPyautogui.copiar(self.coordenada_clique, qtd=3)

    def obter_texto(self):
        atalhosPyautogui.copiar(self.coordenada_validacao, qtd=3)
        return pyperclip.paste()

    def validar(self):
        if self.texto_validacao is None:
            return True

        texto_copiado = self.obter_texto()
        return texto_copiado == self.texto_validacao