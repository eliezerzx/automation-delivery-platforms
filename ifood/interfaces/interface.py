import os

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def exibir_menu():
    limpar_tela()
    print("""
╔══════════════════════════════════════════════════════════════╗
║             --- IFOOD AUTOMATION SYSTEM v2.0 ---             ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   [ GESTÃO DE CARDÁPIO ]                                     ║
║    [1] Criar Novo Cardápio                                   ║
║    [2] Criar Complementos (Adicionais)                       ║
║    [3] Configurar 2 Sabores                                  ║
║                                                              ║
║   [ FINANCEIRO / DESCONTOS ]                                 ║
║    [4] Aplicar Descontos em Massa                            ║
║    [5] Remover Descontos Ativos                              ║
║    [6] Remover Descontos & Alterar Valor                     ║
║                                                              ║
║   [ CONFIGURAÇÕES TÉCNICAS ]                                 ║
║    [9] Pegar Coordenada (Setup)                              ║
║    [0] Sair do Programa                                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
