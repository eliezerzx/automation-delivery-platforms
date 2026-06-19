"""
Automação para criação de complementos no 99Food.
Refatorado com loop, pause/stop, log de progresso e coordenadas via JSON.
"""

import os, sys, time, threading, queue as Q, json

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'  ))
if root_path not in sys.path:
    sys.path.append(root_path)

DATA_PATH   = os.path.join(root_path, 'data')
CONFIG_PATH = os.path.join(root_path, 'config')

# ── Estado ────────────────────────────────────────────────────────────────
state_comp = {
    'fase':          'parado',
    'arquivo':       os.path.join(DATA_PATH, 'complemento.txt'),
    'delay_item':    1.5,
    'delay_conf':    2.5,
    'novo_item':     (924, 775),
    'campo_nome':    (721, 388),
    'btn_confirmar': (1232, 908),
    'inicio_tempo':  None,
    'tempo_pausado': 0.0,
    'pausa_inicio':  None,
    'itens_ok':      0,
    'itens_total':   0,
}

COORD_KEYS_COMP = [
    ('novo_item',    'Btn Novo Item'),
    ('campo_nome',   'Campo Nome'),
    ('btn_confirmar','Btn Confirmar'),
]

def _carregar_coords_comp():
    try:
        with open(os.path.join(CONFIG_PATH, 'coordenadas_complemento.json'), 'r', encoding='utf-8') as f:
            c = json.load(f)
        for key, _ in COORD_KEYS_COMP:
            if key in c:
                state_comp[key] = tuple(c[key])
    except Exception:
        pass

def _salvar_coords_comp():
    try:
        os.makedirs(CONFIG_PATH, exist_ok=True)
        data = {k: list(state_comp[k]) for k, _ in COORD_KEYS_COMP}
        with open(os.path.join(CONFIG_PATH, 'coordenadas_complemento.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

_carregar_coords_comp()

stop_event_comp  = threading.Event()
pause_event_comp = threading.Event()
pause_event_comp.set()

log_queue_comp   = Q.Queue()
coord_queue_comp = Q.Queue()
notif_queue_comp = Q.Queue()

def _push_comp(tipo: str, mensagem: str = ''):
    ts = time.strftime('%H:%M:%S')
    log_queue_comp.put((tipo, mensagem, ts))

def _aguardar_se_pausado_comp() -> bool:
    while not pause_event_comp.is_set():
        if stop_event_comp.is_set(): return False
        time.sleep(0.1)
    return True

def _sleep_cancelavel_comp(segundos: float) -> bool:
    fim = time.time() + segundos
    while time.time() < fim:
        if stop_event_comp.is_set(): return False
        if not pause_event_comp.is_set():
            tr = fim - time.time()
            if not _aguardar_se_pausado_comp(): return False
            fim = time.time() + tr
        time.sleep(0.1)
    return True

# ── Thread de automação ────────────────────────────────────────────────────
def _thread_automacao_comp():
    try:
        from utils import som
    except Exception:
        som = None
    try:
        import pyautogui, pyperclip
        pyautogui.PAUSE = 0.3
        arquivo = state_comp['arquivo']
        _push_comp('separador')
        _push_comp('inicio', 'Iniciando automação Complementos...')
        if not os.path.exists(arquivo):
            _push_comp('erro', f'Arquivo não encontrado: {arquivo}')
            state_comp['fase'] = 'parado'
            stop_event_comp.clear(); pause_event_comp.set(); return
        with open(arquivo, 'r', encoding='utf-8') as f:
            linhas = [l for l in f.readlines() if l.strip()]
        _push_comp('arquivo', f'{len(linhas)} itens em {os.path.basename(arquivo)}')
        _push_comp('separador')
        state_comp['itens_total'] = len(linhas)
        time.sleep(1)
        adicionados = falhados = 0
        for i, linha in enumerate(linhas, 1):
            if stop_event_comp.is_set():
                _push_comp('parada', 'Automação interrompida.'); break
            if not pause_event_comp.is_set():
                _push_comp('pausa', f'Pausado antes do item {i}...')
                if not _aguardar_se_pausado_comp():
                    _push_comp('parada', 'Parado durante pausa.'); break
                _push_comp('retomada', 'Retomando...')
            try:
                partes = linha.strip().split('|')
                if len(partes) < 2:
                    _push_comp('aviso', f'Linha {i} inválida'); falhados += 1; continue
                nome  = partes[0].strip()
                preco_txt = partes[-1].strip()
                preco = float(preco_txt.replace(',', '.'))
                _push_comp('item', f'[{i}/{len(linhas)}] {nome} — R$ {preco:.2f}')
                # Clica em "Novo Item"
                pyautogui.click(*state_comp['novo_item'], duration=0.1)
                if not _sleep_cancelavel_comp(state_comp['delay_item']):
                    _push_comp('parada', 'Parado no delay novo item.'); break
                # Preenche nome
                pyautogui.click(*state_comp['campo_nome'], duration=0.1)
                time.sleep(0.1)
                pyautogui.hotkey('ctrl', 'a'); pyperclip.copy(nome); pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.3)
                # Navega para categoria (tab tab) e seleciona (enter up enter)
                pyautogui.press('tab'); time.sleep(0.1)
                pyautogui.press('tab'); time.sleep(0.1)
                pyautogui.press('enter'); time.sleep(0.1)
                pyautogui.press('up');   time.sleep(0.1)
                pyautogui.press('enter'); time.sleep(0.1)
                # Navega para preço (tab) e preenche
                pyautogui.press('tab'); time.sleep(0.1)
                pyautogui.hotkey('ctrl', 'a')
                pyperclip.copy(f'{preco:.2f}'); pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.3)
                # Confirma
                pyautogui.click(*state_comp['btn_confirmar'], duration=0.1)
                if not _sleep_cancelavel_comp(state_comp['delay_conf']):
                    _push_comp('parada', 'Parado no delay confirmar.'); break
                _push_comp('sucesso', f'"{nome}" adicionado')
                adicionados += 1; state_comp['itens_ok'] = adicionados
            except Exception as e:
                _push_comp('erro', f'Erro item {i}: {e}'); falhados += 1
        _push_comp('separador')
        _push_comp('resumo', f'Concluído — {adicionados} adicionados  {falhados} falhados')
        _push_comp('separador')
        if not stop_event_comp.is_set():
            notif_queue_comp.put(('sucesso' if falhados == 0 else 'aviso', adicionados, falhados))
        if som:
            if falhados == 0 and adicionados > 0: som.som_sucesso()
            elif falhados > 0: som.som_erro()
    except Exception as e:
        _push_comp('erro', f'Erro fatal: {e}')
    finally:
        state_comp['fase'] = 'parado'
        stop_event_comp.clear(); pause_event_comp.set()
