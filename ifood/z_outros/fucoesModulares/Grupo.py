import alertas


class Grupo:
    """
    Classe base para grupos de automação.
    Centraliza clique, validação, alertas sonoros e tratamento de falhas.
    """

    def __init__(
        self,
        componentes=None,
        usar_som=True,
        falhar_com_excecao=True,
        callback_falha_coordenada=None
    ):
        self.componentes = componentes or {}
        self.usar_som = usar_som
        self.falhar_com_excecao = falhar_com_excecao
        self.callback_falha_coordenada = callback_falha_coordenada

    def adicionar_componente(self, nome, componente):
        self.componentes[nome] = componente

    def obter_componente(self, nome):
        if nome not in self.componentes:
            raise KeyError(f"Componente '{nome}' não encontrado.")
        return self.componentes[nome]

    def clicar(self, nome):
        componente = self.obter_componente(nome)
        componente.clicar()

    def validar(self, nome):
        componente = self.obter_componente(nome)
        return componente.validar()

    def executar_componente(self, nome, alertar_sucesso=False):
        componente = self.obter_componente(nome)
        componente.clicar()

        if not componente.validar():
            self._tratar_falha(nome)
            return False

        if alertar_sucesso and self.usar_som:
            alertas.sucesso()

        return True

    def executar_etapa(self, nome, descricao=None, alertar_sucesso=False):
        sucesso = self.executar_componente(nome, alertar_sucesso=alertar_sucesso)

        if sucesso:
            print(f"✅ Etapa concluída: {descricao or nome}")

        return sucesso

    def executar_sequencia(self, etapas, alertar_sucesso_final=False):
        for etapa in etapas:
            if isinstance(etapa, tuple):
                nome, descricao = etapa
            else:
                nome, descricao = etapa, None

            if not self.executar_etapa(nome, descricao=descricao):
                return False

        if alertar_sucesso_final and self.usar_som:
            alertas.sucesso()

        return True

    def _tratar_falha(self, nome):
        mensagem = f"❌ Validação falhou para o componente: {nome}"
        print(mensagem)

        if self.usar_som:
            alertas.problema()

        if self.callback_falha_coordenada:
            try:
                self.callback_falha_coordenada(nome)
            except Exception as e:
                print(f"Erro ao executar callback de falha de coordenada: {e}")

        if self.falhar_com_excecao:
            raise RuntimeError(mensagem)