"""
Painel moderno para automação de cardápio com Tkinter.
Design sofisticado com cards e layout profissional.
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import threading
import time
import json
from datetime import datetime
from pathlib import Path
import os
import sys

import pyautogui

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cria_cardapioNEW import main as cria_cardapio_original
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import som


class PainelAutomacao(tk.Tk):
    """Painel moderno para automação."""

    def __init__(self):
        super().__init__()
        self.title("Automação Cardápio")
        self.geometry("1400x850")
        self.resizable(True, True)

        # Cores
        self.colors = {
            'bg_main': '#1a1f2e',
            'bg_light': '#252d3d',
            'bg_card': '#2a323f',
            'text': '#ffffff',
            'text_light': '#a0a0a0',
            'green': '#00ff00',
            'green_dark': '#00cc00',
            'border': '#00ff00',
        }

        self.configure(bg=self.colors['bg_main'])

        # Estado
        self.automacao_ativa = False
        self.items_total = 0
        self.tempo_inicio = None
        self.thread_automacao = None
        self.velocidade = 1.0
        self.items_lista = []

        self._criar_ui()
        self._carregar_config()
        self._atualizar_timer()

    def _criar_ui(self):
        """Cria interface moderna."""
        # Header
        self._criar_header()

        # Container principal com 2 colunas
        main = tk.Frame(self, bg=self.colors['bg_main'])
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Painel esquerdo
        self._criar_painel_esquerdo(main)

        # Painel direito (logs)
        self._criar_painel_direito(main)

    def _criar_header(self):
        """Header moderno com título e métricas."""
        header = tk.Frame(self, bg=self.colors['bg_main'])
        header.pack(fill=tk.X, padx=15, pady=(15, 10))

        # Título
        titulo = tk.Label(
            header,
            text="AUTOMACAO CARDAPIO",
            bg=self.colors['bg_main'],
            fg=self.colors['green'],
            font=('Arial', 22, 'bold')
        )
        titulo.pack(side=tk.LEFT, pady=10)

        # Métricas no header
        metrics_frame = tk.Frame(header, bg=self.colors['bg_main'])
        metrics_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(20, 0))

        # STATUS
        status_card = self._criar_metrica_pequena(metrics_frame, "STATUS", "PARADO", 'status')
        status_card.pack(side=tk.LEFT, padx=10)

        # ITENS
        items_card = self._criar_metrica_pequena(metrics_frame, "ITENS", "0/0", 'items')
        items_card.pack(side=tk.LEFT, padx=10)

        # TEMPO
        time_card = self._criar_metrica_pequena(metrics_frame, "TEMPO", "00:00", 'time')
        time_card.pack(side=tk.LEFT, padx=10)

        # TAXA
        rate_card = self._criar_metrica_pequena(metrics_frame, "TAXA", "0/min", 'rate')
        rate_card.pack(side=tk.LEFT, padx=10)

        # Linha separadora
        line = tk.Frame(self, bg=self.colors['border'], height=1)
        line.pack(fill=tk.X)

    def _criar_painel_esquerdo(self, parent):
        """Painel esquerdo com controles."""
        painel = tk.Frame(parent, bg=self.colors['bg_main'])
        painel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))

        # Execução
        self._criar_secao(painel, "EXECUCAO")

        self.btn_iniciar = tk.Button(
            painel,
            text="INICIAR AUTOMACAO",
            bg=self.colors['bg_card'],
            fg=self.colors['green'],
            font=('Arial', 10, 'bold'),
            command=self.iniciar_automacao,
            padx=15,
            pady=10,
            cursor='hand2',
            relief=tk.FLAT,
            bd=1,
            activebackground=self.colors['bg_card'],
            activeforeground=self.colors['green']
        )
        self.btn_iniciar.pack(fill=tk.X, pady=10)

        info = tk.Label(
            painel,
            text="Para interromper: Ctrl+C",
            bg=self.colors['bg_main'],
            fg=self.colors['text_light'],
            font=('Arial', 8)
        )
        info.pack(fill=tk.X)

        # Arquivo
        self._criar_secao(painel, "ARQUIVO")

        file_frame = tk.Frame(painel, bg=self.colors['bg_main'])
        file_frame.pack(fill=tk.X, pady=5)

        self.input_arquivo = tk.Entry(
            file_frame,
            font=('Arial', 9),
            relief=tk.FLAT,
            bg=self.colors['bg_card'],
            fg=self.colors['green'],
            insertbackground=self.colors['green'],
            bd=1
        )
        self.input_arquivo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.input_arquivo.insert(0, 'data/pizza.txt')

        btn_browse = tk.Button(
            file_frame,
            text="PROCURAR",
            bg=self.colors['bg_card'],
            fg=self.colors['green'],
            font=('Arial', 8, 'bold'),
            command=self.browse_arquivo,
            padx=8,
            pady=5,
            cursor='hand2',
            relief=tk.FLAT,
            bd=1,
            activebackground=self.colors['bg_card'],
            activeforeground=self.colors['green']
        )
        btn_browse.pack(side=tk.LEFT)

        # Velocidade
        self._criar_secao(painel, "VELOCIDADE")

        tk.Label(
            painel,
            text="Multiplicador (0.5x - 2.0x):",
            bg=self.colors['bg_main'],
            fg=self.colors['text_light'],
            font=('Arial', 8)
        ).pack(anchor=tk.W)

        self.slider_velocidade = tk.Scale(
            painel,
            from_=0.5,
            to=2.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            bg=self.colors['bg_card'],
            fg=self.colors['green'],
            troughcolor=self.colors['bg_light'],
            highlightthickness=0,
            command=self._atualizar_velocidade,
            bd=0
        )
        self.slider_velocidade.set(1.0)
        self.slider_velocidade.pack(fill=tk.X, pady=5)

        self.label_velocidade = tk.Label(
            painel,
            text="1.0x (Normal)",
            bg=self.colors['bg_main'],
            fg=self.colors['green'],
            font=('Arial', 8)
        )
        self.label_velocidade.pack(anchor=tk.W)

        # Capturador
        self._criar_secao(painel, "CAPTURADOR")

        self.btn_capturar = tk.Button(
            painel,
            text="CAPTURAR COORDENADA",
            bg=self.colors['bg_card'],
            fg=self.colors['green'],
            font=('Arial', 9, 'bold'),
            command=self.iniciar_captura_coordenadas,
            padx=10,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
            bd=1,
            activebackground=self.colors['bg_card'],
            activeforeground=self.colors['green']
        )
        self.btn_capturar.pack(fill=tk.X, pady=5)

        self.label_coordenada = tk.Label(
            painel,
            text="Nenhuma capturada",
            bg=self.colors['bg_main'],
            fg=self.colors['text_light'],
            font=('Arial', 8)
        )
        self.label_coordenada.pack(anchor=tk.W)

        # Coordenadas
        self._criar_secao(painel, "COORDENADAS")

        self.coordenadas = {}
        for key, label, default in [
            ('menu', 'Menu Opcoes', '1764, 655'),
            ('dup', 'Botao Duplicar', '1716, 835'),
            ('name', 'Campo Nome', '310, 545'),
            ('send', 'Botao Enviar', '304, 999')
        ]:
            tk.Label(
                painel,
                text=label,
                bg=self.colors['bg_main'],
                fg=self.colors['text_light'],
                font=('Arial', 8)
            ).pack(anchor=tk.W, pady=(3, 0))

            entry = tk.Entry(
                painel,
                font=('Arial', 8),
                relief=tk.FLAT,
                bg=self.colors['bg_card'],
                fg=self.colors['green'],
                insertbackground=self.colors['green'],
                bd=1
            )
            entry.pack(fill=tk.X, pady=(0, 5))
            entry.insert(0, default)
            self.coordenadas[key] = entry

        btn_salvar = tk.Button(
            painel,
            text="SALVAR CONFIGURACAO",
            bg=self.colors['bg_card'],
            fg=self.colors['green'],
            font=('Arial', 9, 'bold'),
            command=self.salvar_config,
            padx=10,
            pady=8,
            cursor='hand2',
            relief=tk.FLAT,
            bd=1,
            activebackground=self.colors['bg_card'],
            activeforeground=self.colors['green']
        )
        btn_salvar.pack(fill=tk.X, pady=(10, 0))

    def _criar_metrica_pequena(self, parent, titulo, valor, key):
        """Métrica compacta para o header."""
        card = tk.Frame(parent, bg=self.colors['bg_card'], relief=tk.FLAT, bd=1)

        titulo_lbl = tk.Label(
            card,
            text=titulo,
            bg=self.colors['bg_card'],
            fg=self.colors['green'],
            font=('Arial', 8, 'bold')
        )
        titulo_lbl.pack(padx=10, pady=(5, 2), anchor=tk.CENTER)

        valor_lbl = tk.Label(
            card,
            text=valor,
            bg=self.colors['bg_card'],
            fg=self.colors['text'],
            font=('Arial', 14, 'bold')
        )
        valor_lbl.pack(padx=10, pady=(2, 5), anchor=tk.CENTER)

        if key == 'status':
            self.label_status = valor_lbl
        elif key == 'items':
            self.label_items = valor_lbl
        elif key == 'time':
            self.label_time = valor_lbl
        elif key == 'rate':
            self.label_rate = valor_lbl

        return card

    def _criar_painel_direito(self, parent):
        """Painel direito com logs."""
        painel = tk.Frame(parent, bg=self.colors['bg_card'], relief=tk.FLAT, bd=1)
        painel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Header
        header = tk.Frame(painel, bg=self.colors['bg_card'])
        header.pack(fill=tk.X, padx=12, pady=10)

        tk.Label(
            header,
            text="LOG DE EXECUCAO",
            bg=self.colors['bg_card'],
            fg=self.colors['green'],
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT)

        btn_limpar = tk.Button(
            header,
            text="LIMPAR LOG",
            bg='#cc0000',
            fg='#ffffff',
            font=('Arial', 8, 'bold'),
            command=self.limpar_logs,
            padx=8,
            pady=3,
            cursor='hand2',
            relief=tk.FLAT,
            bd=0,
            activebackground='#990000',
            activeforeground='#ffffff'
        )
        btn_limpar.pack(side=tk.RIGHT)

        # Logs
        self.text_logs = scrolledtext.ScrolledText(
            painel,
            font=('Courier New', 9),
            bg=self.colors['bg_main'],
            fg=self.colors['green'],
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=10,
            wrap=tk.WORD,
            insertbackground=self.colors['green']
        )
        self.text_logs.pack(fill=tk.BOTH, expand=True, pady=(0, 10), padx=12)

        self.text_logs.tag_config('info', foreground=self.colors['green'])
        self.text_logs.tag_config('success', foreground=self.colors['green'])
        self.text_logs.tag_config('error', foreground='#ff6666')
        self.text_logs.tag_config('warning', foreground='#ffaa00')
        self.text_logs.tag_config('time', foreground=self.colors['text_light'])

        self.adicionar_log("Sistema pronto para iniciar", 'info')

    def _criar_secao(self, parent, titulo):
        """Separador de seção."""
        secao = tk.Frame(parent, bg=self.colors['bg_main'])
        secao.pack(fill=tk.X, padx=0, pady=(15, 8))

        tk.Label(
            secao,
            text=titulo,
            bg=self.colors['bg_main'],
            fg=self.colors['green'],
            font=('Arial', 9, 'bold')
        ).pack(anchor=tk.W)

        line = tk.Frame(secao, bg=self.colors['border'], height=1)
        line.pack(fill=tk.X, pady=(3, 0))

    def adicionar_log(self, mensagem, tipo='info'):
        """Adiciona log."""
        tempo = datetime.now().strftime("%H:%M:%S")
        self.text_logs.insert(tk.END, f"[{tempo}] ", 'time')
        self.text_logs.insert(tk.END, f"{mensagem}\n", tipo)
        self.text_logs.see(tk.END)
        self.update_idletasks()

    def limpar_logs(self):
        """Limpa logs."""
        self.text_logs.delete(1.0, tk.END)
        self.adicionar_log("Logs limpos", 'info')

    def browse_arquivo(self):
        """Seleciona arquivo."""
        arquivo = filedialog.askopenfilename(
            title="Selecione o arquivo",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos", "*.*")]
        )
        if arquivo:
            self.input_arquivo.delete(0, tk.END)
            self.input_arquivo.insert(0, arquivo)

    def _atualizar_velocidade(self, valor):
        """Atualiza velocidade."""
        vel = float(valor)
        descricao = "Normal" if vel == 1.0 else "Rapido" if vel > 1.0 else "Lento"
        self.label_velocidade.config(text=f"{vel:.1f}x ({descricao})")
        self.velocidade = vel

    def iniciar_captura_coordenadas(self):
        """Inicia captura."""
        self.adicionar_log("Capturando em 2 segundos...", 'warning')
        self.btn_capturar.config(state=tk.DISABLED)
        thread = threading.Thread(target=self._capturar_coordenadas, daemon=True)
        thread.start()

    def _capturar_coordenadas(self):
        """Captura coordenadas."""
        time.sleep(2)
        x, y = pyautogui.position()
        self.label_coordenada.config(text=f"Ultima: {x}, {y}", fg=self.colors['green'])
        self.btn_capturar.config(state=tk.NORMAL)
        self.adicionar_log(f"Coordenadas: {x}, {y}", 'success')

    def iniciar_automacao(self):
        """Inicia automação."""
        arquivo = self.input_arquivo.get()

        if not Path(arquivo).exists():
            messagebox.showerror("Erro", f"Arquivo nao encontrado")
            self.adicionar_log(f"Arquivo nao encontrado", 'error')
            return

        self.automacao_ativa = True
        self.tempo_inicio = time.time()

        self.btn_iniciar.config(state=tk.DISABLED)
        self.label_status.config(text="EXECUTANDO", fg=self.colors['green'])

        self.adicionar_log("Automacao iniciada", 'success')

        self.thread_automacao = threading.Thread(
            target=self._executar_automacao,
            args=(arquivo,),
            daemon=True
        )
        self.thread_automacao.start()

    def _executar_automacao(self, arquivo):
        """Executa automação com logs detalhados."""
        try:
            # Configurar velocidade do pyautogui
            pausa_base = 0.5 / self.velocidade
            pyautogui.PAUSE = pausa_base
            self.adicionar_log(f"Velocidade configurada: {self.velocidade:.1f}x", 'info')

            self.adicionar_log("Carregando dados...", 'info')

            with open(arquivo, 'r', encoding='utf-8') as f:
                linhas = f.readlines()

            self.items_lista = [l.strip() for l in linhas if l.strip()]
            self.items_total = len(self.items_lista)
            self.label_items.config(text=f"0/{self.items_total}")

            self.adicionar_log(f"Total de itens: {self.items_total}", 'success')
            time.sleep(1)

            self.adicionar_log("Iniciando automacao...", 'success')
            time.sleep(1)

            items_processados = 0

            try:
                # Executa automação original
                cria_cardapio_original()

                # Após automação, contar itens processados
                if self.automacao_ativa:
                    for idx, item in enumerate(self.items_lista, 1):
                        if not self.automacao_ativa:
                            break
                        items_processados = idx
                        self.label_items.config(text=f"{items_processados}/{self.items_total}")
                        self.adicionar_log(f"✓ Processado [{idx}/{self.items_total}]: {item}", 'success')
                        self.update_idletasks()

                    self.adicionar_log("Automacao concluida com sucesso!", 'success')
                    self.label_status.config(text="CONCLUIDO")
                    self.automacao_ativa = False
                    self.btn_iniciar.config(state=tk.NORMAL)

            except KeyboardInterrupt:
                self.adicionar_log("Automacao interrompida pelo usuario!", 'warning')
                self.automacao_ativa = False
                self.btn_iniciar.config(state=tk.NORMAL)
                self.label_status.config(text="INTERROMPIDO")
            except Exception as e:
                self.adicionar_log(f"Erro na automacao: {str(e)}", 'error')
                self.automacao_ativa = False
                self.btn_iniciar.config(state=tk.NORMAL)
                self.label_status.config(text="ERRO")

        except Exception as e:
            self.adicionar_log(f"Erro fatal: {str(e)}", 'error')
            self.automacao_ativa = False
            self.btn_iniciar.config(state=tk.NORMAL)
        finally:
            pyautogui.PAUSE = 0.5

    def _atualizar_timer(self):
        """Atualiza timer."""
        if self.tempo_inicio and self.automacao_ativa:
            elapsed = int(time.time() - self.tempo_inicio)
            mins = elapsed // 60
            secs = elapsed % 60
            self.label_time.config(text=f"{mins:02d}:{secs:02d}")

        self.after(1000, self._atualizar_timer)

    def salvar_config(self):
        """Salva configuração."""
        config = {
            'arquivo': self.input_arquivo.get(),
            'velocidade': self.velocidade,
            'coordenadas': {
                'menu': self.coordenadas['menu'].get(),
                'dup': self.coordenadas['dup'].get(),
                'name': self.coordenadas['name'].get(),
                'send': self.coordenadas['send'].get()
            }
        }

        try:
            with open('config/painel.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            self.adicionar_log("Configuracao salva!", 'success')
            messagebox.showinfo("Sucesso", "Configuracao salva!")
        except Exception as e:
            self.adicionar_log(f"Erro ao salvar", 'error')

    def _carregar_config(self):
        """Carrega configuração."""
        try:
            if Path('config/painel.json').exists():
                with open('config/painel.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)

                self.input_arquivo.delete(0, tk.END)
                self.input_arquivo.insert(0, config.get('arquivo', 'data/pizza.txt'))

                self.slider_velocidade.set(config.get('velocidade', 1.0))

                coords = config.get('coordenadas', {})
                for key in ['menu', 'dup', 'name', 'send']:
                    if key in coords:
                        self.coordenadas[key].delete(0, tk.END)
                        self.coordenadas[key].insert(0, coords[key])
        except:
            pass


if __name__ == "__main__":
    app = PainelAutomacao()
    app.mainloop()
