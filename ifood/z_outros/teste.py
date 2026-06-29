import tkinter as tk

# Função que limpa e mostra novo conteúdo no frame principal
def mostrar_pagina(conteudo):
    for widget in frame_conteudo.winfo_children():
        widget.destroy()
    conteudo()

# Exemplos de páginas
def pagina_categoria():
    tk.Label(frame_conteudo, text="Página de Categoria", font=("Arial", 16)).pack(pady=20)

def pagina_complemento():
    tk.Label(frame_conteudo, text="Página de Complemento", font=("Arial", 16)).pack(pady=20)

def pagina_nome():
    tk.Label(frame_conteudo, text="Editar Nome do Produto", font=("Arial", 16)).pack(pady=20)

def pagina_tamanho():
    tk.Label(frame_conteudo, text="Editar Tamanho", font=("Arial", 16)).pack(pady=20)

def pagina_preco():
    tk.Label(frame_conteudo, text="Editar Preço", font=("Arial", 16)).pack(pady=20)

def pagina_upsell():
    tk.Label(frame_conteudo, text="Página de UpSell", font=("Arial", 16)).pack(pady=20)

# Janela principal
janela = tk.Tk()
janela.title("Auxiliar de Cardápios iFood")
janela.geometry("900x450")

# === Menu customizado (substitui o tk.Menu) ===
menu_frame = tk.Frame(janela, bg="#8a2be2", height=60)  # Roxo
menu_frame.pack(side="top", fill="x")

# Botões no menu
botoes = [
    ("Criar Categoria", pagina_categoria),
    ("Criar Complemento", pagina_complemento),
    ("Editar Nome", pagina_nome),
    ("Editar Tamanho", pagina_tamanho),
    ("Editar Preço", pagina_preco),
    ("UpSell", pagina_upsell),
]

for texto, comando in botoes:
    tk.Button(
        menu_frame, 
        text=texto, 
        command=lambda c=comando: mostrar_pagina(c),
        bg="#3a006e", fg="white", font=("Arial", 12, "bold"),
        relief="flat", padx=15, pady=5
    ).pack(side="left", padx=10, pady=10)

# Frame de conteúdo principal
frame_conteudo = tk.Frame(janela, bg="white")
frame_conteudo.pack(fill="both", expand=True)

# Mostrar página inicial
mostrar_pagina(pagina_categoria)

janela.mainloop()
