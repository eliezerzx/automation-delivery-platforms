# pip install selenium webdriver-manager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import time
import html

# ==========================
# Configurações e variáveis
# ==========================
CATEGORIA = "Supreme"
PRECO_DESCONTO = "7990"
PRECO_ORIGINAL  = "11490"

# Título EXATO da seção/“lista” (vem no atributo title do <span>).
# Ex.: >>> Pizzas Mais Vendidas 1 <<<
TITULO_SECAO = ">>> Pizzas Mais Vendidas 1 <<<"

# (Opcional) Só editar itens cujo nome contenha esse trecho (case sensitive):
FILTRO_NOME_ITEM_CONTÉM = None      # exemplo: "Broto inteira"  | ou deixe None para pegar todos da seção

DEFAULT_TIMEOUT = 20

SELETORS = {
    # Cards da listagem:
    "cards_todos": (By.CSS_SELECTOR, "[data-testid^='item-card-']"),

    # Botão de opções (⋮) dentro do card
    "botao_opcoes_item": (By.CSS_SELECTOR, "[data-testid='item-menu-options']"),

    # Item do menu "Editar item"
    "menu_editar": (By.XPATH, "//span[normalize-space()='Editar item']"),

    # Campo nome do produto (na tela de edição)
    "campo_nome_produto": (By.CSS_SELECTOR, "input[name='name']"),

    # Aba "Disponível em"
    "aba_disponivel_em": (By.XPATH, "//button[.//span[normalize-space()='Disponível em']]"),

    # Botão para abrir edição de preço/desconto (ícone de desconto)
    "abrir_edicao_preco": (By.CSS_SELECTOR, "button[aria-label='discount']"),

    # Inputs de preço (ordem: original, depois desconto)
    "inputs_preco": (By.CSS_SELECTOR, "input[data-testid='currency-field']"),

    # Botão "Aplicar" do modal/preço
    "botao_aplicar": (By.XPATH, "//button[normalize-space()='Aplicar']"),
}

# ========= helpers =========
def wait_for(driver, locator, condition="visible", timeout=DEFAULT_TIMEOUT):
    by, sel = locator
    w = WebDriverWait(driver, timeout)
    if condition == "visible":
        return w.until(EC.visibility_of_element_located((by, sel)))
    if condition == "clickable":
        return w.until(EC.element_to_be_clickable((by, sel)))
    if condition == "present":
        return w.until(EC.presence_of_element_located((by, sel)))
    if condition == "invisible":
        return w.until(EC.invisibility_of_element_located((by, sel)))
    raise ValueError("condição desconhecida")

def get_value(el):
    val = el.get_attribute("value")
    if not val:
        val = el.text
    return (val or "").strip()

def set_text(el, text):
    el.click()
    el.send_keys(Keys.CONTROL, "a")
    el.send_keys(Keys.DELETE)
    el.send_keys(text)

def scroll_to_center(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)

# ========= fluxo de edição =========
def editar_produto_atual(driver):
    """equivale ao seu executar()"""
    nome_el = wait_for(driver, SELETORS["campo_nome_produto"], "visible")
    texto = get_value(nome_el)

    if "-" in texto:
        esquerda, direita = texto.split("-", 1)
        esquerda_mod = f"{esquerda.strip()} {CATEGORIA}"
        novo_texto = f"{esquerda_mod} - {direita.strip()}"
    else:
        novo_texto = f"{texto.strip()} {CATEGORIA}"

    set_text(nome_el, novo_texto)

    # Aba Disponível em
    try:
        aba = wait_for(driver, SELETORS["aba_disponivel_em"], "clickable")
        scroll_to_center(driver, aba)
        aba.click()
    except TimeoutException:
        pass

    # Abrir edição de preços
    btn_preco = wait_for(driver, SELETORS["abrir_edicao_preco"], "clickable")
    scroll_to_center(driver, btn_preco)
    btn_preco.click()

    # Inputs de preço
    inputs = WebDriverWait(driver, DEFAULT_TIMEOUT).until(
        EC.visibility_of_all_elements_located(SELETORS["inputs_preco"])
    )
    if len(inputs) < 2:
        raise RuntimeError("Não encontrei os dois campos de preço.")
    set_text(inputs[0], PRECO_ORIGINAL)
    set_text(inputs[1], PRECO_DESCONTO)

    # Aplicar
    aplicar = wait_for(driver, SELETORS["botao_aplicar"], "clickable")
    scroll_to_center(driver, aplicar)
    aplicar.click()

    # Espera o “Aplicar” sumir (ou ajuste aqui para outra condição da sua UI)
    try:
        wait_for(driver, SELETORS["botao_aplicar"], "invisible", timeout=15)
    except TimeoutException:
        time.sleep(1.0)

def abrir_item_para_editar(driver, card_el):
    """No card, clicar no ⋮ e depois em 'Editar item'."""
    btn_opts = card_el.find_element(*SELETORS["botao_opcoes_item"])
    scroll_to_center(driver, btn_opts)
    btn_opts.click()

    editar = wait_for(driver, SELETORS["menu_editar"], "clickable")
    scroll_to_center(driver, editar)
    editar.click()

    wait_for(driver, SELETORS["campo_nome_produto"], "visible")

# ========= filtrar por seção =========
def encontrar_cards_da_secao(driver, titulo_secao):
    """
    Localiza a seção pelo <span title="..."> e retorna SOMENTE os cards dentro dessa seção.
    """
    # Atenção: no HTML o title vem “escapado”, então garanta que estamos comparando exatamente.
    titulo_escapado = html.escape(titulo_secao)  # transforma <<< em &lt;&lt;&lt; etc, como no seu print
    # Encontra o span do título
    titulo_el = WebDriverWait(driver, DEFAULT_TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH,
            f"//span[@title='{titulo_escapado}']"
        ))
    )
    scroll_to_center(driver, titulo_el)

    # Sobe para o container da seção (o primeiro ancestral que contém botões 'Criar combo' OU 'Adicionar item')
    # Ajuste se necessário, mas costuma ser robusto:
    container_secao = titulo_el.find_element(
        By.XPATH,
        "./ancestor::div[.//button[normalize-space()='Criar combo'] or .//button[normalize-space()='Adicionar item']][1]"
    )

    # Busca os cards apenas dentro desse container
    cards = container_secao.find_elements(*SELETORS["cards_todos"])
    return cards

# ========= loop principal =========
def processar_filtrado(driver, titulo_secao, filtro_nome_item_contem=None):
    cards = encontrar_cards_da_secao(driver, titulo_secao)
    if not cards:
        raise RuntimeError(f"Nenhum item encontrado na seção: {titulo_secao}")

    # Filtra por nome do item (texto que aparece no card), se solicitado
    if filtro_nome_item_contem:
        alvo = filtro_nome_item_contem
        cards = [c for c in cards if alvo in c.text]
        if not cards:
            raise RuntimeError(f"Nenhum item na seção contém '{alvo}' no nome.")

    for idx, card in enumerate(cards, start=1):
        abrir_item_para_editar(driver, card)
        editar_produto_atual(driver)

        # Volta para a lista (rota anterior)
        driver.back()

        # Aguarda reaparecer a seção e re-coleta os cards (DOM muda após voltar)
        WebDriverWait(driver, DEFAULT_TIMEOUT).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//span[@title='{html.escape(titulo_secao)}']")
            )
        )
        cards = encontrar_cards_da_secao(driver, titulo_secao)

def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    from selenium.webdriver.chrome.service import Service

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)


    try:
        driver.get("https://portal.ifood.com.br/menu/list")
        # TODO: faça o login se precisar (localize os campos e entre)

        # Aguarda aparecer qualquer card (ou ao menos a página de cardápio)
        try:
            WebDriverWait(driver, DEFAULT_TIMEOUT).until(
                EC.presence_of_element_located(SELETORS["cards_todos"])
            )
        except TimeoutException:
            # se não houver cards visíveis (ex.: só aparece depois do scroll), pelo menos confira que carregou a página
            time.sleep(2)

        # Processa SOMENTE a seção pedida (e opcionalmente, apenas itens cujo nome contenha um texto)
        processar_filtrado(
            driver,
            titulo_secao=TITULO_SECAO,
            filtro_nome_item_contem=FILTRO_NOME_ITEM_CONTÉM,
        )

        print("Pronto!")

    finally:
        # driver.quit()
        pass

if __name__ == "__main__":
    main()
