"""
Painel de Estoque iFood - NiceGUI  (port 8086)
Preenche automaticamente todos os campos de Estoque com o valor configurado.
Usa locateAllOnScreen para encontrar múltiplos campos de uma vez.
"""

import os, sys, time, threading, queue as queue_module, json

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.append(root_path)

DATA_PATH   = os.path.join(root_path, 'data')
CONFIG_PATH = os.path.join(root_path, 'config')
IMG_PATH    = os.path.join(root_path, 'img')

from nicegui import ui

# ── Estado ────────────────────────────────────────────────────────────────
state = {
    'fase':             'parado',
    'delay_item':       1.5,      # delay entre cada preenchimento (s)
    'delay_erro':       30.0,     # pausa ao detectar erro de rate limit (s)
    'delay_retry':      2.0,      # pausa antes de retentar campo com erro (s)
    'max_retries':      3,        # tentativas por campo antes de desistir
    'max_scrolls_vazio': 3,       # scrolls sem resultado antes de encerrar
    'valor_estoque':    '99999',  # valor a preencher
    'inicio_tempo':     None,
    'tempo_pausado':    0.0,
    'pausa_inicio':     None,
    'itens_ok':         0,
}

CONFIG_FILE = os.path.join(CONFIG_PATH, 'estoque_ifood.json')

def _carregar_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            c = json.load(f)
        for k in ('delay_item', 'delay_erro', 'max_scrolls_vazio', 'valor_estoque'):
            if k in c:
                state[k] = c[k]
    except Exception:
        pass

def _salvar_config():
    try:
        os.makedirs(CONFIG_PATH, exist_ok=True)
        data = {k: state[k] for k in ('delay_item', 'delay_erro', 'delay_retry', 'max_retries', 'max_scrolls_vazio', 'valor_estoque')}
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

_carregar_config()

stop_event  = threading.Event()
pause_event = threading.Event()
pause_event.set()

log_queue   = queue_module.Queue()
notif_queue = queue_module.Queue()

LOG_ICONS = {
    'inicio':    ('rocket_launch', '#EA1D2C'),
    'item':      ('play_arrow',    '#EA1D2C'),
    'sucesso':   ('check_circle',  '#22c55e'),
    'erro':      ('cancel',        '#ef4444'),
    'aviso':     ('warning',       '#f97316'),
    'parada':    ('block',         '#ef4444'),
    'pausa':     ('pause_circle',  '#EA1D2C'),
    'retomada':  ('play_circle',   '#22c55e'),
    'resumo':    ('bar_chart',     '#EA1D2C'),
    'info':      ('info',          '#94a3b8'),
    'scroll':    ('keyboard_arrow_down', '#64748b'),
    'separador': ('remove',        '#1e293b'),
}

log_ref    = {'container': None, 'scroll': None}
ui_refs    = {}
notif_queue = queue_module.Queue()

def _push(tipo: str, mensagem: str = ''):
    ts = time.strftime('%H:%M:%S')
    log_queue.put((tipo, mensagem, ts))

def _aguardar_se_pausado() -> bool:
    while not pause_event.is_set():
        if stop_event.is_set(): return False
        time.sleep(0.1)
    return True

def _sleep_cancelavel(segundos: float) -> bool:
    fim = time.time() + segundos
    while time.time() < fim:
        if stop_event.is_set(): return False
        if not pause_event.is_set():
            tr = fim - time.time()
            if not _aguardar_se_pausado(): return False
            fim = time.time() + tr
        time.sleep(0.1)
    return True

# ── Thread de automação ────────────────────────────────────────────────────
def _thread_automacao():
    try:
        import pyautogui, pyperclip
        pyautogui.PAUSE    = 0.2
        pyautogui.FAILSAFE = False

        img_estoque       = os.path.join(IMG_PATH, 'estoque_input.png')
        img_erro          = os.path.join(IMG_PATH, 'erro_vermelho.png')
        img_erro_estoque  = os.path.join(IMG_PATH, 'erro_estoque.png')  # "Falha ao atualizar estoque!"

        if not os.path.exists(img_estoque):
            _push('aviso', f'Imagem não encontrada: estoque_input.png em {IMG_PATH}')
            _push('aviso', 'Tire um print do campo de estoque e salve como ifood/img/estoque_input.png')

        _push('separador')
        _push('inicio', 'Iniciando automação — Estoque iFood...')
        _push('info',   f'Valor: {state["valor_estoque"]} | Delay: {state["delay_item"]}s | Max scrolls vazios: {state["max_scrolls_vazio"]}')
        _push('separador')
        time.sleep(1.0)

        preenchidos      = 0
        scrolls_sem_item = 0
        valor            = state['valor_estoque']

        while True:
            # ── [PAUSA/PARADA] ─────────────────────────────────────────────
            if stop_event.is_set():
                _push('parada', 'Automação interrompida.'); break
            if not pause_event.is_set():
                _push('pausa', 'Pausado...')
                if not _aguardar_se_pausado():
                    _push('parada', 'Parado durante pausa.'); break
                _push('retomada', 'Retomando...')

            # ── [ERRO VERMELHO] Verifica se apareceu mensagem de erro ───────
            if os.path.exists(img_erro):
                try:
                    loc_erro = pyautogui.locateOnScreen(img_erro, confidence=0.7)
                    if loc_erro:
                        _push('erro', f'Mensagem de erro detectada! Aguardando {state["delay_erro"]:.0f}s...')
                        if not _sleep_cancelavel(state['delay_erro']):
                            break
                        _push('retomada', 'Retomando após pausa de erro...')
                        continue
                except Exception:
                    pass

            # ── [LOCALIZAR] Busca todos os campos de estoque visíveis ───────
            _push('info', 'Buscando campos de estoque na tela...')
            locais = []
            try:
                resultado = list(pyautogui.locateAllOnScreen(img_estoque, confidence=0.8))
                locais = sorted(resultado, key=lambda r: r.top)
            except Exception as e:
                _push('aviso', f'locateAllOnScreen: {e}')

            if not locais:
                scrolls_sem_item += 1
                _push('scroll', f'Nenhum campo encontrado — scroll {scrolls_sem_item}/{state["max_scrolls_vazio"]}')

                if scrolls_sem_item >= state['max_scrolls_vazio']:
                    _push('resumo', f'Nenhum campo após {state["max_scrolls_vazio"]} scrolls — encerrando.')
                    break

                # Scroll para baixo e tenta novamente
                pyautogui.scroll(-500)
                time.sleep(0.8)
                continue

            # Encontrou campos — reseta contador de scrolls vazios
            scrolls_sem_item = 0
            _push('info', f'{len(locais)} campo(s) encontrado(s) na tela')

            # ── [PREENCHER] Processa cada campo encontrado ──────────────────
            for i, loc in enumerate(locais, 1):
                if stop_event.is_set():
                    _push('parada', 'Interrompido durante preenchimento.'); break
                if not pause_event.is_set():
                    _push('pausa', f'Pausado antes do campo {i}...')
                    if not _aguardar_se_pausado():
                        _push('parada', 'Parado durante pausa.'); break
                    _push('retomada', 'Retomando...')

                # ── [ERRO VERMELHO DE RATE LIMIT] Verifica antes de cada campo
                if os.path.exists(img_erro):
                    try:
                        loc_err_rate = pyautogui.locateOnScreen(img_erro, confidence=0.7)
                        if loc_err_rate:
                            _push('erro', f'Rate limit detectado! Aguardando {state["delay_erro"]:.0f}s...')
                            if not _sleep_cancelavel(state['delay_erro']):
                                break
                            _push('retomada', 'Retomando...')
                    except Exception:
                        pass

                # ── [RETRY LOOP] Tenta preencher o campo, repete se der erro
                tentativa = 0
                campo_ok  = False
                while tentativa < state['max_retries']:
                    tentativa += 1
                    if stop_event.is_set(): break

                    cx, cy = pyautogui.center(loc)
                    pyautogui.click(cx, cy)
                    time.sleep(0.3)
                    pyautogui.hotkey('ctrl', 'a')
                    time.sleep(0.1)
                    pyautogui.typewrite(valor, interval=0.03)
                    time.sleep(0.1)
                    pyautogui.press('tab')  # confirma

                    # Aguarda um momento para ver se aparece "Falha ao atualizar"
                    time.sleep(1.2)

                    # ── [VERIFICAR ERRO DO CAMPO] ──────────────────────────
                    erro_campo = False
                    if os.path.exists(img_erro_estoque):
                        try:
                            loc_ef = pyautogui.locateOnScreen(img_erro_estoque, confidence=0.75)
                            if loc_ef:
                                erro_campo = True
                        except Exception:
                            pass

                    if erro_campo:
                        if tentativa < state['max_retries']:
                            _push('aviso', f'Falha ao atualizar campo — tentativa {tentativa}/{state["max_retries"]}. Aguardando {state["delay_retry"]:.1f}s...')
                            if not _sleep_cancelavel(state['delay_retry']):
                                break
                            # Volta a clicar no campo para limpar o erro e tentar de novo
                            pyautogui.click(cx, cy)
                            time.sleep(0.3)
                        else:
                            _push('erro', f'Campo falhou após {state["max_retries"]} tentativas — pulando.')
                    else:
                        campo_ok = True
                        break  # sucesso — sai do retry loop

                if stop_event.is_set(): break

                if campo_ok:
                    preenchidos += 1
                    state['itens_ok'] = preenchidos
                    _push('sucesso', f'Campo {preenchidos} preenchido com {valor}')

                # Delay entre campos (evita rate limit)
                if not _sleep_cancelavel(state['delay_item']):
                    break

            # Após processar todos os visíveis, scroll para verificar mais
            if not stop_event.is_set():
                _push('scroll', 'Rolando para verificar mais campos...')
                pyautogui.scroll(-500)
                time.sleep(0.8)

        # ── [RESUMO] ─────────────────────────────────────────────────────────
        _push('separador')
        _push('resumo', f'Concluído — {preenchidos} campos preenchidos com {valor}')
        _push('separador')
        if not stop_event.is_set():
            notif_queue.put(('sucesso', preenchidos))

    except Exception as e:
        _push('erro', f'Erro fatal: {e}')
    finally:
        state['fase'] = 'parado'
        stop_event.clear(); pause_event.set()

_btn_ini_global = {'el': None}
_btn_pau_global = {'el': None}
_btn_par_global = {'el': None}

# ── UI ────────────────────────────────────────────────────────────────────
def iniciar_painel():

    ui.add_head_html("""
<style>
* { box-sizing:border-box; margin:0; padding:0; }
body  { background:#0b1120 !important; }
.q-page { padding:0 !important; }
.q-drawer__content { overflow-y:auto !important; }
::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:#2d3748; border-radius:4px; }
.card { background:#131c2e; border:1px solid #1e2d45; border-radius:14px; padding:18px; }
.dash-item { display:flex; align-items:center; gap:10px; padding:10px 14px; border-radius:9px; cursor:pointer; color:#94a3b8; font-size:13px; user-select:none; transition:all .15s; border-left:3px solid transparent; }
.dash-item:hover { background:rgba(255,255,255,.04); color:#cbd5e1; }
.dash-item.active { background:rgba(234,29,44,.1); border-left-color:#EA1D2C; color:#EA1D2C; font-weight:700; }
.nav-item { display:flex; align-items:center; gap:10px; padding:9px 14px; border-radius:9px; cursor:pointer; color:#94a3b8; font-size:13px; user-select:none; transition:all .15s; border-left:3px solid transparent; }
.nav-item:hover { background:rgba(255,255,255,.04); color:#cbd5e1; }
.nav-item.active { background:rgba(234,29,44,.1); border-left-color:#EA1D2C; color:#EA1D2C; font-weight:700; }
.sec-lbl { font-size:10px; font-weight:800; letter-spacing:.12em; text-transform:uppercase; color:#374151; display:block; padding:0 14px; margin-bottom:4px; margin-top:2px; }
.spinner-ring { width:62px; height:62px; border-radius:50%; border:5px solid rgba(234,29,44,.15); border-top-color:#EA1D2C; flex-shrink:0; }
@keyframes spin { to { transform:rotate(360deg); } }
.spinner-ring.spinning { animation:spin .8s linear infinite; }
.spinner-ring.paused   { border-top-color:#b91c1c; animation:spin 2s linear infinite; }
.spinner-ring.stopped  { border-top-color:#ef4444; }
.stat-box { flex:1; min-width:0; background:#0f172a; border:1px solid #1e293b; border-radius:12px; padding:14px; display:flex; align-items:center; gap:10px; }
.stat-icon { width:34px; height:34px; border-radius:9px; background:#1e293b; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.prog-track { background:#1e293b; border-radius:4px; height:5px; width:100%; margin-top:5px; overflow:hidden; }
.prog-fill  { background:linear-gradient(90deg,#b91c1c,#EA1D2C); height:5px; width:0%; transition:width .4s; border-radius:4px; }
@keyframes pulse-glow { 0%,100% { box-shadow:0 4px 14px rgba(234,29,44,.3); } 50% { box-shadow:0 4px 26px rgba(234,29,44,.65); transform:translateY(-1px); } }
.btn-ini { flex:1; min-width:0; background:linear-gradient(135deg,#EA1D2C,#b91c1c) !important; color:#fff !important; font-weight:800 !important; border-radius:10px !important; padding:12px !important; text-transform:none !important; font-size:14px !important; animation:pulse-glow 2s ease-in-out infinite; transition:all .2s !important; }
.btn-ini[disabled]  { opacity:.4 !important; animation:none !important; }
.btn-ini.running    { animation:none !important; background:linear-gradient(135deg,#166534,#15803d) !important; }
.btn-ctrl { flex:1; min-width:0; background:#1e293b !important; border:1px solid #2d3748 !important; color:#cbd5e1 !important; font-weight:600 !important; border-radius:10px !important; padding:12px !important; text-transform:none !important; font-size:14px !important; transition:all .2s !important; }
.btn-ctrl:hover:not([disabled]) { background:#243044 !important; border-color:#3d4f6a !important; }
.btn-ctrl[disabled] { opacity:.35 !important; }
.btn-resume { flex:1; min-width:0; background:linear-gradient(135deg,#16a34a,#15803d) !important; color:#fff !important; font-weight:700 !important; border-radius:10px !important; padding:12px !important; text-transform:none !important; font-size:14px !important; }
.btn-resume[disabled] { opacity:.35 !important; }
.btn-stop-sm { background:#ef4444 !important; color:#fff !important; font-weight:700 !important; border-radius:8px !important; padding:8px 16px !important; text-transform:none !important; font-size:13px !important; flex-shrink:0; }
.btn-stop-sm[disabled] { opacity:.35 !important; }
.btn-quick { width:100% !important; background:#1e293b !important; border:1px solid #2d3748 !important; color:#94a3b8 !important; border-radius:9px !important; text-transform:none !important; font-size:13px !important; padding:10px 14px !important; transition:all .15s !important; }
.btn-quick:hover { background:#243044 !important; color:#EA1D2C !important; border-color:rgba(234,29,44,.35) !important; }
.log-area { background:#080e1a; border-radius:10px; padding:14px; overflow-y:auto; }
.log-line { display:flex; align-items:flex-start; gap:8px; padding:2px 0; line-height:1.6; }
.log-ts   { color:#22c55e; flex-shrink:0; font-size:12px; }
.log-msg  { font-size:12px; word-break:break-word; font-family:'Courier New',monospace; }
.info-row { display:flex; justify-content:space-between; align-items:center; padding:7px 0; border-bottom:1px solid #1a2540; }
.info-row:last-child { border-bottom:none; }
.cfg-lbl  { font-size:13px; color:#94a3b8; }
.cfg-val  { font-size:13px; font-weight:700; color:#EA1D2C; }
.badge-img { display:inline-flex; align-items:center; gap:6px; background:rgba(234,29,44,.1); border:1px solid rgba(234,29,44,.3); border-radius:8px; padding:6px 12px; font-size:12px; color:#EA1D2C; font-weight:600; }
.badge-img.ok  { background:rgba(34,197,94,.08); border-color:rgba(34,197,94,.3); color:#22c55e; }
.badge-img.err { background:rgba(239,68,68,.08); border-color:rgba(239,68,68,.3); color:#ef4444; }
</style>
""")

    dark = ui.dark_mode(); dark.enable()

    # ── HEADER ──────────────────────────────────────────────────────────────
    with ui.header(elevated=False).style(
        'background:#0d1526; border-bottom:1px solid #1a2540; padding:0 20px; height:52px; z-index:300;'
    ):
        with ui.row().classes('items-center justify-between w-full h-full'):
            with ui.row().classes('items-center gap-2'):
                ui.icon('inventory_2', size='sm').style('color:#EA1D2C;')
                ui.html('<span style="font-size:17px;font-weight:800;color:#EA1D2C;">iFood</span>'
                        '<span style="font-size:17px;font-weight:300;color:#f1f5f9;margin-left:4px;">Estoque</span>')
                ui.html('<span style="background:rgba(234,29,44,.15);border:1px solid rgba(234,29,44,.4);border-radius:5px;padding:2px 8px;font-size:11px;font-weight:700;color:#EA1D2C;">v1.0</span>')
            with ui.row().classes('items-center gap-3'):
                ui.icon('light_mode',size='xs').style('color:#6b7280;')
                ui.switch('',value=True,on_change=lambda e: dark.enable() if e.value else dark.disable()).props('color=red dense')
                ui.icon('dark_mode',size='xs').style('color:#6b7280;')

    # ── SIDEBAR ─────────────────────────────────────────────────────────────
    with ui.left_drawer(value=True, bordered=False).style(
        'width:260px; background:#0d1526; border-right:1px solid #1a2540; padding:14px 10px;'
    ):
        with ui.element('div').classes('dash-item active'):
            ui.icon('home',size='xs').style('color:inherit;'); ui.label('Dashboard').style('color:inherit;')
        ui.element('div').style('height:10px;')

        ui.label('CONFIGURAÇÕES').classes('sec-lbl')
        with ui.element('div').classes('nav-item'):
            ui.icon('speed',size='xs').style('color:inherit;'); ui.label('Velocidade').style('color:inherit;font-size:13px;')
        with ui.element('div').classes('nav-item'):
            ui.icon('tune',size='xs').style('color:inherit;'); ui.label('Preferências').style('color:inherit;font-size:13px;')
        ui.element('div').style('height:10px;')

        ui.label('COMANDOS').classes('sec-lbl')
        with ui.element('div').classes('nav-item active').on('click', lambda: _iniciar()):
            ui.icon('play_arrow',size='xs').style('color:inherit;'); ui.label('Executar').style('color:inherit;font-size:13px;')

        with ui.element('div').style('position:absolute;bottom:16px;left:10px;right:10px;background:#131c2e;border:1px solid #1e2d45;border-radius:12px;padding:14px;'):
            with ui.row().classes('items-center justify-between'):
                status_sidebar_lbl = ui.label('Pronto').style('font-size:13px;font-weight:600;color:#f1f5f9;')
                ui.element('div').style('width:8px;height:8px;border-radius:50%;background:#22c55e;box-shadow:0 0 8px #22c55e;flex-shrink:0;')
            ui.label('📦 Estoque sempre em dia.').style('font-size:11px;color:#6b7280;margin-top:4px;display:block;')

    # ── PAGE CONTENT ─────────────────────────────────────────────────────────
    with ui.element('div').style('padding:20px; width:100%; min-height:calc(100vh - 52px);'):

        # Title row
        with ui.element('div').style('display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;'):
            with ui.row().classes('items-center gap-3'):
                with ui.element('div').style('width:48px;height:48px;border-radius:12px;background:#1e293b;display:flex;align-items:center;justify-content:center;border:1px solid #2d3748;flex-shrink:0;'):
                    ui.icon('inventory_2').style('color:#EA1D2C;font-size:22px;')
                with ui.element('div'):
                    ui.label('Automação de Estoque').style('font-size:24px;font-weight:700;color:#f1f5f9;display:block;')
                    ui.label('Preenche automaticamente todos os campos de Estoque no iFood').style('font-size:13px;color:#64748b;display:block;margin-top:2px;')
            with ui.element('div').style('display:flex;align-items:center;gap:6px;background:rgba(34,197,94,.08);border:1px solid rgba(34,197,94,.25);border-radius:20px;padding:6px 14px;flex-shrink:0;'):
                ui.element('div').style('width:7px;height:7px;border-radius:50%;background:#22c55e;')
                ui.label('Servidor conectado').style('font-size:12px;color:#22c55e;font-weight:500;')

        with ui.element('div').style('display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:20px;width:100%;align-items:start;'):

            # ── CENTER ──────────────────────────────────────────────────────
            with ui.element('div').style('display:flex;flex-direction:column;gap:14px;'):

                # STATUS CARD
                with ui.element('div').classes('card'):
                    with ui.element('div').style('display:flex;align-items:center;gap:16px;margin-bottom:16px;'):
                        spinner = ui.element('div').classes('spinner-ring').props('id=status-spinner')
                        with ui.element('div').style('flex:1;min-width:0;'):
                            ui.label('Status Atual').style('font-size:11px;color:#6b7280;font-weight:600;letter-spacing:.06em;text-transform:uppercase;display:block;margin-bottom:4px;')
                            status_txt = ui.label('Aguardando comando...').style('font-size:20px;font-weight:700;color:#EA1D2C;display:block;')
                        btn_par_status = ui.button(on_click=lambda: _parar()).classes('btn-stop-sm')
                        with btn_par_status:
                            ui.icon('stop',size='xs'); ui.label('Parar').style('font-size:13px;font-weight:700;')
                        btn_par_status.disable()

                    with ui.element('div').style('display:flex;gap:10px;'):
                        def _stat(icon_nm, lbl_txt, ref_key, init):
                            with ui.element('div').classes('stat-box'):
                                with ui.element('div').classes('stat-icon'):
                                    ui.icon(icon_nm,size='xs').style('color:#64748b;')
                                with ui.element('div').style('flex:1;min-width:0;'):
                                    ui.label(lbl_txt).style('font-size:10px;color:#6b7280;font-weight:700;letter-spacing:.06em;text-transform:uppercase;display:block;')
                                    lbl = ui.label(init).style('font-size:18px;font-weight:800;color:#f1f5f9;display:block;')
                                    ui_refs[ref_key] = lbl
                        _stat('timer',       'Tempo',      'tempo_lbl', '00:00:00')
                        _stat('inventory_2', 'Preenchidos','itens_lbl', '0')
                        _stat('keyboard_arrow_down', 'Scrolls', 'scroll_lbl', '0')
                        _stat('speed',       'Velocidade', 'vel_lbl',   f'{state["delay_item"]}s')

                # CONTROLES
                with ui.element('div').classes('card'):
                    with ui.row().classes('items-center gap-2').style('margin-bottom:14px;'):
                        ui.icon('tune').style('color:#EA1D2C;font-size:18px;')
                        ui.label('Controles de Execução').style('font-size:14px;font-weight:700;color:#f1f5f9;')
                    with ui.element('div').style('display:flex;gap:10px;'):
                        btn_ini = ui.button(on_click=lambda: _iniciar()).classes('btn-ini')
                        with btn_ini: ui.icon('play_arrow',size='sm'); ui.label('Iniciar')
                        _btn_ini_global['el'] = btn_ini
                        btn_pau = ui.button(on_click=lambda: _pausar_retomar()).classes('btn-ctrl')
                        with btn_pau: ui.icon('pause',size='sm'); ui.label('Pausar')
                        btn_pau.disable(); _btn_pau_global['el'] = btn_pau
                        btn_par = ui.button(on_click=lambda: _parar()).classes('btn-ctrl')
                        with btn_par: ui.icon('stop',size='sm'); ui.label('Parar')
                        btn_par.disable(); _btn_par_global['el'] = btn_par
                        with ui.button(on_click=lambda: _limpar_log()).classes('btn-ctrl'):
                            ui.icon('delete_sweep',size='sm'); ui.label('Limpar Log')

                # LOG
                with ui.element('div').classes('card'):
                    with ui.element('div').style('display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;'):
                        with ui.row().classes('items-center gap-2'):
                            ui.icon('terminal').style('color:#EA1D2C;font-size:18px;')
                            ui.label('Log de Execução').style('font-size:14px;font-weight:700;color:#f1f5f9;')
                        with ui.button(on_click=lambda: _limpar_log()).props('flat dense').style('color:#6b7280;padding:4px;'):
                            ui.icon('delete',size='xs')
                    log_scroll = ui.scroll_area().classes('log-area').style('height:calc(100vh - 520px);min-height:300px;')
                    with log_scroll:
                        log_container = ui.column().classes('w-full gap-0')
                    log_ref['container'] = log_container
                    log_ref['scroll']    = log_scroll
                    _push('info', 'iFood Estoque — Pronto para iniciar')

            # ── RIGHT PANEL ─────────────────────────────────────────────────
            with ui.element('div').style('display:flex;flex-direction:column;gap:14px;'):

                # CONFIGURAÇÕES
                with ui.element('div').classes('card'):
                    with ui.row().classes('items-center gap-2').style('margin-bottom:14px;'):
                        ui.icon('settings').style('color:#EA1D2C;font-size:18px;')
                        ui.label('Configurações').style('font-size:14px;font-weight:700;color:#f1f5f9;')

                    # Valor do estoque
                    with ui.element('div').style('margin-bottom:14px;'):
                        ui.label('Valor do Estoque').style('font-size:12px;color:#6b7280;font-weight:700;letter-spacing:.06em;text-transform:uppercase;display:block;margin-bottom:8px;')
                        valor_inp = ui.input(value=state['valor_estoque']).props('outlined dense').style(
                            'width:100%;font-size:20px;font-weight:800;color:#EA1D2C;font-family:monospace;'
                        )
                        def on_valor(e):
                            v = ''.join(c for c in (e.value or '') if c.isdigit())
                            state['valor_estoque'] = v or '99999'
                            _salvar_config()
                        valor_inp.on('blur', on_valor)
                        ui.label('Apenas números. Padrão: 99999').style('font-size:11px;color:#4b5563;display:block;margin-top:4px;')

                    ui.separator().style('opacity:.15;margin:10px 0;')

                    # Delay entre itens
                    with ui.element('div').style('margin-bottom:14px;'):
                        with ui.element('div').style('display:flex;justify-content:space-between;margin-bottom:6px;'):
                            ui.label('Delay entre preenchimentos').classes('cfg-lbl')
                            delay_val = ui.label(f'{state["delay_item"]:.1f}s').classes('cfg-val')
                        def on_delay(e):
                            state['delay_item'] = e.value
                            delay_val.set_text(f'{e.value:.1f}s')
                            ui_refs['vel_lbl'].set_text(f'{e.value:.1f}s')
                            _salvar_config()
                        ui.slider(min=0.5, max=10, step=0.5, value=state['delay_item'], on_change=on_delay).props('color=red').classes('w-full')
                        ui.label('Aumente se aparecer erro de rate limit').style('font-size:11px;color:#4b5563;display:block;margin-top:2px;')

                    # Delay ao detectar erro
                    with ui.element('div').style('margin-bottom:14px;'):
                        with ui.element('div').style('display:flex;justify-content:space-between;margin-bottom:6px;'):
                            ui.label('Pausa ao detectar erro').classes('cfg-lbl')
                            erro_val = ui.label(f'{state["delay_erro"]:.0f}s').classes('cfg-val')
                        def on_erro(e):
                            state['delay_erro'] = e.value
                            erro_val.set_text(f'{e.value:.0f}s')
                            _salvar_config()
                        ui.slider(min=5, max=120, step=5, value=state['delay_erro'], on_change=on_erro).props('color=red').classes('w-full')

                    # Delay retry (campo com erro)
                    with ui.element('div').style('margin-bottom:14px;'):
                        with ui.element('div').style('display:flex;justify-content:space-between;margin-bottom:6px;'):
                            ui.label('Pausa antes de retentar campo').classes('cfg-lbl')
                            retry_val = ui.label(f'{state["delay_retry"]:.1f}s').classes('cfg-val')
                        def on_retry(e):
                            state['delay_retry'] = e.value
                            retry_val.set_text(f'{e.value:.1f}s')
                            _salvar_config()
                        ui.slider(min=1, max=15, step=0.5, value=state['delay_retry'], on_change=on_retry).props('color=red').classes('w-full')
                        ui.label('Aguarda este tempo antes de retentar um campo que falhou').style('font-size:11px;color:#4b5563;display:block;margin-top:2px;')

                    # Max retries por campo
                    with ui.element('div').style('margin-bottom:14px;'):
                        with ui.element('div').style('display:flex;justify-content:space-between;margin-bottom:6px;'):
                            ui.label('Tentativas por campo').classes('cfg-lbl')
                            maxret_val = ui.label(str(state['max_retries'])).classes('cfg-val')
                        def on_maxret(e):
                            state['max_retries'] = int(e.value)
                            maxret_val.set_text(str(int(e.value)))
                            _salvar_config()
                        ui.slider(min=1, max=5, step=1, value=state['max_retries'], on_change=on_maxret).props('color=red').classes('w-full')
                        ui.label('Se exceder, pula o campo e continua').style('font-size:11px;color:#4b5563;display:block;margin-top:2px;')

                    # Max scrolls
                    with ui.element('div'):
                        with ui.element('div').style('display:flex;justify-content:space-between;margin-bottom:6px;'):
                            ui.label('Scrolls sem resultado (encerra)').classes('cfg-lbl')
                            scroll_val = ui.label(str(state['max_scrolls_vazio'])).classes('cfg-val')
                        def on_scroll(e):
                            state['max_scrolls_vazio'] = int(e.value)
                            scroll_val.set_text(str(int(e.value)))
                            _salvar_config()
                        ui.slider(min=1, max=10, step=1, value=state['max_scrolls_vazio'], on_change=on_scroll).props('color=red').classes('w-full')

                # IMAGENS
                with ui.element('div').classes('card'):
                    with ui.row().classes('items-center gap-2').style('margin-bottom:12px;'):
                        ui.icon('image_search').style('color:#EA1D2C;font-size:18px;')
                        ui.label('Imagens de Referência').style('font-size:14px;font-weight:700;color:#f1f5f9;')

                    img_status_refs = {}

                    def _check_img(nome, descricao):
                        path = os.path.join(IMG_PATH, nome)
                        existe = os.path.exists(path)
                        with ui.element('div').style('display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-bottom:1px solid #1a2540;'):
                            with ui.element('div'):
                                ui.label(nome).style('font-size:12px;font-weight:700;color:#f1f5f9;display:block;')
                                ui.label(descricao).style('font-size:11px;color:#64748b;display:block;')
                            badge = ui.element('div').classes(f'badge-img {"ok" if existe else "err"}')
                            with badge:
                                ui.icon('check_circle' if existe else 'error', size='xs')
                                ui.label('OK' if existe else 'Faltando')
                            img_status_refs[nome] = badge

                    _check_img('estoque_input.png', 'Campo de estoque (obrigatório)')
                    _check_img('erro_estoque.png', '"Falha ao atualizar estoque!" (recomendado)')
                    _check_img('erro_vermelho.png', 'Rate limit vermelho (opcional)')

                    with ui.element('div').style('margin-top:10px;'):
                        ui.label('Salve prints em ifood/img/').style('font-size:11px;color:#4b5563;display:block;')

                    def _verificar_imagens():
                        for nome, badge in img_status_refs.items():
                            existe = os.path.exists(os.path.join(IMG_PATH, nome))
                            badge.classes(remove='ok err', add='ok' if existe else 'err')
                            badge.clear()
                            with badge:
                                ui.icon('check_circle' if existe else 'error', size='xs')
                                ui.label('OK' if existe else 'Faltando')
                        ui.notify('Imagens verificadas!', type='positive', position='top-right', timeout=3000)

                    with ui.button(on_click=_verificar_imagens).classes('btn-quick').style('margin-top:10px;'):
                        with ui.row().classes('items-center gap-2 w-full justify-center'):
                            ui.icon('refresh', size='xs'); ui.label('Verificar Imagens')

                # INSTRUÇÕES
                with ui.element('div').classes('card'):
                    with ui.row().classes('items-center gap-2').style('margin-bottom:10px;'):
                        ui.icon('help_outline').style('color:#EA1D2C;font-size:18px;')
                        ui.label('Como usar').style('font-size:14px;font-weight:700;color:#f1f5f9;')
                    for txt in [
                        '1. Abra o iFood Portal do Parceiro',
                        '2. Vá em Cardápio → lista de produtos',
                        '3. Print do campo Estoque → ifood/img/estoque_input.png',
                        '4. Print do "Falha ao atualizar estoque!" → ifood/img/erro_estoque.png',
                        '5. Configure delay e tentativas no painel',
                        '6. Clique Iniciar — preenche, detecta erro e retenta automaticamente',
                    ]:
                        ui.label(txt).style('font-size:12px;color:#94a3b8;display:block;padding:3px 0;line-height:1.6;')

    # ── FOOTER ──────────────────────────────────────────────────────────────
    with ui.element('div').style('background:#0d1526;border-top:1px solid #1a2540;padding:10px 24px;display:flex;justify-content:space-between;align-items:center;'):
        ui.label('© 2025 iFood Automation. Todos os direitos reservados.').style('font-size:12px;color:#4b5563;')
        ui.html('<span style="font-size:12px;color:#4b5563;">Feito com <span style="color:#ef4444;">♥</span> para facilitar seu dia.</span>')

    # ── AUXILIARES ──────────────────────────────────────────────────────────
    prev_fase     = {'v': 'parado'}
    scroll_count  = {'v': 0}

    def _sync_ui():
        while not log_queue.empty():
            try:
                tipo, msg, ts = log_queue.get_nowait()
                icon_nm, color = LOG_ICONS.get(tipo, LOG_ICONS['info'])
                with log_ref['container']:
                    if tipo == 'separador':
                        ui.separator().style('opacity:.2;margin:4px 0;')
                    else:
                        tc = '#cbd5e1' if tipo not in ('erro','aviso','parada','pausa') else color
                        with ui.element('div').classes('log-line'):
                            ui.label(f'[{ts}]').classes('log-ts')
                            ui.icon(icon_nm, size='xs').style(f'color:{color};flex-shrink:0;margin-top:3px;')
                            ui.label(msg).classes('log-msg').style(f'color:{tc};')
                        if tipo == 'scroll':
                            scroll_count['v'] += 1
                            ui_refs['scroll_lbl'].set_text(str(scroll_count['v']))
                log_ref['scroll'].scroll_to(percent=1.0)
            except Exception:
                pass

        while not notif_queue.empty():
            try:
                tipo_n, total = notif_queue.get_nowait()
                ui.notify(f'✅ Concluído! {total} campos preenchidos.', type='positive', position='top', timeout=8000)
            except Exception:
                pass

        if state['inicio_tempo'] is not None:
            pe = (time.time()-state['pausa_inicio']) if state['fase']=='pausado' and state['pausa_inicio'] else 0.0
            elapsed = max(0.0, time.time()-state['inicio_tempo']-state['tempo_pausado']-pe)
            h,r=divmod(int(elapsed),3600); m,s=divmod(r,60)
            ui_refs['tempo_lbl'].set_text(f'{h:02d}:{m:02d}:{s:02d}')
            ui_refs['itens_lbl'].set_text(str(state['itens_ok']))

        fase = state['fase']
        if fase != prev_fase['v']:
            prev_fase['v'] = fase
            if fase == 'rodando':
                status_txt.set_text('Preenchendo estoques...')
                status_txt.style('font-size:20px;font-weight:700;color:#EA1D2C;display:block;')
                status_sidebar_lbl.set_text('Em execução')
                ui.run_javascript("var s=document.getElementById('status-spinner');if(s){s.classList.remove('paused','stopped');s.classList.add('spinning');}")
                btn_par_status.enable()
                _btn_ini_global['el'].disable(); _btn_ini_global['el'].classes(add='running')
                _btn_ini_global['el'].clear()
                with _btn_ini_global['el']: ui.icon('pending',size='sm'); ui.label('Rodando...')
                _btn_pau_global['el'].enable(); _btn_par_global['el'].enable()
            elif fase == 'pausado':
                status_txt.set_text('Pausado — aguardando retomada...')
                status_txt.style('font-size:20px;font-weight:700;color:#b91c1c;display:block;')
                ui.run_javascript("var s=document.getElementById('status-spinner');if(s){s.classList.remove('spinning','stopped');s.classList.add('paused');}")
            elif fase == 'parando':
                status_txt.set_text('Encerrando...')
                status_txt.style('font-size:20px;font-weight:700;color:#ef4444;display:block;')
                ui.run_javascript("var s=document.getElementById('status-spinner');if(s){s.classList.remove('spinning','paused');s.classList.add('stopped');}")
            else:
                status_txt.set_text('Aguardando comando...')
                status_txt.style('font-size:20px;font-weight:700;color:#EA1D2C;display:block;')
                status_sidebar_lbl.set_text('Pronto')
                ui.run_javascript("var s=document.getElementById('status-spinner');if(s)s.className='spinner-ring';")
                btn_par_status.disable()
                _btn_ini_global['el'].enable(); _btn_ini_global['el'].classes(remove='running')
                _btn_ini_global['el'].clear()
                with _btn_ini_global['el']: ui.icon('play_arrow',size='sm'); ui.label('Iniciar')
                _btn_pau_global['el'].disable(); _btn_pau_global['el'].classes(remove='btn-resume',add='btn-ctrl')
                _btn_pau_global['el'].clear()
                with _btn_pau_global['el']: ui.icon('pause',size='sm'); ui.label('Pausar')
                _btn_par_global['el'].disable()

    ui.timer(0.3, _sync_ui)

    # ── CONTROLES ───────────────────────────────────────────────────────────
    def _iniciar():
        if state['fase'] != 'parado': return
        stop_event.clear(); pause_event.set()
        scroll_count['v'] = 0
        state.update({
            'fase': 'rodando', 'inicio_tempo': time.time(),
            'tempo_pausado': 0.0, 'pausa_inicio': None, 'itens_ok': 0
        })
        ui_refs['tempo_lbl'].set_text('00:00:00')
        ui_refs['itens_lbl'].set_text('0')
        ui_refs['scroll_lbl'].set_text('0')
        threading.Thread(target=_thread_automacao, daemon=True).start()

    def _pausar_retomar():
        if state['fase'] == 'rodando':
            pause_event.clear(); state['fase'] = 'pausado'; state['pausa_inicio'] = time.time()
            btn_pau.classes(remove='btn-ctrl', add='btn-resume'); btn_pau.clear()
            with btn_pau: ui.icon('play_arrow',size='sm'); ui.label('Retomar')
        elif state['fase'] == 'pausado':
            if state['pausa_inicio']:
                state['tempo_pausado'] += time.time()-state['pausa_inicio']
                state['pausa_inicio'] = None
            pause_event.set(); state['fase'] = 'rodando'
            btn_pau.classes(remove='btn-resume', add='btn-ctrl'); btn_pau.clear()
            with btn_pau: ui.icon('pause',size='sm'); ui.label('Pausar')

    def _parar():
        if state['fase'] not in ('rodando', 'pausado'): return
        state['fase'] = 'parando'; pause_event.set(); stop_event.set()
        btn_pau.disable(); btn_par.disable(); btn_par_status.disable()
        btn_pau.classes(remove='btn-resume', add='btn-ctrl'); btn_pau.clear()
        with btn_pau: ui.icon('pause',size='sm'); ui.label('Pausar')
        _push('parada', 'Encerrando após o campo atual...')

    def _limpar_log():
        log_ref['container'].clear()
        scroll_count['v'] = 0
        ui_refs['scroll_lbl'].set_text('0')

    ui.run(title='iFood Estoque', port=8086, reload=False, favicon='📦')


if __name__ in {"__main__", "__mp_main__"}:
    iniciar_painel()
