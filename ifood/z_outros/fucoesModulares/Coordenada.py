"""
Gerenciamento de coordenadas com SQLite.

Recursos:
- salvar e carregar coordenadas
- clique e validação separados
- captura por clique direito em overlay fullscreen
- teste de coordenada

Estrutura de armazenamento:
Tabela coordenadas
- nome
- x
- y
- x_validacao
- y_validacao
- atualizado_em
"""

import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import pyautogui


DB_PATH = "automacao_ifood.db"


class Coordenada:
    def __init__(self, x_novo, y_novo):
        self.x = x_novo
        self.y = y_novo

    def getXY(self):
        return (self.x, self.y)

    def setXY(self, x_novo, y_novo):
        self.x = x_novo
        self.y = y_novo

    def __repr__(self):
        return f"Coordenada(x={self.x}, y={self.y})"


def inicializar_banco(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coordenadas (
            nome TEXT PRIMARY KEY,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            x_validacao INTEGER,
            y_validacao INTEGER,
            atualizado_em TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS presets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            tipo TEXT NOT NULL,
            dados TEXT NOT NULL,
            criado_em TEXT
        )
    """)

    conn.commit()
    conn.close()


def carregarCoordenadas(db_path=DB_PATH):
    """
    Retorna:
    {
        "nome": Coordenada(...),
        "nome__validacao": Coordenada(...)
    }
    """
    inicializar_banco(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT nome, x, y, x_validacao, y_validacao FROM coordenadas")
    registros = cursor.fetchall()
    conn.close()

    coordenadas = {}

    for nome, x, y, x_valid, y_valid in registros:
        coordenadas[nome] = Coordenada(x, y)

        if x_valid is not None and y_valid is not None:
            coordenadas[f"{nome}__validacao"] = Coordenada(x_valid, y_valid)

    return coordenadas


def listar_coordenadas(db_path=DB_PATH):
    inicializar_banco(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nome, x, y, x_validacao, y_validacao, atualizado_em
        FROM coordenadas
        ORDER BY nome
    """)
    registros = cursor.fetchall()
    conn.close()
    return registros


def salvar_ou_atualizar_coordenada(nome, x, y, db_path=DB_PATH):
    inicializar_banco(db_path)
    agora = datetime.now().isoformat(sep=" ", timespec="seconds")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO coordenadas (nome, x, y, atualizado_em)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(nome) DO UPDATE SET
            x=excluded.x,
            y=excluded.y,
            atualizado_em=excluded.atualizado_em
    """, (nome, x, y, agora))

    conn.commit()
    conn.close()


def salvar_ou_atualizar_validacao(nome, x_validacao, y_validacao, db_path=DB_PATH):
    inicializar_banco(db_path)
    agora = datetime.now().isoformat(sep=" ", timespec="seconds")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO coordenadas (nome, x, y, x_validacao, y_validacao, atualizado_em)
        VALUES (?, 0, 0, ?, ?, ?)
        ON CONFLICT(nome) DO UPDATE SET
            x_validacao=excluded.x_validacao,
            y_validacao=excluded.y_validacao,
            atualizado_em=excluded.atualizado_em
    """, (nome, x_validacao, y_validacao, agora))

    conn.commit()
    conn.close()


def obter_coordenada(nome, db_path=DB_PATH, eh_validacao=False):
    inicializar_banco(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT x, y, x_validacao, y_validacao
        FROM coordenadas
        WHERE nome = ?
    """, (nome,))
    registro = cursor.fetchone()
    conn.close()

    if not registro:
        return None

    x, y, x_valid, y_valid = registro

    if eh_validacao:
        if x_valid is None or y_valid is None:
            return None
        return Coordenada(x_valid, y_valid)

    return Coordenada(x, y)


def deletar_coordenada(nome, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM coordenadas WHERE nome = ?", (nome,))
    conn.commit()
    conn.close()


def testar_coordenada(nome, db_path=DB_PATH, eh_validacao=False, clicar=False):
    coord = obter_coordenada(nome, db_path=db_path, eh_validacao=eh_validacao)
    if coord is None:
        raise ValueError(f"Coordenada '{nome}' não encontrada.")

    x, y = coord.getXY()
    pyautogui.moveTo(x, y, duration=0.3)

    if clicar:
        pyautogui.click(x, y)

    return (x, y)


def capturar_coordenada_por_overlay(titulo="Capturar coordenada", botao="direito"):
    """
    Abre overlay fullscreen.
    Quando o usuário clicar com o botão escolhido, captura a posição.
    """
    resultado = {"x": None, "y": None}

    root = tk.Tk()
    root.title(titulo)
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.configure(bg="black")
    root.attributes("-alpha", 0.20)
    root.config(cursor="crosshair")

    label = tk.Label(
        root,
        text="Clique com o botão DIREITO no local desejado\n\nPressione ESC para cancelar",
        font=("Arial", 18, "bold"),
        bg="black",
        fg="white"
    )
    label.pack(expand=True)

    def cancelar(event=None):
        root.destroy()

    def capturar_direito(event):
        resultado["x"] = event.x_root
        resultado["y"] = event.y_root
        root.destroy()

    def capturar_esquerdo(event):
        resultado["x"] = event.x_root
        resultado["y"] = event.y_root
        root.destroy()

    root.bind("<Escape>", cancelar)

    if botao == "direito":
        root.bind("<Button-3>", capturar_direito)
    else:
        root.bind("<Button-1>", capturar_esquerdo)

    root.mainloop()

    if resultado["x"] is None or resultado["y"] is None:
        return None

    return (resultado["x"], resultado["y"])


def capturar_e_salvar(nome, db_path=DB_PATH, eh_validacao=False):
    titulo = f"Capturar {'validação' if eh_validacao else 'clique'} - {nome}"
    pos = capturar_coordenada_por_overlay(titulo=titulo, botao="direito")

    if pos is None:
        return None

    x, y = pos

    if eh_validacao:
        salvar_ou_atualizar_validacao(nome, x, y, db_path=db_path)
    else:
        salvar_ou_atualizar_coordenada(nome, x, y, db_path=db_path)

    return (x, y)