"""
Painel visual da automação iFood

Recursos:
- criar produtos
- editar produtos
- fila visual de itens
- presets
- coordenadas com captura por clique direito
- testar coordenada
- tratamento visual de erro
- opção de recalibrar quando algo falhar

Dependências:
- tkinter
- sqlite3
- pyautogui
- FluxoProdutos.py
- Coordenada.py
"""

import json
import sqlite3
import threading
import traceback
import tkinter as tk
from tkinter import ttk, messagebox

import Coordenada
from FluxoProdutos import FluxoProdutos


DB_PATH = "automacao_ifood.db"


class PainelAutomacao:
    def __init__(self, root):
        self.root = root
        self.root.title("Painel de Automação iFood")
        self.root.geometry("1180x760")
        self.root.minsize(1100, 700)

        Coordenada.inicializar_banco()
        self.fluxo = FluxoProdutos(callback_falha_coordenada=self._abrir_recalibracao_automatica)

        self._montar_estilo()
        self._montar_interface()
        self._carregar_coordenadas()
        self._carregar_presets()
        
    def _abrir_recalibracao_automatica(self, nome_componente):
        """
        Chamado automaticamente quando uma validação falha em algum Grupo.
        """
        def acao_ui():
            self._log(f"Falha de validação detectada em: {nome_componente}")

            self.notebook.select(self.tab_coordenadas)
            self.var_coord_nome.set(nome_componente)

            resposta = messagebox.askyesnocancel(
                "Falha de validação",
                f"O componente '{nome_componente}' falhou na validação.\n\n"
                f"Sim = capturar coordenada de clique\n"
                f"Não = capturar coordenada de validação\n"
                f"Cancelar = não alterar agora"
            )

            if resposta is None:
                return

            if resposta is True:
                self._capturar_clique_automatico(nome_componente)
            else:
                self._capturar_validacao_automatica(nome_componente)

        self.root.after(0, acao_ui)

    def _capturar_clique_automatico(self, nome):
        self.root.withdraw()
        self.root.after(200, lambda: self._capturar_clique_real(nome))

    def _capturar_validacao_automatica(self, nome):
        self.root.withdraw()
        self.root.after(200, lambda: self._capturar_validacao_real(nome))
    # =========================================================
    # ESTILO
    # =========================================================

    def _montar_estilo(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("TLabel", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10))
        style.configure("TNotebook.Tab", font=("Arial", 10, "bold"))

    # =========================================================
    # INTERFACE
    # =========================================================

    def _montar_interface(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self.tab_execucao = ttk.Frame(self.notebook)
        self.tab_coordenadas = ttk.Frame(self.notebook)
        self.tab_presets = ttk.Frame(self.notebook)
        self.tab_logs = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_execucao, text="Execução")
        self.notebook.add(self.tab_coordenadas, text="Coordenadas")
        self.notebook.add(self.tab_presets, text="Presets")
        self.notebook.add(self.tab_logs, text="Logs")

        self._montar_tab_execucao()
        self._montar_tab_coordenadas()
        self._montar_tab_presets()
        self._montar_tab_logs()

    # =========================================================
    # TAB EXECUÇÃO
    # =========================================================

    def _montar_tab_execucao(self):
        container = ttk.Frame(self.tab_execucao)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        topo = ttk.LabelFrame(container, text="Ação")
        topo.pack(fill="x", pady=5)

        self.tipo_acao_var = tk.StringVar(value="criar")
        ttk.Radiobutton(topo, text="Criar produto", variable=self.tipo_acao_var, value="criar").pack(side="left", padx=10, pady=8)
        ttk.Radiobutton(topo, text="Editar produto", variable=self.tipo_acao_var, value="editar").pack(side="left", padx=10, pady=8)

        form = ttk.LabelFrame(container, text="Dados do item")
        form.pack(fill="x", pady=5)

        self.vars_item = {
            "posicao_produto": tk.StringVar(value="0"),
            "nome_produto": tk.StringVar(),
            "descricao_produto": tk.StringVar(),
            "preco_produto": tk.StringVar(value="0"),
            "desconto_produto": tk.StringVar(value="0"),
            "tipo_alteracao": tk.StringVar(value="0"),
            "separador": tk.StringVar(value=" - "),
            "soma": tk.StringVar(value="0"),
        }

        campos = [
            ("Posição", "posicao_produto", 0, 0),
            ("Nome", "nome_produto", 0, 1),
            ("Descrição", "descricao_produto", 1, 0),
            ("Preço", "preco_produto", 1, 1),
            ("Desconto", "desconto_produto", 2, 0),
            ("Tipo alteração", "tipo_alteracao", 2, 1),
            ("Separador", "separador", 3, 0),
            ("Soma", "soma", 3, 1),
        ]

        for texto, chave, r, c in campos:
            frame = ttk.Frame(form)
            frame.grid(row=r, column=c, sticky="ew", padx=8, pady=6)
            ttk.Label(frame, text=texto).pack(anchor="w")
            ttk.Entry(frame, textvariable=self.vars_item[chave], width=55 if chave == "descricao_produto" else 30).pack(fill="x")

        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        botoes = ttk.Frame(container)
        botoes.pack(fill="x", pady=8)

        ttk.Button(botoes, text="Adicionar à fila", command=self._adicionar_item_fila).pack(side="left", padx=4)
        ttk.Button(botoes, text="Atualizar item selecionado", command=self._atualizar_item_fila).pack(side="left", padx=4)
        ttk.Button(botoes, text="Remover selecionado", command=self._remover_item_fila).pack(side="left", padx=4)
        ttk.Button(botoes, text="Limpar fila", command=self._limpar_fila).pack(side="left", padx=4)
        ttk.Button(botoes, text="Executar fila", command=self._executar_fila_thread).pack(side="right", padx=4)

        tabela_frame = ttk.LabelFrame(container, text="Fila")
        tabela_frame.pack(fill="both", expand=True, pady=5)

        colunas = (
            "tipo", "posicao", "nome", "descricao", "preco",
            "desconto", "tipo_alteracao", "separador", "soma"
        )

        self.tree_fila = ttk.Treeview(tabela_frame, columns=colunas, show="headings", height=14)
        self.tree_fila.pack(fill="both", expand=True)

        larguras = {
            "tipo": 80,
            "posicao": 70,
            "nome": 180,
            "descricao": 240,
            "preco": 80,
            "desconto": 80,
            "tipo_alteracao": 100,
            "separador": 80,
            "soma": 70,
        }

        titulos = {
            "tipo": "Tipo",
            "posicao": "Posição",
            "nome": "Nome",
            "descricao": "Descrição",
            "preco": "Preço",
            "desconto": "Desconto",
            "tipo_alteracao": "Tipo Alt.",
            "separador": "Separador",
            "soma": "Soma",
        }

        for col in colunas:
            self.tree_fila.heading(col, text=titulos[col])
            self.tree_fila.column(col, width=larguras[col], anchor="center")

        self.tree_fila.bind("<<TreeviewSelect>>", self._carregar_item_selecionado_na_form)

        rodape = ttk.Frame(container)
        rodape.pack(fill="x", pady=8)

        ttk.Button(rodape, text="Salvar preset da fila", command=self._salvar_preset_dialog).pack(side="left", padx=4)

        self.lbl_status = ttk.Label(rodape, text="Status: aguardando")
        self.lbl_status.pack(side="right", padx=4)

    def _ler_form_item(self):
        return {
            "tipo": self.tipo_acao_var.get(),
            "posicao_produto": self.vars_item["posicao_produto"].get().strip() or "0",
            "nome_produto": self.vars_item["nome_produto"].get().strip(),
            "descricao_produto": self.vars_item["descricao_produto"].get().strip(),
            "preco_produto": self.vars_item["preco_produto"].get().strip() or "0",
            "desconto_produto": self.vars_item["desconto_produto"].get().strip() or "0",
            "tipo_alteracao": self.vars_item["tipo_alteracao"].get().strip() or "0",
            "separador": self.vars_item["separador"].get(),
            "soma": self.vars_item["soma"].get().strip() or "0",
        }

    def _adicionar_item_fila(self):
        item = self._ler_form_item()

        if not item["nome_produto"]:
            messagebox.showerror("Erro", "Informe o nome do produto.")
            return

        self.tree_fila.insert("", "end", values=(
            item["tipo"],
            item["posicao_produto"],
            item["nome_produto"],
            item["descricao_produto"],
            item["preco_produto"],
            item["desconto_produto"],
            item["tipo_alteracao"],
            item["separador"],
            item["soma"],
        ))

        self._log(f"Item adicionado à fila: {item['nome_produto']}")

    def _atualizar_item_fila(self):
        selecionado = self.tree_fila.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um item da fila.")
            return

        item = self._ler_form_item()
        self.tree_fila.item(selecionado[0], values=(
            item["tipo"],
            item["posicao_produto"],
            item["nome_produto"],
            item["descricao_produto"],
            item["preco_produto"],
            item["desconto_produto"],
            item["tipo_alteracao"],
            item["separador"],
            item["soma"],
        ))
        self._log(f"Item atualizado: {item['nome_produto']}")

    def _remover_item_fila(self):
        selecionado = self.tree_fila.selection()
        if not selecionado:
            return
        self.tree_fila.delete(selecionado[0])

    def _limpar_fila(self):
        for item in self.tree_fila.get_children():
            self.tree_fila.delete(item)

    def _carregar_item_selecionado_na_form(self, event=None):
        selecionado = self.tree_fila.selection()
        if not selecionado:
            return

        valores = self.tree_fila.item(selecionado[0], "values")
        self.tipo_acao_var.set(valores[0])
        self.vars_item["posicao_produto"].set(valores[1])
        self.vars_item["nome_produto"].set(valores[2])
        self.vars_item["descricao_produto"].set(valores[3])
        self.vars_item["preco_produto"].set(valores[4])
        self.vars_item["desconto_produto"].set(valores[5])
        self.vars_item["tipo_alteracao"].set(valores[6])
        self.vars_item["separador"].set(valores[7])
        self.vars_item["soma"].set(valores[8])

    def _coletar_fila(self):
        itens = []
        for iid in self.tree_fila.get_children():
            v = self.tree_fila.item(iid, "values")
            itens.append({
                "tipo": v[0],
                "posicao_produto": int(v[1]),
                "nome_produto": v[2],
                "descricao_produto": v[3],
                "preco_produto": float(str(v[4]).replace(",", ".")),
                "desconto_produto": v[5],
                "tipo_alteracao": int(v[6]),
                "separador": v[7],
                "soma": int(v[8]),
            })
        return itens

    def _executar_fila_thread(self):
        thread = threading.Thread(target=self._executar_fila, daemon=True)
        thread.start()

    def _executar_fila(self):
        try:
            self._set_status("executando")

            itens = self._coletar_fila()
            if not itens:
                messagebox.showwarning("Aviso", "A fila está vazia.")
                self._set_status("aguardando")
                return

            for item in itens:
                nome = item["nome_produto"]
                self._log(f"Iniciando item: {nome}")

                if item["tipo"] == "criar":
                    self.fluxo.criar_a_partir_do_topo(
                        nome_produto=item["nome_produto"],
                        descricao_produto=item["descricao_produto"],
                        preco_produto=item["preco_produto"],
                        desconto_produto=item["desconto_produto"]
                    )
                else:
                    self.fluxo.editar_por_posicao(
                        posicao_produto=item["posicao_produto"],
                        nome_produto=item["nome_produto"],
                        descricao_produto=item["descricao_produto"],
                        preco_produto=item["preco_produto"],
                        desconto_produto=item["desconto_produto"],
                        tipo_alteracao=item["tipo_alteracao"],
                        separador=item["separador"],
                        soma=item["soma"]
                    )

                self._log(f"Finalizado item: {nome}")

            self._set_status("finalizado com sucesso")
            messagebox.showinfo("Sucesso", "Fila executada com sucesso.")

        except Exception as e:
            self._set_status("erro")
            self._log("ERRO:\n" + traceback.format_exc())
            self._tratar_erro_visual(str(e))

    # =========================================================
    # TAB COORDENADAS
    # =========================================================

    def _montar_tab_coordenadas(self):
        container = ttk.Frame(self.tab_coordenadas)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        esq = ttk.LabelFrame(container, text="Coordenadas salvas")
        esq.pack(side="left", fill="both", expand=True, padx=(0, 5))

        colunas = ("nome", "x", "y", "xv", "yv", "atualizado")
        self.tree_coord = ttk.Treeview(esq, columns=colunas, show="headings", height=24)
        self.tree_coord.pack(fill="both", expand=True)

        heads = {
            "nome": "Nome",
            "x": "X",
            "y": "Y",
            "xv": "X Val.",
            "yv": "Y Val.",
            "atualizado": "Atualizado",
        }

        widths = {
            "nome": 260,
            "x": 70,
            "y": 70,
            "xv": 70,
            "yv": 70,
            "atualizado": 160,
        }

        for c in colunas:
            self.tree_coord.heading(c, text=heads[c])
            self.tree_coord.column(c, width=widths[c], anchor="center")

        self.tree_coord.bind("<<TreeviewSelect>>", self._carregar_coordenada_form)

        dirf = ttk.LabelFrame(container, text="Editar / Capturar")
        dirf.pack(side="right", fill="y", padx=(5, 0))

        self.var_coord_nome = tk.StringVar()
        self.var_coord_x = tk.StringVar()
        self.var_coord_y = tk.StringVar()
        self.var_coord_xv = tk.StringVar()
        self.var_coord_yv = tk.StringVar()

        campos = [
            ("Nome", self.var_coord_nome),
            ("X", self.var_coord_x),
            ("Y", self.var_coord_y),
            ("X validação", self.var_coord_xv),
            ("Y validação", self.var_coord_yv),
        ]

        for texto, var in campos:
            frame = ttk.Frame(dirf)
            frame.pack(fill="x", padx=8, pady=5)
            ttk.Label(frame, text=texto).pack(anchor="w")
            ttk.Entry(frame, textvariable=var, width=28).pack(fill="x")

        ttk.Button(dirf, text="Salvar manualmente", command=self._salvar_coord_manual).pack(fill="x", padx=8, pady=4)
        ttk.Button(dirf, text="Capturar clique (botão direito)", command=self._capturar_clique).pack(fill="x", padx=8, pady=4)
        ttk.Button(dirf, text="Capturar validação (botão direito)", command=self._capturar_validacao).pack(fill="x", padx=8, pady=4)
        ttk.Button(dirf, text="Testar coordenada", command=self._testar_coordenada).pack(fill="x", padx=8, pady=4)
        ttk.Button(dirf, text="Testar e clicar", command=self._testar_coordenada_clicando).pack(fill="x", padx=8, pady=4)
        ttk.Button(dirf, text="Excluir coordenada", command=self._excluir_coordenada).pack(fill="x", padx=8, pady=12)

    def _carregar_coordenadas(self):
        for iid in self.tree_coord.get_children():
            self.tree_coord.delete(iid)

        for nome, x, y, xv, yv, atualizado in Coordenada.listar_coordenadas():
            self.tree_coord.insert("", "end", values=(nome, x, y, xv or "", yv or "", atualizado or ""))

    def _carregar_coordenada_form(self, event=None):
        selecionado = self.tree_coord.selection()
        if not selecionado:
            return

        v = self.tree_coord.item(selecionado[0], "values")
        self.var_coord_nome.set(v[0])
        self.var_coord_x.set(v[1])
        self.var_coord_y.set(v[2])
        self.var_coord_xv.set(v[3])
        self.var_coord_yv.set(v[4])

    def _salvar_coord_manual(self):
        nome = self.var_coord_nome.get().strip()
        if not nome:
            messagebox.showerror("Erro", "Informe o nome da coordenada.")
            return

        try:
            x = int(self.var_coord_x.get())
            y = int(self.var_coord_y.get())
            Coordenada.salvar_ou_atualizar_coordenada(nome, x, y)

            if self.var_coord_xv.get().strip() and self.var_coord_yv.get().strip():
                xv = int(self.var_coord_xv.get())
                yv = int(self.var_coord_yv.get())
                Coordenada.salvar_ou_atualizar_validacao(nome, xv, yv)

            self._carregar_coordenadas()
            self._log(f"Coordenada salva: {nome}")
            messagebox.showinfo("Sucesso", "Coordenada salva.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _capturar_clique(self):
        nome = self.var_coord_nome.get().strip()
        if not nome:
            messagebox.showerror("Erro", "Informe o nome da coordenada.")
            return

        self.root.withdraw()
        self.root.after(200, lambda: self._capturar_clique_real(nome))

    def _capturar_clique_real(self, nome):
        pos = Coordenada.capturar_e_salvar(nome, eh_validacao=False)
        self.root.deiconify()
        self.root.lift()

        if pos:
            x, y = pos
            self.var_coord_x.set(str(x))
            self.var_coord_y.set(str(y))
            self._carregar_coordenadas()
            self._log(f"Coordenada de clique capturada: {nome} -> ({x}, {y})")

    def _capturar_validacao(self):
        nome = self.var_coord_nome.get().strip()
        if not nome:
            messagebox.showerror("Erro", "Informe o nome da coordenada.")
            return

        self.root.withdraw()
        self.root.after(200, lambda: self._capturar_validacao_real(nome))

    def _capturar_validacao_real(self, nome):
        pos = Coordenada.capturar_e_salvar(nome, eh_validacao=True)
        self.root.deiconify()
        self.root.lift()

        if pos:
            x, y = pos
            self.var_coord_xv.set(str(x))
            self.var_coord_yv.set(str(y))
            self._carregar_coordenadas()
            self._log(f"Coordenada de validação capturada: {nome} -> ({x}, {y})")

    def _testar_coordenada(self):
        nome = self.var_coord_nome.get().strip()
        if not nome:
            messagebox.showerror("Erro", "Informe o nome da coordenada.")
            return

        try:
            x, y = Coordenada.testar_coordenada(nome, clicar=False)
            self._log(f"Teste de coordenada: {nome} -> ({x}, {y})")
            messagebox.showinfo("Teste", f"Mouse movido para ({x}, {y}).")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _testar_coordenada_clicando(self):
        nome = self.var_coord_nome.get().strip()
        if not nome:
            messagebox.showerror("Erro", "Informe o nome da coordenada.")
            return

        try:
            x, y = Coordenada.testar_coordenada(nome, clicar=True)
            self._log(f"Teste com clique: {nome} -> ({x}, {y})")
            messagebox.showinfo("Teste", f"Mouse movido e clique executado em ({x}, {y}).")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _excluir_coordenada(self):
        nome = self.var_coord_nome.get().strip()
        if not nome:
            return

        if not messagebox.askyesno("Confirmar", f"Excluir coordenada '{nome}'?"):
            return

        Coordenada.deletar_coordenada(nome)
        self._carregar_coordenadas()
        self._log(f"Coordenada excluída: {nome}")

    # =========================================================
    # TAB PRESETS
    # =========================================================

    def _montar_tab_presets(self):
        container = ttk.Frame(self.tab_presets)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        left = ttk.LabelFrame(container, text="Presets salvos")
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.tree_presets = ttk.Treeview(left, columns=("id", "nome", "tipo", "criado"), show="headings", height=24)
        self.tree_presets.pack(fill="both", expand=True)

        self.tree_presets.heading("id", text="ID")
        self.tree_presets.heading("nome", text="Nome")
        self.tree_presets.heading("tipo", text="Tipo")
        self.tree_presets.heading("criado", text="Criado em")

        self.tree_presets.column("id", width=60, anchor="center")
        self.tree_presets.column("nome", width=240, anchor="w")
        self.tree_presets.column("tipo", width=120, anchor="center")
        self.tree_presets.column("criado", width=180, anchor="center")

        right = ttk.LabelFrame(container, text="Ações")
        right.pack(side="right", fill="y", padx=(5, 0))

        ttk.Button(right, text="Carregar preset na fila", command=self._carregar_preset_na_fila).pack(fill="x", padx=8, pady=6)
        ttk.Button(right, text="Excluir preset", command=self._excluir_preset).pack(fill="x", padx=8, pady=6)

    def _carregar_presets(self):
        for iid in self.tree_presets.get_children():
            self.tree_presets.delete(iid)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, tipo, criado_em FROM presets ORDER BY nome")
        registros = cursor.fetchall()
        conn.close()

        for row in registros:
            self.tree_presets.insert("", "end", values=row)

    def _salvar_preset_dialog(self):
        itens = self._coletar_fila()
        if not itens:
            messagebox.showwarning("Aviso", "A fila está vazia.")
            return

        janela = tk.Toplevel(self.root)
        janela.title("Salvar preset")
        janela.geometry("360x140")
        janela.transient(self.root)
        janela.grab_set()

        ttk.Label(janela, text="Nome do preset").pack(pady=(15, 5))
        var_nome = tk.StringVar()
        ttk.Entry(janela, textvariable=var_nome, width=35).pack(pady=5)

        def salvar():
            nome = var_nome.get().strip()
            if not nome:
                messagebox.showerror("Erro", "Informe o nome do preset.")
                return

            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO presets (nome, tipo, dados, criado_em)
                    VALUES (?, ?, ?, datetime('now','localtime'))
                """, (nome, "fila_produtos", json.dumps(itens, ensure_ascii=False)))
                conn.commit()
                conn.close()

                janela.destroy()
                self._carregar_presets()
                self._log(f"Preset salvo: {nome}")
                messagebox.showinfo("Sucesso", "Preset salvo com sucesso.")
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Já existe um preset com esse nome.")

        ttk.Button(janela, text="Salvar", command=salvar).pack(pady=12)

    def _carregar_preset_na_fila(self):
        selecionado = self.tree_presets.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um preset.")
            return

        preset_id = self.tree_presets.item(selecionado[0], "values")[0]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT dados FROM presets WHERE id = ?", (preset_id,))
        registro = cursor.fetchone()
        conn.close()

        if not registro:
            return

        itens = json.loads(registro[0])

        self._limpar_fila()

        for item in itens:
            self.tree_fila.insert("", "end", values=(
                item.get("tipo", "criar"),
                item.get("posicao_produto", 0),
                item.get("nome_produto", ""),
                item.get("descricao_produto", ""),
                item.get("preco_produto", 0),
                item.get("desconto_produto", "0"),
                item.get("tipo_alteracao", 0),
                item.get("separador", " - "),
                item.get("soma", 0),
            ))

        self.notebook.select(self.tab_execucao)
        self._log("Preset carregado na fila.")

    def _excluir_preset(self):
        selecionado = self.tree_presets.selection()
        if not selecionado:
            return

        preset_id = self.tree_presets.item(selecionado[0], "values")[0]
        nome = self.tree_presets.item(selecionado[0], "values")[1]

        if not messagebox.askyesno("Confirmar", f"Excluir preset '{nome}'?"):
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM presets WHERE id = ?", (preset_id,))
        conn.commit()
        conn.close()

        self._carregar_presets()
        self._log(f"Preset excluído: {nome}")

    # =========================================================
    # TAB LOGS
    # =========================================================

    def _montar_tab_logs(self):
        frame = ttk.Frame(self.tab_logs)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.txt_logs = tk.Text(frame, wrap="word", font=("Consolas", 10))
        self.txt_logs.pack(fill="both", expand=True)

        ttk.Button(frame, text="Limpar logs", command=lambda: self.txt_logs.delete("1.0", "end")).pack(pady=6)

    def _log(self, texto):
        self.txt_logs.insert("end", texto + "\n")
        self.txt_logs.see("end")

    # =========================================================
    # ERRO / RECALIBRAÇÃO
    # =========================================================

    def _tratar_erro_visual(self, mensagem):
        self._log(f"Erro capturado: {mensagem}")

        messagebox.showerror(
            "Erro na automação",
            f"{mensagem}\n\n"
            f"Se a falha foi de validação, a tela de recalibração já foi aberta automaticamente."
        )
    # =========================================================
    # STATUS
    # =========================================================

    def _set_status(self, texto):
        self.lbl_status.config(text=f"Status: {texto}")
        self.root.update_idletasks()


if __name__ == "__main__":
    Coordenada.inicializar_banco()

    root = tk.Tk()
    app = PainelAutomacao(root)
    root.mainloop()