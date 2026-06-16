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
║    [2] Criar Novo Cardápio (Versão Nova)                     ║
║    [3] -                                                     ║
║                                                              ║
║   [ FINANCEIRO / DESCONTOS ]                                 ║
║    [4] -                                                     ║
║    [5] -                                                     ║
║    [6] -                                                     ║
║                                                              ║
║   [ CONFIGURAÇÕES TÉCNICAS ]                                 ║            
║    [9] Pegar Coordenada (Setup)                              ║
║    [0] Sair do Programa                                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
