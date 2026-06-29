from GrupoProduto import GrupoProduto


class FluxoProdutos:
    """
    Orquestra navegação pela lista + formulário do produto.
    """

    def __init__(self, callback_falha_coordenada=None):
        self.produto = GrupoProduto(callback_falha_coordenada=callback_falha_coordenada)
        self.lista = self.produto.lista

    def criar_a_partir_do_topo(self, nome_produto, descricao_produto, preco_produto, desconto_produto="0"):
        self.lista.esperar_carregamento_pagina(posicao_produto=0, preco="10,00")
        self.lista.duplicar_produto_da_lista(posicao_produto=0)
        self.produto.criar_produto(
            nome_produto=nome_produto,
            descricao_produto=descricao_produto,
            preco_produto=preco_produto,
            desconto_produto=desconto_produto
        )

    def editar_por_posicao(
        self,
        posicao_produto,
        nome_produto,
        descricao_produto,
        preco_produto,
        desconto_produto="0",
        tipo_alteracao=0,
        separador=" - ",
        soma=0
    ):
        self.lista.esperar_carregamento_pagina(posicao_produto=posicao_produto, preco="10,00")
        self.lista.editar_produto_da_lista(posicao_produto=posicao_produto)

        self.produto.editar_produto(
            nome_produto=nome_produto,
            descricao_produto=descricao_produto,
            preco_produto=preco_produto,
            desconto_produto=desconto_produto,
            tipo_alteracao=tipo_alteracao,
            separador=separador,
            tipo_operacao=1,
            soma=soma
        )