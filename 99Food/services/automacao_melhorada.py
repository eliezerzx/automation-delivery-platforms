"""
Automação melhorada com retry, logs de falha, checkpoint e validação.
"""

import pyautogui
import time
import os
import sys
import pyperclip
import logging
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Tuple, List, Dict

# --- Configuração de logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automacao.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Configuração de caminho ---
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.append(root_path)

from utils import som

pyautogui.PAUSE = 0.5


@dataclass
class Coordenadas:
    """Armazena coordenadas de cliques."""
    menu_opcoes: Tuple[int, int]
    btn_duplicar: Tuple[int, int]
    campo_nome: Tuple[int, int]
    btn_enviar: Tuple[int, int]

    @classmethod
    def carregar_config(cls, arquivo: str = 'config/coordenadas.json') -> 'Coordenadas':
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return cls(
                menu_opcoes=tuple(config['menu_opcoes']),
                btn_duplicar=tuple(config['btn_duplicar']),
                campo_nome=tuple(config['campo_nome']),
                btn_enviar=tuple(config['btn_enviar'])
            )
        except FileNotFoundError:
            logger.warning(f"Arquivo {arquivo} não encontrado. Usando valores padrão.")
            return cls(
                menu_opcoes=(1764, 655),
                btn_duplicar=(1716, 835),
                campo_nome=(310, 545),
                btn_enviar=(304, 999)
            )


class AutomacaoMelhorada:
    """Automação com retry, logs de falha e checkpoint."""

    def __init__(self, max_retries: int = 3, pausa_entre_grupos: int = 5):
        self.coordenadas = Coordenadas.carregar_config()
        self.max_retries = max_retries
        self.pausa_entre_grupos = pausa_entre_grupos
        self.falhas = []
        self.processados = []
        self.checkpoint_file = 'config/checkpoint.json'
        logger.info("Automação melhorada inicializada")

    def validar_dados(self, caminho_arquivo: str) -> Tuple[bool, List[str], str]:
        """
        Valida dados do arquivo.
        
        Returns:
            (sucesso, linhas_validas, mensagem_erro)
        """
        if not os.path.exists(caminho_arquivo):
            return False, [], f"Arquivo {caminho_arquivo} não encontrado"

        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                linhas = f.readlines()

            linhas_validas = []
            linhas_invalidas = 0

            for i, linha in enumerate(linhas, 1):
                if not linha.strip():
                    continue
                
                partes = linha.strip().split('|')
                if len(partes) != 3:
                    linhas_invalidas += 1
                    logger.warning(f"Linha {i} inválida: {linha.strip()}")
                    continue

                linhas_validas.append(linha.strip())

            if not linhas_validas:
                return False, [], "Nenhuma linha válida encontrada no arquivo"

            msg = f"✓ {len(linhas_validas)} linhas válidas"
            if linhas_invalidas > 0:
                msg += f" ({linhas_invalidas} inválidas)"

            return True, linhas_validas, msg

        except Exception as e:
            return False, [], f"Erro ao validar dados: {str(e)}"

    def carregar_checkpoint(self) -> int:
        """Carrega último item processado."""
        try:
            if os.path.exists(self.checkpoint_file):
                with open(self.checkpoint_file, 'r') as f:
                    data = json.load(f)
                    return data.get('ultimo_item', 0)
        except:
            pass
        return 0

    def salvar_checkpoint(self, item_num: int):
        """Salva progresso."""
        try:
            with open(self.checkpoint_file, 'w') as f:
                json.dump({'ultimo_item': item_num}, f)
        except Exception as e:
            logger.error(f"Erro ao salvar checkpoint: {e}")

    def limpar_checkpoint(self):
        """Limpa checkpoint após conclusão."""
        try:
            if os.path.exists(self.checkpoint_file):
                os.remove(self.checkpoint_file)
        except:
            pass

    def registrar_falha(self, item: str, motivo: str, tentativa: int):
        """Registra item que falhou."""
        falha = {
            'item': item,
            'motivo': motivo,
            'tentativa': tentativa,
            'timestamp': time.strftime('%H:%M:%S')
        }
        self.falhas.append(falha)
        logger.error(f"FALHA: {item} (Tentativa {tentativa}/{self.max_retries}) - {motivo}")

    def salvar_log_falhas(self):
        """Salva log de falhas em arquivo."""
        if self.falhas:
            try:
                with open('logs/falhas.txt', 'w', encoding='utf-8') as f:
                    f.write("=== LOG DE FALHAS ===\n\n")
                    for falha in self.falhas:
                        f.write(f"Item: {falha['item']}\n")
                        f.write(f"Motivo: {falha['motivo']}\n")
                        f.write(f"Tentativa: {falha['tentativa']}/{self.max_retries}\n")
                        f.write(f"Hora: {falha['timestamp']}\n")
                        f.write("-" * 50 + "\n\n")
                logger.info(f"Log de falhas salvo: {len(self.falhas)} itens")
            except Exception as e:
                logger.error(f"Erro ao salvar log de falhas: {e}")

    def duplicar(self) -> bool:
        """Duplica item."""
        try:
            pyautogui.click(*self.coordenadas.menu_opcoes)
            time.sleep(0.2)
            pyautogui.click(*self.coordenadas.btn_duplicar)
            time.sleep(2)
            return True
        except Exception as e:
            logger.error(f"Erro ao duplicar: {e}")
            return False

    def adiciona_item(self, item: str, descricao: str, preco: str) -> bool:
        """Adiciona item com retry automático."""
        for tentativa in range(1, self.max_retries + 1):
            try:
                logger.info(f"Tentativa {tentativa}/{self.max_retries}: {item}")
                
                pyautogui.press('home')
                time.sleep(0.2)

                if not self.duplicar():
                    raise Exception("Falha ao duplicar")

                # Nome
                pyautogui.click(*self.coordenadas.campo_nome, duration=0.1)
                time.sleep(0.1)
                pyautogui.hotkey("ctrl", "a")
                pyperclip.copy(item)
                pyautogui.hotkey("ctrl", "v")
                time.sleep(0.5)

                # Descrição
                pyautogui.press('tab')
                time.sleep(0.1)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                pyperclip.copy(descricao)
                pyautogui.hotkey("ctrl", "v")
                time.sleep(0.5)

                # Preço
                for _ in range(4):
                    pyautogui.press('tab')
                    time.sleep(0.1)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                pyperclip.copy(preco)
                pyautogui.hotkey("ctrl", "v")
                time.sleep(0.5)

                # Enviar
                pyautogui.click(*self.coordenadas.btn_enviar)
                time.sleep(3)

                logger.info(f"✓ Sucesso: {item}")
                return True

            except Exception as e:
                motivo = str(e)
                self.registrar_falha(item, motivo, tentativa)
                
                if tentativa < self.max_retries:
                    logger.warning(f"Tentando novamente em 2 segundos...")
                    time.sleep(2)
                else:
                    logger.error(f"Falhou após {self.max_retries} tentativas: {item}")
                    return False

        return False

    def processar_arquivo(self, caminho: str = 'data/pizza.txt', 
                         modo_teste: bool = False, num_teste: int = 1) -> Dict:
        """
        Processa arquivo com validação, checkpoint e resumo.
        
        Args:
            caminho: Caminho do arquivo
            modo_teste: Se True, processa apenas num_teste itens
            num_teste: Número de itens para modo teste
        """
        resultado = {
            'total': 0,
            'sucesso': 0,
            'falhas': 0,
            'tempo_total': 0,
            'taxa': 0,
            'itens_falhados': []
        }

        # Validar dados
        valido, linhas, msg = self.validar_dados(caminho)
        if not valido:
            logger.error(msg)
            return resultado

        logger.info(msg)

        # Aplicar modo teste
        if modo_teste:
            linhas = linhas[:num_teste]
            logger.info(f"🔧 MODO TESTE: Processando apenas {num_teste} item(ns)")

        resultado['total'] = len(linhas)
        tempo_inicio = time.time()

        # Carregar checkpoint
        ultimo_item = self.carregar_checkpoint()
        if ultimo_item > 0:
            logger.info(f"Retomando a partir do item {ultimo_item + 1}")
            linhas = linhas[ultimo_item:]

        try:
            for idx, linha in enumerate(linhas, start=ultimo_item + 1):
                try:
                    partes = linha.split('|')
                    nome = partes[0].strip()
                    descricao = partes[1].strip()
                    preco = partes[2].strip()

                    logger.info(f"Processando [{idx}/{resultado['total']}]: {nome}")

                    if self.adiciona_item(nome, descricao, preco):
                        resultado['sucesso'] += 1
                        self.processados.append(nome)
                        som.som_sucesso()
                    else:
                        resultado['falhas'] += 1
                        resultado['itens_falhados'].append(nome)
                        som.som_erro()

                    # Pausa inteligente entre grupos
                    if idx % self.pausa_entre_grupos == 0 and idx < resultado['total']:
                        logger.info(f"Pausa após {self.pausa_entre_grupos} itens...")
                        time.sleep(2)

                    self.salvar_checkpoint(idx)

                except Exception as e:
                    logger.error(f"Erro ao processar linha: {e}")
                    resultado['falhas'] += 1

        except KeyboardInterrupt:
            logger.warning("Automação interrompida pelo usuário")

        finally:
            tempo_total = time.time() - tempo_inicio
            resultado['tempo_total'] = tempo_total
            resultado['taxa'] = (resultado['sucesso'] / max(tempo_total/60, 0.1))

            # Salvar log de falhas
            self.salvar_log_falhas()

            # Limpar checkpoint
            self.limpar_checkpoint()

        return resultado

    def gerar_sumario(self, resultado: Dict) -> str:
        """Gera sumário formatado."""
        minutos = int(resultado['tempo_total'] // 60)
        segundos = int(resultado['tempo_total'] % 60)
        taxa_sucesso = (resultado['sucesso'] / resultado['total'] * 100) if resultado['total'] > 0 else 0

        sumario = f"""
╔════════════════════════════════════════╗
║     RESUMO DA AUTOMAÇÃO                ║
╠════════════════════════════════════════╣
║ Total processado:   {resultado['sucesso']}/{resultado['total']} ({taxa_sucesso:.1f}%)
║ Sucesso:            {resultado['sucesso']}
║ Falhas:             {resultado['falhas']}
║ Tempo total:        {minutos:02d}:{segundos:02d}
║ Velocidade média:   {resultado['taxa']:.1f} itens/min
╚════════════════════════════════════════╝
"""
        if resultado['falhas'] > 0:
            sumario += f"\n⚠️  Itens falhados: {', '.join(resultado['itens_falhados'][:5])}"
            if len(resultado['itens_falhados']) > 5:
                sumario += f" ... e mais {len(resultado['itens_falhados']) - 5}"
            sumario += f"\n📄 Veja 'logs/falhas.txt' para detalhes"

        return sumario
