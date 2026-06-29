"""O arquivo contem o conjunto de funções que estrutura a criação de um adicional no iFood com a automação.
* Favor, não colocar numeros de coordenadas fixas no código, usar o arquivo coordenada.json para tal.
* Dar preferência em usar e criar funções para manter a organização e limpeza do script.
Isabelly Faria - 30/01/2026 """
import atalhosPyautogui
import Coordenada
coordenadas = Coordenada.carregarCoordenadas()
def criarNovoGrupo(nome='Grupo de Adicionais',min=0,max=1):
    #clicka em novo grupo
    atalhosPyautogui.clickar(coordenadas['btn_adicionarGrupo_complemento'])
    atalhosPyautogui.clickar(coordenadas['btn_criarNovoGrupo_complemento'])
    atalhosPyautogui.clickar(coordenadas['btn_continuar_complemento'])
    #seleciona o tipo 'ingrediente'
    atalhosPyautogui.clickar(coordenadas['btn_ingredientes_complemento'])
    atalhosPyautogui.clickar(coordenadas['btn_continuar_complemento'])
    #adiciona o nome do grupo
    pyperclip.copy(nome)
    time.sleep(0.1)
    atalhosPyautogui.copiar(coordenadas['campo_nomeGrupo_complemento'], duracao=0.3)
    #seleciona a quantidade minima e maxima
    #máximo
    atalhosPyautogui.clickar(coordenadas['campo_qtdMaxima_complemento'], qtd=max,duracao=0.3)]
    #minimo
    atalhosPyautogui.clickar(coordenadas['campo_qtdMinima_complemento'], qtd=min,duracao=0.3)]
    #finaliza o grupo
    atalhosPyautogui.clickar(coordenadas['btn_continuar_complemento'])
    
def finalizarGrupo():
    #clickar no botão de concluir
    atalhosPyautogui.clickar(coordenadas['btn_concluir_grupo_complemento'])
def clickarNovoComplemento():
    #clicka em novo complemento
    atalhosPyautogui.clickar(coordenadas['btn_criarNovoComplemento_complemento'])
    time.sleep(3)
    #seleciona o tipo 'ingrediente'
    atalhosPyautogui.clickar(coordenadas['btn_selecionarTipo_complemento'])
    atalhosPyautogui.clickar(coordenadas['btn_selecionar_ingrediente'])
    time.sleep(1)

def adicionarNome(nome_produto):
    #Clica no campo de nome e realiza movimento
    atalhosPyautogui.clickar(coordenadas['campo_nome_complemento'], duracao=0.3)
    #copia o nome
    pyperclip.copy(nome_produto)
    time.sleep(1)
    print(pyperclip.paste())
    time.sleep(0.5)
    atalhosPyautogui.colar(coordenadas['campo_nome_complemento'])

def adicionarDescricao(descricao_produto):
    pyperclip.copy(descricao_produto)
    time.sleep(0.5)
    atalhosPyautogui.colar(coordenadas[campo_descricao_complemento])

def adicionarPreco(preco_produto):
    #preciso pegar coordenada
    pyautogui.scroll(-300)
    pyperclip.copy(preco_produto)
    time.sleep(0.5)
    atalhosPyautogui.colar(coordenadas['campo_preco_complemento'])
def finalizarProduto():
    #clickar no botão de concluir
    atalhosPyautogui.clickar(coordenadas['btn_adicionarAoGrupo_complemento'])
    time.sleep(2)
    