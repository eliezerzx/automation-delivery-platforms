import time
import pyautogui
import Coordenada

from Grupo import Grupo
from Botao import Botao
from Campo import Campo


class GrupoAdicional(Grupo):
    def __init__(self):
        super().__init__(usar_som=True, falhar_com_excecao=True)
        self.coordenadas = Coordenada.carregarCoordenadas()
        self._montar_componentes()

    def _montar_componentes(self):
        c = self.coordenadas

        self.adicionar_componente("btn_adicionar_grupo", Botao(c["btn_adicionarGrupo_complemento"]))
        self.adicionar_componente("btn_criar_novo_grupo", Botao(c["btn_criarNovoGrupo_complemento"]))
        self.adicionar_componente("btn_continuar", Botao(c["btn_continuar_complemento"]))
        self.adicionar_componente("btn_ingredientes", Botao(c["btn_ingredientes_complemento"]))
        self.adicionar_componente("btn_concluir_grupo", Botao(c["btn_concluir_grupo_complemento"]))

        self.adicionar_componente("btn_criar_novo_complemento", Botao(c["btn_criarNovoComplemento_complemento"]))
        self.adicionar_componente("btn_selecionar_tipo", Botao(c["btn_selecionarTipo_complemento"]))
        self.adicionar_componente("btn_selecionar_ingrediente", Botao(c["btn_selecionar_ingrediente"]))
        self.adicionar_componente("btn_adicionar_ao_grupo", Botao(c["btn_adicionarAoGrupo_complemento"]))

        self.adicionar_componente("campo_nome_grupo", Campo(c["campo_nomeGrupo_complemento"]))
        self.adicionar_componente("campo_qtd_maxima", Botao(c["campo_qtdMaxima_complemento"]))
        self.adicionar_componente("campo_qtd_minima", Botao(c["campo_qtdMinima_complemento"]))

        self.adicionar_componente("campo_nome_complemento", Campo(c["campo_nome_complemento"]))
        self.adicionar_componente("campo_descricao_complemento", Campo(c["campo_descricao_complemento"]))
        self.adicionar_componente("campo_preco_complemento", Campo(c["campo_preco_complemento"]))

    def _clicar_varias_vezes(self, nome_componente, quantidade, espera=0.1):
        for i in range(int(quantidade)):
            self.executar_etapa(
                nome_componente,
                descricao=f"{nome_componente} - clique {i + 1} de {quantidade}"
            )
            time.sleep(espera)

    def _preencher_campo(self, nome_campo, valor, descricao=None):
        campo = self.obter_componente(nome_campo)

        campo.clicar()
        time.sleep(0.2)

        campo.preencher(valor)
        time.sleep(0.2)

        if not campo.validar():
            self._tratar_falha(nome_campo)

        print(f"✅ Campo preenchido: {descricao or nome_campo}")

    def _scroll(self, quantidade):
        pyautogui.scroll(quantidade)
        time.sleep(0.3)

    # --------------------------
    # Fluxo de grupo
    # --------------------------

    def iniciar_criacao_grupo(self):
        self.executar_sequencia([
            ("btn_adicionar_grupo", "Adicionar grupo"),
            ("btn_criar_novo_grupo", "Criar novo grupo"),
            ("btn_continuar", "Continuar criação do grupo"),
        ])

    def selecionar_tipo_ingrediente(self):
        self.executar_sequencia([
            ("btn_ingredientes", "Selecionar tipo ingrediente"),
            ("btn_continuar", "Confirmar tipo ingrediente"),
        ])

    def preencher_nome_grupo(self, nome):
        self._preencher_campo("campo_nome_grupo", nome, "Nome do grupo")

    def preencher_quantidades_grupo(self, minimo=0, maximo=1):
        self._clicar_varias_vezes("campo_qtd_maxima", maximo)
        self._clicar_varias_vezes("campo_qtd_minima", minimo)

    def salvar_grupo(self):
        self.executar_etapa("btn_continuar", "Salvar grupo")

    def concluir_grupo(self):
        self.executar_etapa("btn_concluir_grupo", "Concluir grupo", alertar_sucesso=True)

    def criar_novo_grupo(self, nome="Grupo de Adicionais", minimo=0, maximo=1):
        self.iniciar_criacao_grupo()
        self.selecionar_tipo_ingrediente()
        self.preencher_nome_grupo(nome)
        self.preencher_quantidades_grupo(minimo, maximo)
        self.salvar_grupo()

    # --------------------------
    # Fluxo de complemento
    # --------------------------

    def iniciar_criacao_complemento(self):
        self.executar_etapa("btn_criar_novo_complemento", "Criar novo complemento")
        time.sleep(2)

        self.executar_sequencia([
            ("btn_selecionar_tipo", "Abrir seleção de tipo"),
            ("btn_selecionar_ingrediente", "Selecionar ingrediente"),
        ])
        time.sleep(1)

    def preencher_nome_complemento(self, nome):
        self._preencher_campo("campo_nome_complemento", nome, "Nome do complemento")

    def preencher_descricao_complemento(self, descricao):
        self._preencher_campo("campo_descricao_complemento", descricao, "Descrição do complemento")

    def preencher_preco_complemento(self, preco):
        self._scroll(-300)
        self._preencher_campo("campo_preco_complemento", preco, "Preço do complemento")

    def salvar_complemento(self):
        self.executar_etapa("btn_adicionar_ao_grupo", "Adicionar complemento ao grupo")
        time.sleep(2)

    def criar_complemento(self, nome, descricao="", preco="0,00"):
        self.iniciar_criacao_complemento()
        self.preencher_nome_complemento(nome)

        if descricao:
            self.preencher_descricao_complemento(descricao)

        self.preencher_preco_complemento(preco)
        self.salvar_complemento()

    # --------------------------
    # Fluxo completo
    # --------------------------

    def criar_grupo_complementos(self, nome_grupo, complementos, minimo=0, maximo=1):
        self.criar_novo_grupo(nome_grupo, minimo, maximo)

        for item in complementos:
            self.criar_complemento(
                nome=item.get("nome", ""),
                descricao=item.get("descricao", ""),
                preco=item.get("preco", "0,00")
            )

        self.concluir_grupo()