"""
Automação para criação de cardápio.
Refatorizado para melhor manutenibilidade e robustez.
"""

import pyautogui
import time
import os
import sys
import pyperclip
import logging
import math
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Tuple

# --- Configuração de caminho ---
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# --- Configuração de logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(root_path, 'logs', 'automacao.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
if root_path not in sys.path:
    sys.path.append(root_path)

from utils import som

# Configuração global
pyautogui.PAUSE = 0.5


@dataclass
class Coordenadas:
    """Armazena coordenadas de cliques da interface."""
    menu_opcoes: Tuple[int, int]
    btn_duplicar: Tuple[int, int]
    campo_nome: Tuple[int, int]
    btn_enviar: Tuple[int, int]

    @classmethod
    def carregar_config(cls, arquivo: str = None) -> 'Coordenadas':
        """Carrega coordenadas de um arquivo JSON."""
        if arquivo is None:
            arquivo = os.path.join(root_path, 'config', 'coordenadas.json')
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


@dataclass
class ConfiguracaoTempo:
    """Configuração de delays para operações."""
    pausa_menu: float = 0.2
    pausa_duplicacao: float = 2
    pausa_tabtab: float = 0.1
    pausa_preco: float = 0.5
    pausa_envio: float = 3


class AutomacaoCardapio:
    """Gerencia automação de criação de cardápio."""

    def __init__(self, coordenadas: Optional[Coordenadas] = None,
                 config_tempo: Optional[ConfiguracaoTempo] = None):
        self.coordenadas = coordenadas or Coordenadas.carregar_config()
        self.config = config_tempo or ConfiguracaoTempo()
        logger.info("Automação inicializada")

    def duplicar(self) -> bool:
        """
        Duplica o item atual abrindo o menu e clicando em duplicar.

        Returns:
            bool: True se bem-sucedido, False caso contrário.
        """
        try:
            logger.info("Abrindo menu de opções...")
            pyautogui.click(*self.coordenadas.menu_opcoes)
            time.sleep(self.config.pausa_menu)

            logger.info("Clicando em duplicar...")
            pyautogui.click(*self.coordenadas.btn_duplicar)
            time.sleep(self.config.pausa_duplicacao)

            return True
        except Exception as e:
            logger.error(f"Erro ao duplicar item: {e}")
            return False

    def _preencher_campo_com_tab(self, valor: str, num_tabs: int = 1) -> None:
        """
        Preenche um campo de formulário navegando com TAB e inserindo valor.

        Args:
            valor: Texto ou número a ser inserido.
            num_tabs: Quantidade de TABs antes de preencher.
        """
        for _ in range(num_tabs):
            pyautogui.press('tab')
            time.sleep(self.config.pausa_tabtab)

        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        pyperclip.copy(valor)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.2)

    def adiciona_item(self, item: str, descricao: str, preco: str) -> bool:
        """
        Adiciona um novo item ao cardápio.

        Args:
            item: Nome do item
            descricao: Descrição do item
            preco: Preço em formato string (ex: "37.90")

        Returns:
            bool: True se bem-sucedido, False caso contrário.
        """
        try:
            logger.info(f"Adicionando item: {item}")

            # Volta ao topo da página
            pyautogui.press('home')
            time.sleep(0.2)

            # Duplica o item
            if not self.duplicar():
                return False

            # Preenche nome do item
            logger.info("Preenchendo nome...")
            pyautogui.click(*self.coordenadas.campo_nome, duration=0.1)
            time.sleep(0.1)
            pyautogui.hotkey("ctrl", "a")
            pyperclip.copy(item)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.5)

            # Preenche descrição (2 TABs)
            logger.info("Preenchendo descrição...")
            self._preencher_campo_com_tab(descricao, num_tabs=2)

            # Preenche preço (5 TABs)
            logger.info(f"Preenchendo preço: {preco}...")
            self._preencher_campo_com_tab(preco, num_tabs=5)
            time.sleep(self.config.pausa_preco)

            # Clica em Enviar
            logger.info("Enviando formulário...")
            pyautogui.moveTo(*self.coordenadas.btn_enviar, duration=0.1)
            pyautogui.click()
            time.sleep(self.config.pausa_envio)

            logger.info(f"✓ Item '{item}' adicionado com sucesso")
            return True

        except Exception as e:
            logger.error(f"Erro ao adicionar item '{item}': {e}")
            return False

    def processar_arquivo_pizza(self, caminho_arquivo: str = 'data/pizza.txt') -> bool:
        """
        Processa arquivo de pizza e adiciona itens ao cardápio.

        Args:
            caminho_arquivo: Caminho para arquivo de entrada

        Returns:
            bool: True se todos os itens foram adicionados, False caso contrário.
        """
        try:
            # Alterna para a janela da aplicação
            logger.info("Alternando para janela da aplicação...")
            time.sleep(0.5)

            # Lê o arquivo
            if not os.path.exists(caminho_arquivo):
                raise FileNotFoundError(f"Arquivo {caminho_arquivo} não encontrado")

            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                linhas = arquivo.readlines()

            logger.info(f"Processando {len(linhas)} linhas do arquivo")

            itens_adicionados = 0
            itens_falhados = 0

            for i, linha in enumerate(linhas, start=1):
                # Remove linhas vazias
                if not linha.strip():
                    continue

                try:
                    # Parse da linha
                    partes = linha.strip().split('|')
                    if len(partes) != 3:
                        logger.warning(f"Linha {i} com formato inválido: {linha.strip()}")
                        itens_falhados += 1
                        continue

                    nome, descricao, preco_txt = partes

                    # Valida e formata os dados
                    nome = nome.strip()
                    descricao = descricao.strip() + " Foto Ilustrativa."

                    try:
                        preco_base = float(preco_txt.strip().replace(',', '.'))
                    except ValueError:
                        logger.warning(f"Preço inválido na linha {i}: {preco_txt}")
                        itens_falhados += 1
                        continue

                    # Calcula desconto (mantém lógica original)
                    desconto_valor = math.floor(preco_base) + 0.9

                    # Adiciona item
                    if self.adiciona_item(nome, descricao, f"{preco_base:.2f}"):
                        itens_adicionados += 1
                    else:
                        itens_falhados += 1

                except Exception as e:
                    logger.error(f"Erro processando linha {i}: {e}")
                    itens_falhados += 1

            # Resumo final
            logger.info(f"\n{'='*50}")
            logger.info(f"Resumo: {itens_adicionados} adicionados, {itens_falhados} falhados")
            logger.info(f"{'='*50}")

            return itens_falhados == 0

        except FileNotFoundError as e:
            logger.error(f"Arquivo não encontrado: {e}")
            som.som_erro()
            pyautogui.alert(f"❌ ERRO:\nArquivo não encontrado: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            som.som_erro()
            pyautogui.alert(f"❌ ERRO:\n{str(e)}")
            return False

    def executar_cardapio(self, caminho_arquivo: str = None) -> None:
        """
        Executa o processo completo de criação de cardápio.

        Args:
            caminho_arquivo: Caminho para arquivo de entrada
        """
        if caminho_arquivo is None:
            caminho_arquivo = os.path.join(root_path, 'data', 'pizza.txt')
        logger.info("Iniciando criação de cardápio...")

        sucesso = self.processar_arquivo_pizza(caminho_arquivo)

        if sucesso:
            som.som_sucesso()
            pyautogui.alert("✅ Cardápio finalizado com sucesso!")
            logger.info("Cardápio criado com sucesso!")
        else:
            logger.error("Cardápio criado com erros. Verifique o log.")


def main():
    """Função principal."""
    try:
        automacao = AutomacaoCardapio()
        automacao.executar_cardapio()
    except KeyboardInterrupt:
        logger.info("Automação cancelada pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        som.som_erro()


# Alias para compatibilidade com menu.py
criaCardapio = main

if __name__ == "__main__":
    main()