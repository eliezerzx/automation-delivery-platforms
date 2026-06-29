from abc import ABC, abstractmethod


class Componente(ABC):
    """
    Classe base de todos os componentes da automação.

    Todo componente deve:
    - ter uma coordenada de clique
    - ter uma coordenada de validação (opcional)
    - saber clicar
    - saber validar
    """

    def __init__(self, coordenada_clique, coordenada_validacao=None):
        self.coordenada_clique = coordenada_clique
        self.coordenada_validacao = coordenada_validacao or coordenada_clique

    @abstractmethod
    def clicar(self):
        pass

    @abstractmethod
    def validar(self):
        pass