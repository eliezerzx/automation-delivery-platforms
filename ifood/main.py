import customtkinter as ctk
import keyboard
import pyautogui
import os
from datetime import datetime

# Segurança: Mover o mouse para o canto superior esquerdo cancela a automação
pyautogui.FAILSAFE = True

# Importação dos seus módulos (certifique-se que as pastas existem no diretório)
try:
    from services import criar_cardapio, criar_complementos, dois_sabores, aplicar_desconto, remover_desconto, remov_desc_alt_valor
    from utils import coordenada
except ImportError as e:
    print(f"Aviso: Erro ao carregar módulos de serviço: {e}")

# --- CONFIGURAÇÕES VISUAIS ---
COR_FUNDO = "#1E1E1E"
COR_AMARELO = "#FFC20E"
COR_AMARELO_HOVER = "#E5AF0D"
COR_BOTAO_SALVAR = "#1B4F72"
COR_SUCESSO = "#2ECC71"
COR_LOG_FUNDO = "#000000" # Fundo preto estilo terminal

class AppAutomacao(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("iFood - Automação Profissional")
        self.geometry("1000x900") # Aumentei um pouco a largura para os logs
        self.configure(fg_color=COR_FUNDO)

        # Definição dos caminhos de dados
        self.caminho_dados = {
            "complementos": os.path.join("data", "complemento.txt"),
            "pizzas": os.path.join("data", "pizza.txt")
        }

        # Containers de Tela
        self.frame_inicial = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_editor = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_automacao = ctk.CTkFrame(self, fg_color="transparent")
        
        # Bind Global de Emergência
        keyboard.add_hotkey('ctrl+0', self.interromper_em_emergencia)

        self.renderizar_menu_principal()

    # --- DOCUMENTAÇÃO DAS FUNÇÕES ---

    def log(self, mensagem):
        """ 
        [DEF] Adiciona uma mensagem na caixa de logs com data e hora. 
        Simula o terminal do VS Code.
        """
        if hasattr(self, 'txt_logs'):
            hora = datetime.now().strftime("%H:%M:%S")
            self.txt_logs.configure(state="normal") # Habilita edição para inserir
            self.txt_logs.insert("end", f"[{hora}] {mensagem}\n")
            self.txt_logs.configure(state="disabled") # Desabilita novamente
            self.txt_logs.see("end") # Faz o scroll automático para o final

    def interromper_em_emergencia(self):
        """ [DEF] Fecha o programa imediatamente ao pressionar Ctrl+0. """
        print("\n[!] Interrupção de emergência disparada.")
        os._exit(0)

    def limpar_tela(self):
        """ [DEF] Esconde todos os frames para trocar de página. """
        for f in [self.frame_inicial, self.frame_editor, self.frame_automacao]:
            f.pack_forget()
            for widget in f.winfo_children():
                widget.destroy()

    def renderizar_menu_principal(self):
        """ [DEF] Constrói a tela inicial baseada no protótipo do Figma. """
        self.limpar_tela()
        self.frame_inicial.pack(expand=True, fill="both")
        
        ctk.CTkLabel(self.frame_inicial, text="IFOOD - AUTOMAÇÃO", 
                     font=ctk.CTkFont(family="Segoe UI Light", size=54), 
                     text_color="white").pack(pady=(80, 40))

        # Botões principais
        self.criar_btn_figma(self.frame_inicial, "Adicionar\nComplementos", lambda: self.abrir_editor("complementos"))
        self.criar_btn_figma(self.frame_inicial, "Adicionar\nPizzas", lambda: self.abrir_editor("pizzas"))
        
        ctk.CTkButton(self.frame_inicial, text="ABRIR PAINEL DE CONTROLE  ➔", 
                      fg_color="transparent", border_width=2, border_color=COR_AMARELO,
                      text_color=COR_AMARELO, font=("Arial", 16, "bold"),
                      height=50, width=380, command=self.abrir_menu_automacao).pack(pady=40)

    def abrir_editor(self, tipo):
        """ [DEF] Tela de edição de texto para os arquivos de gabarito. """
        self.limpar_tela()
        self.frame_editor.pack(expand=True, fill="both", padx=40, pady=20)

        header = ctk.CTkFrame(self.frame_editor, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        # Botão voltar circular
        ctk.CTkButton(header, text="<", width=50, height=50, corner_radius=25,
                      fg_color=COR_AMARELO, text_color="black", font=("Arial", 24, "bold"),
                      command=self.renderizar_menu_principal).pack(side="left")

        ctk.CTkLabel(header, text=f"Editando: {tipo}.txt", font=("Segoe UI", 20, "bold"), text_color="white").pack(side="left", padx=20)

        self.textbox = ctk.CTkTextbox(self.frame_editor, font=("Consolas", 16), fg_color="#FFFFFF", border_color=COR_AMARELO, border_width=1)
        self.textbox.pack(expand=True, fill="both", pady=10)

        if os.path.exists(self.caminho_dados[tipo]):
            with open(self.caminho_dados[tipo], "r", encoding="utf-8") as f:
                self.textbox.insert("1.0", f.read())

        # Botão salvar alterações
        self.btn_salvar = ctk.CTkButton(self.frame_editor, text="SALVAR ALTERAÇÕES", 
                                        fg_color=COR_BOTAO_SALVAR, font=("Arial", 16, "bold"), 
                                        height=60, command=lambda: self.salvar_dados(tipo))
        self.btn_salvar.pack(fill="x", pady=20)

    def salvar_dados(self, tipo):
        """ [DEF] Salva o conteúdo no arquivo .txt. """
        conteudo = self.textbox.get("1.0", "end-1c")
        os.makedirs("data", exist_ok=True)
        with open(self.caminho_dados[tipo], "w", encoding="utf-8") as f:
            f.write(conteudo)
        self.btn_salvar.configure(text="✅ ARQUIVO SALVO!", fg_color=COR_SUCESSO)
        self.after(1500, lambda: self.btn_salvar.configure(text="SALVAR ALTERAÇÕES", fg_color=COR_BOTAO_SALVAR))

    def abrir_menu_automacao(self):
        """ [DEF] Painel de execução com terminal de logs integrado. """
        self.limpar_tela()
        self.frame_automacao.pack(expand=True, fill="both", padx=50, pady=30)

        # Cabeçalho
        header = ctk.CTkFrame(self.frame_automacao, fg_color="#252525", border_width=2, border_color=COR_AMARELO)
        header.pack(fill="x", pady=10)
        ctk.CTkLabel(header, text="--- PAINEL DE CONTROLE ---", font=("Courier New", 20, "bold"), text_color=COR_AMARELO).pack(pady=10)

        # Grid para separar Botões de Logs
        conteudo = ctk.CTkFrame(self.frame_automacao, fg_color="transparent")
        conteudo.pack(expand=True, fill="both")

        # Lado Esquerdo: Botões
        botoes_frame = ctk.CTkFrame(conteudo, fg_color="transparent")
        botoes_frame.pack(side="left", fill="y", padx=(0, 20))

        opcoes = [
            ("1 - Criar Cardápio", lambda: self.executar_delay(criar_cardapio.criaCardapio, "Cardápio")),
            ("2 - Criar Complementos", lambda: self.executar_delay(criar_complementos.executar, "Complementos")),
            ("3 - 2 Sabores", lambda: self.executar_delay(dois_sabores.executar, "2 Sabores")),
            ("4 - Aplicar Descontos", lambda: self.executar_delay(aplicar_desconto.apli_desconto, "Descontos")),
            ("5 - Remover Descontos", lambda: self.executar_delay(remover_desconto.remover_desconto, "Descontos")),
            ("6 - Remover Descontos & Alterar Valor", lambda: self.executar_delay(remov_desc_alt_valor.alterar_desconto, "Descontos")),
            ("9 - Pegar Coordenada", self.rodar_coordenada_log),
            ("0 - Voltar", self.renderizar_menu_principal)
        ]

        for txt, cmd in opcoes:
            ctk.CTkButton(botoes_frame, text=txt, font=("Consolas", 16), height=45, width=250, anchor="w",
                          fg_color="#333333" if "9" not in txt else "#D35400", command=cmd).pack(pady=5)

        # Lado Direito: Terminal de Logs (estilo VS Code)
        logs_frame = ctk.CTkFrame(conteudo, fg_color="transparent")
        logs_frame.pack(side="right", expand=True, fill="both")

        ctk.CTkLabel(logs_frame, text="--- [!] EM DESENVOLVIMENTO [!] --- \nCONSOLE DE SAÍDA (LOGS) \n >>> Para Melhor Visualizaçao Veja no Terminal do VScode <<<", font=("Consolas", 12, "bold"), text_color="#AAAAAA").pack(anchor="w")
        
        self.txt_logs = ctk.CTkTextbox(logs_frame, fg_color=COR_LOG_FUNDO, text_color="#00FF00", # Texto verde estilo Matrix
                                       font=("Consolas", 13), border_width=1, border_color="#444444")
        self.txt_logs.pack(expand=True, fill="both")
        self.txt_logs.configure(state="disabled") # Inicialmente bloqueado para escrita manual

        # Barra de Progresso inferior
        self.pbar = ctk.CTkProgressBar(self.frame_automacao, width=800, fg_color="#333333", progress_color=COR_AMARELO)
        self.pbar.set(0)
        self.pbar.pack(pady=20)

        self.log("Sistema iniciado. Aguardando comando...")

    def executar_delay(self, func, nome):
        """ [DEF] Prepara a execução com aviso nos logs e na barra. """
        self.log(f"Iniciando processo: {nome}...")
        self.log("Contagem regressiva de 2 segundos. Prepare a tela do iFood!")
        
        for i in range(1, 11):
            self.after(200 * i, lambda v=i/10: self.pbar.set(v))
        
        self.after(2000, lambda: self.rodar_pyautogui(func, nome))

    def rodar_pyautogui(self, func, nome):
        """ [DEF] Executa a automação real e registra nos logs. """
        self.log(f"EXECUTANDO {nome.upper()} AGORA...")
        self.update()
        try:
            func()
            self.log(f"SUCESSO: {nome} finalizado corretamente.")
        except Exception as e:
            self.log(f"ERRO: Falha ao executar {nome}. Detalhes: {e}")
        
        self.pbar.set(0)

    def rodar_coordenada_log(self):
        """ [DEF] Wrapper para a função de coordenada com registro de log. """
        self.log("Capturando coordenadas do mouse...")
        coordenada.coordenada()
        self.log("Captura finalizada.")

    def criar_btn_figma(self, master, texto, comando):
        """ [DEF] Helper para botões grandes do menu inicial. """
        ctk.CTkButton(master, text=texto, fg_color=COR_AMARELO, hover_color=COR_AMARELO_HOVER,
                      text_color="white", font=ctk.CTkFont(family="Cooper Black", size=28),
                      corner_radius=12, height=100, width=380, command=comando).pack(pady=10)

if __name__ == "__main__":
    AppAutomacao().mainloop()
