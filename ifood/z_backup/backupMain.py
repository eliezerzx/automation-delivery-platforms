from z_outros import funcionalidadeSecundaria
from z_outros import upsellDefinido
from z_outros import upsellIndefinido
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# Pasta para salvar os arquivos
PASTA_DADOS = "dados"
os.makedirs(PASTA_DADOS, exist_ok=True)

# Variáveis globais
dados_categoria = {}
dados_complemento = {}
dados_nome = {}
dados_tamanho = {}
dados_preco = {}
dados_upsell = {}

# Função que limpa e mostra novo conteúdo no frame principal
def mostrar_pagina(conteudo):
    for widget in frame_conteudo.winfo_children():
        widget.destroy()
    conteudo()

# Função auxiliar para validar formatação NomeItem | Descricao
def validar_txt(caminho):
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            for linha in f:
                if "|" not in linha:
                    return False
        return True
    except:
        return False

# Função para salvar arquivo
def salvar_arquivo(nome, conteudo):
    caminho = os.path.join(PASTA_DADOS, nome)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)
    messagebox.showinfo("Sucesso", f"Dados salvos em {caminho}")

# Página inicial
def pagina_inicial():
    label_boasVindas = tk.Label(frame_conteudo, text="Bem-vindo!", font=("Arial", 14))
    label_boasVindas.pack(pady=10)

    texto_introducao = """Essa aplicação otimiza a construção de cardápios no iFood, a partir de algumas instruções.
Ela utiliza as coordenadas específicas para um monitor 1920x1080, para outra resolução, clique abaixo para configurar. (Função Indisponivel)"""
    label_texto = tk.Label(frame_conteudo, text=texto_introducao, wraplength=800, font=("Arial",12))
    label_texto.pack(pady=10)

    botao = tk.Button(frame_conteudo, text="Configurar Coordenadas",
                      command=lambda: messagebox.showinfo("Configuração", "Aqui abriria a tela de configuração de coordenadas."))
    botao.pack()

    texto_gabarito = """Caso não saiba a formatação dos arquivos de texto, clique abaixo para baixar o gabarito"""
    label_gabarito = tk.Label(frame_conteudo,text=texto_gabarito,  wraplength=800, font=("Arial",12))
    label_gabarito.pack(pady=10)

    botao = tk.Button(frame_conteudo, text="Baixar Gabaritos", command=funcionalidadeSecundaria.baixar_gabaritos)
    botao.pack()

# Página Categoria
def pagina_categoria():
    tk.Label(frame_conteudo, text="Página de Categoria", font=("Arial", 16)).pack(pady=20)

    def carregar_arquivo():
        caminho = filedialog.askopenfilename(filetypes=[("Arquivos de texto","*.txt")])
        if caminho:
            if validar_txt(caminho):
                with open(caminho, "r", encoding="utf-8") as f:
                    conteudo = f.read()
                dados_categoria["arquivo"] = conteudo
                salvar_arquivo("categoria.txt", conteudo)
            else:
                messagebox.showerror("Erro", "Arquivo inválido. Use formato NomeItem | Descricao")

    tk.Button(frame_conteudo, text="Carregar Arquivo de Categoria", command=carregar_arquivo).pack(pady=5)

    tk.Label(frame_conteudo, text="Possui complementos?").pack()
    var_complemento = tk.BooleanVar()
    tk.Checkbutton(frame_conteudo, text="Sim", variable=var_complemento).pack()

    def carregar_complemento():
        if var_complemento.get():
            caminho = filedialog.askopenfilename(filetypes=[("Arquivos de texto","*.txt")])
            if caminho:
                if validar_txt(caminho):
                    with open(caminho, "r", encoding="utf-8") as f:
                        conteudo = f.read()
                    dados_categoria["complemento"] = conteudo
                    salvar_arquivo("categoria_complemento.txt", conteudo)
                else:
                    messagebox.showerror("Erro", "Complemento inválido. Use formato NomeItem | Descricao")
        else:
            messagebox.showwarning("Aviso", "Marque a opção 'Sim' para carregar complementos.")

    tk.Button(frame_conteudo, text="Carregar Complementos", command=carregar_complemento).pack(pady=5)

# Página Complemento
def pagina_complemento():
    tk.Label(frame_conteudo, text="Página de Complemento", font=("Arial", 16)).pack(pady=20)

    def carregar_arquivo():
        caminho = filedialog.askopenfilename(filetypes=[("Arquivos de texto","*.txt")])
        if caminho:
            if validar_txt(caminho):
                with open(caminho, "r", encoding="utf-8") as f:
                    conteudo = f.read()
                dados_complemento["arquivo"] = conteudo
                salvar_arquivo("complemento.txt", conteudo)
            else:
                messagebox.showerror("Erro", "Arquivo inválido.")
    tk.Button(frame_conteudo, text="Carregar Arquivo de Complemento", command=carregar_arquivo).pack(pady=5)

# Página Editar Nome
def pagina_nome():
    tk.Label(frame_conteudo, text="Editar Nome do Produto", font=("Arial", 16)).pack(pady=20)
    tk.Label(frame_conteudo, text="Palavra antiga:").pack()
    entrada_antiga = tk.Entry(frame_conteudo)
    entrada_antiga.pack()
    tk.Label(frame_conteudo, text="Palavra nova:").pack()
    entrada_nova = tk.Entry(frame_conteudo)
    entrada_nova.pack()
    tk.Label(frame_conteudo, text="Quantidade de produtos:").pack()
    entrada_qtd = tk.Entry(frame_conteudo)
    entrada_qtd.pack()

    def salvar():
        dados_nome["antiga"] = entrada_antiga.get()
        dados_nome["nova"] = entrada_nova.get()
        dados_nome["qtd"] = entrada_qtd.get()
        salvar_arquivo("nome.txt", str(dados_nome))

    tk.Button(frame_conteudo, text="Salvar", command=salvar).pack(pady=5)

# Página Editar Tamanho
def pagina_tamanho():
    tk.Label(frame_conteudo, text="Editar Tamanho", font=("Arial", 16)).pack(pady=20)
    tk.Label(frame_conteudo, text="Tamanho antigo:").pack()
    entrada_antigo = tk.Entry(frame_conteudo)
    entrada_antigo.pack()
    tk.Label(frame_conteudo, text="Tamanho novo:").pack()
    entrada_novo = tk.Entry(frame_conteudo)
    entrada_novo.pack()
    tk.Label(frame_conteudo, text="Quantidade de produtos:").pack()
    entrada_qtd = tk.Entry(frame_conteudo)
    entrada_qtd.pack()

    def salvar():
        dados_tamanho["antigo"] = entrada_antigo.get()
        dados_tamanho["novo"] = entrada_novo.get()
        dados_tamanho["qtd"] = entrada_qtd.get()
        salvar_arquivo("tamanho.txt", str(dados_tamanho))

    tk.Button(frame_conteudo, text="Salvar", command=salvar).pack(pady=5)

# Página Editar Preço
def pagina_preco():
    tk.Label(frame_conteudo, text="Editar Preço", font=("Arial", 16)).pack(pady=20)
    tk.Label(frame_conteudo, text="Preço original:").pack()
    entrada_original = tk.Entry(frame_conteudo)
    entrada_original.pack()
    tk.Label(frame_conteudo, text="Preço com desconto:").pack()
    entrada_desconto = tk.Entry(frame_conteudo)
    entrada_desconto.pack()
    tk.Label(frame_conteudo, text="Quantidade de produtos:").pack()
    entrada_qtd = tk.Entry(frame_conteudo)
    entrada_qtd.pack()

    def salvar():
        dados_preco["original"] = entrada_original.get()
        dados_preco["desconto"] = entrada_desconto.get()
        dados_preco["qtd"] = entrada_qtd.get()
        salvar_arquivo("preco.txt", str(dados_preco))

    tk.Button(frame_conteudo, text="Salvar", command=salvar).pack(pady=5)

# Página Upsell
def pagina_upsell_definido():
    tk.Label(frame_conteudo, text="Página de UpSell (Preço Definido)", font=("Arial", 16)).pack(pady=20)

    tk.Label(frame_conteudo, text="Nome da categoria:").pack()
    entrada_categoria = tk.Entry(frame_conteudo)
    entrada_categoria.pack()

    tk.Label(frame_conteudo, text="Preço base (ex: 44.9):").pack()
    entrada_base = tk.Entry(frame_conteudo)
    entrada_base.pack()

    tk.Label(frame_conteudo, text="Quantidade de produtos:").pack()
    entrada_qtd = tk.Entry(frame_conteudo)
    entrada_qtd.pack()

    tk.Label(frame_conteudo, text="A partir de qual item:").pack()
    entrada_i = tk.Entry(frame_conteudo)
    entrada_i.pack()

    def salvar():
        try:
            categoria = entrada_categoria.get()
            valor_base = float(entrada_base.get())
            qtd = int(entrada_qtd.get())
            i = int(entrada_i.get()) - 1

            upsellDefinido.executaVarias(
                qtd,
                i,
                categoria,
                valor_base
            )

            messagebox.showinfo("Sucesso", "Upsell definido executado com sucesso!")

        except ValueError:
            messagebox.showerror("Erro", "Verifique os valores inseridos.")

    tk.Button(frame_conteudo, text="Executar", command=salvar).pack(pady=10)
def pagina_upsell_indefinido():
    tk.Label(frame_conteudo, text="Página de UpSell", font=("Arial", 16)).pack(pady=20)
    tk.Label(frame_conteudo, text="Nome da categoria:").pack()
    entrada_categoria = tk.Entry(frame_conteudo)
    entrada_categoria.pack()
    tk.Label(frame_conteudo, text="Valor Somado:").pack()
    entrada_upsell = tk.Entry(frame_conteudo)
    entrada_upsell.pack()
    tk.Label(frame_conteudo, text="Quantidade de produtos:").pack()
    entrada_qtd = tk.Entry(frame_conteudo)
    entrada_qtd.pack()
    tk.Label(frame_conteudo, text="A partir de qual item:").pack()
    entrada_i = tk.Entry(frame_conteudo)
    entrada_i.pack()

    def salvar():
        categoria = entrada_categoria.get()
        valorAdd = float(entrada_upsell.get())
        qtd = int(entrada_qtd.get())
        i = int(entrada_i.get())-1
        upsellIndefinido.executaVarias(qtd,i,categoria,valorAdd)

    tk.Button(frame_conteudo, text="Salvar", command=salvar).pack(pady=5)

# Janela principal
janela = tk.Tk()
janela.title("Auxiliar de Cardápios iFood")
janela.geometry("900x450")

# Menu
menubar = tk.Menu(janela)
janela.config(menu=menubar)

file_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Criar", menu=file_menu)
file_menu.add_command(label="Categoria", command=lambda: mostrar_pagina(pagina_categoria))
file_menu.add_command(label="Complemento", command=lambda: mostrar_pagina(pagina_complemento))

edit_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Editar", menu=edit_menu)
edit_menu.add_command(label="Nome", command=lambda: mostrar_pagina(pagina_nome))
edit_menu.add_command(label="Tamanho", command=lambda: mostrar_pagina(pagina_tamanho))
edit_menu.add_command(label="Preço", command=lambda: mostrar_pagina(pagina_preco))
upsell_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Upsell", menu=upsell_menu)
upsell_menu.add_command(label="Preço Definido", command=lambda: mostrar_pagina(pagina_upsell_definido))
upsell_menu.add_command(label="Preço Indefinido", command=lambda: mostrar_pagina(pagina_upsell_indefinido))
# Frame de conteúdo principal
frame_conteudo = tk.Frame(janela)
frame_conteudo.pack(fill="both", expand=True)

# Mostrar página inicial ao abrir
mostrar_pagina(pagina_inicial)

# Loop da interface
janela.mainloop()
