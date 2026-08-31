"""
Painel Alt Preço 99Food - NiceGUI
Duplica item, ajusta nome e preço, exclui original. Para em GABARITO.
"""

import os, sys, time, threading, queue as queue_module, json

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.append(root_path)

CONFIG_PATH = os.path.join(root_path, 'config')
IMG_PATH    = os.path.join(root_path, 'img')

from nicegui import ui

# ── Estado ────────────────────────────────────────────────────────────────
state = {
    'fase':          'parado',
    'preco':         '0.00',
    'delay_dup':     2.0,
    'delay_env':     2.0,
    'delay_exc':     1.0,
    'delay_pos_exc': 1.0,
    'campo_nome':    (0, 0),
    'btn_enviar':    (0, 0),
    'clique_fora':   (0, 0),
    'btn_confirmar': (0, 0),
    'inicio_tempo':  None,
    'tempo_pausado': 0.0,
    'pausa_inicio':  None,
    'itens_ok':      0,
}

COORD_KEYS = [
    ('campo_nome',    'Campo Nome'),
    ('btn_enviar',    'Botão Enviar'),
    ('clique_fora',   'Clique Fora (após enviar)'),
    ('btn_confirmar', 'Confirmar Exclusão'),
]

def _carregar_coordenadas():
    try:
        with open(os.path.join(CONFIG_PATH, 'coordenadas_alt_preco.json'), 'r', encoding='utf-8') as f:
            c = json.load(f)
        for key, _ in COORD_KEYS:
            if key in c:
                state[key] = tuple(c[key])
    except Exception:
        pass

def _salvar_coordenadas():
    try:
        os.makedirs(CONFIG_PATH, exist_ok=True)
        data = {k: list(state[k]) for k, _ in COORD_KEYS}
        with open(os.path.join(CONFIG_PATH, 'coordenadas_alt_preco.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

_carregar_coordenadas()

stop_event  = threading.Event()
pause_event = threading.Event()
pause_event.set()

log_queue   = queue_module.Queue()
coord_queue = queue_module.Queue()
notif_queue = queue_module.Queue()

LOG_ICONS = {
    'inicio':    ('rocket_launch', '#EAB308'),
    'item':      ('play_arrow',    '#EAB308'),
    'sucesso':   ('check_circle',  '#22c55e'),
    'erro':      ('cancel',        '#ef4444'),
    'aviso':     ('warning',       '#f97316'),
    'parada':    ('block',         '#ef4444'),
    'pausa':     ('pause_circle',  '#EAB308'),
    'retomada':  ('play_circle',   '#22c55e'),
    'resumo':    ('bar_chart',     '#EAB308'),
    'info':      ('info',          '#94a3b8'),
    'separador': ('remove',        '#1e293b'),
}

log_ref      = {'container': None, 'scroll': None}
coord_labels = {}
coord_btns   = {}
ui_refs      = {}

def _push(tipo, mensagem=''):
    ts = time.strftime('%H:%M:%S')
    log_queue.put((tipo, mensagem, ts))

def _aguardar_se_pausado():
    while not pause_event.is_set():
        if stop_event.is_set(): return False
        time.sleep(0.1)
    return True

def _sleep_cancelavel(segundos):
    fim = time.time() + segundos
    while time.time() < fim:
        if stop_event.is_set(): return False
        if not pause_event.is_set():
            tr = fim - time.time()
            if not _aguardar_se_pausado(): return False
            fim = time.time() + tr
        time.sleep(0.1)
    return True

# ── Helpers de imagem ─────────────────────────────────────────────────────
def _clicar_imagem(pyautogui, img_path, descricao, confidence=0.8, scroll=0):
    """Localiza imagem na tela e clica. Retorna True se clicou, False se não achou."""
    try:
        loc = pyautogui.locateOnScreen(img_path, confidence=confidence)
        if loc:
            cx, cy = pyautogui.center(loc)
            pyautogui.click(cx, cy)
            return True
    except Exception as e:
        _push('aviso', f'locateOnScreen ({descricao}): {e}')
    if scroll != 0:
        pyautogui.scroll(scroll)
        time.sleep(0.5)
        try:
            loc = pyautogui.locateOnScreen(img_path, confidence=confidence)
            if loc:
                cx, cy = pyautogui.center(loc)
                pyautogui.click(cx, cy)
                return True
        except Exception:
            pass
    _push('erro', f'Imagem não encontrada: {descricao}')
    return False

# ── Thread de automação ────────────────────────────────────────────────────
def _thread_automacao():
    try:
        import pyautogui, pyperclip
        pyautogui.PAUSE = 0.25
        pyautogui.FAILSAFE = False

        img_menu     = os.path.join(IMG_PATH, 'menu.png')
        img_duplicar = os.path.join(IMG_PATH, 'duplicar.png')
        img_excluir  = os.path.join(IMG_PATH, 'excluir.png')

        _push('separador')
        _push('inicio', f'Iniciando — preço: R$ {state["preco"]}')
        time.sleep(1)

        processados = 0
        while True:

            # -- [PAUSA/PARADA] --------------------------------------------
            if stop_event.is_set():
                _push('parada', 'Automação interrompida.'); break
            if not pause_event.is_set():
                _push('pausa', 'Pausado...')
                if not _aguardar_se_pausado():
                    _push('parada', 'Parado durante pausa.'); break
                _push('retomada', 'Retomando...')

            # -- [MENU] Abre menu do item via imagem -----------------------
            _push('info', 'Abrindo menu...')
            if not _clicar_imagem(pyautogui, img_menu, 'menu'): break
            time.sleep(0.5)

            # -- [DUPLICAR] Clica em duplicar via imagem -------------------
            _push('info', 'Duplicando item...')
            if not _clicar_imagem(pyautogui, img_duplicar, 'duplicar'): break
            if not _sleep_cancelavel(state['delay_dup']):
                _push('parada', 'Parado no delay.'); break

            # -- [NOME] Clica no campo, copia, limpa " Copiar", cola -------
            pyperclip.copy('')
            pyautogui.click(*state['campo_nome'], duration=0.1)
            time.sleep(0.3)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.3)
            nome_raw = pyperclip.paste()
            nome = nome_raw.replace(' Copiar', '').replace(' copiar', '').strip()
            _push('item', f'Item: {nome}')

            # -- [GABARITO] Para se chegou ao item marcador ----------------
            if 'GABARITO' in nome.upper():
                _push('aviso', 'GABARITO encontrado — encerrando automação.')
                notif_queue.put(('gabarito', processados))
                break

            # -- [COLAR NOME] Cola nome limpo ------------------------------
            pyperclip.copy(nome)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.3)

            # -- [PREÇO] 9 tabs → seleciona tudo → digita preço -----------
            for _ in range(9): pyautogui.press('tab'); time.sleep(0.1)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('ctrl', 'a')
            pyperclip.copy(state['preco'])
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            pyautogui.press('tab'); time.sleep(0.1)
            pyautogui.write('30')
            pyautogui.press('enter'); time.sleep(0.1)
            time.sleep(0.5)

            # -- [ENVIAR] Clica enviar e aguarda ---------------------------
            _push('info', 'Enviando...')
            pyautogui.click(*state['btn_enviar'], duration=0.1)
            if not _sleep_cancelavel(state['delay_env']):
                _push('parada', 'Parado no delay.'); break

            # -- [MENU PRÉ-FORA] Abre menu para forçar carregamento -------
            _push('info', 'Abrindo menu para carregar...')
            if not _clicar_imagem(pyautogui, img_menu, 'menu (pré-fora)'): break
            time.sleep(0.5)

            # -- [CLIQUE FORA] Clica fora para fechar menu e carregar -----
            _push('info', 'Clicando fora para carregar...')
            pyautogui.click(*state['clique_fora'], duration=0.1)
            time.sleep(0.5)

            # -- [MENU EXCLUIR] Abre menu novamente para excluir ----------
            _push('info', 'Abrindo menu para excluir...')
            if not _clicar_imagem(pyautogui, img_menu, 'menu (excluir)'): break
            time.sleep(0.5)

            # -- [EXCLUIR] Clica excluir via imagem ------------------------
            _push('info', 'Excluindo original...')
            if not _clicar_imagem(pyautogui, img_excluir, 'excluir'): break
            time.sleep(0.5)

            # -- [DELAY EXCLUSÃO] Aguarda modal de confirmação carregar ----
            if not _sleep_cancelavel(state['delay_exc']):
                _push('parada', 'Parado no delay.'); break

            # -- [CONFIRMAR EXCLUSÃO] Confirma o modal de exclusão ---------
            _push('info', 'Confirmando exclusão...')
            pyautogui.click(*state['btn_confirmar'], duration=0.1)

            # -- [DELAY PÓS EXCLUSÃO] Aguarda exclusão processar ----------
            if not _sleep_cancelavel(state['delay_pos_exc']):
                _push('parada', 'Parado no delay.'); break

            processados += 1
            state['itens_ok'] = processados
            _push('sucesso', f'"{nome}" — concluído ({processados} total)')

            if not _sleep_cancelavel(0.5):
                break

        # -- [RESUMO] ------------------------------------------------------
        _push('separador')
        _push('resumo', f'Concluído — {processados} itens processados')
        _push('separador')

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
body { background:#0b1120 !important; }
.q-page { padding:0 !important; }
::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-thumb { background:#2d3748; border-radius:4px; }
.card { background:#131c2e; border:1px solid #1e2d45; border-radius:14px; padding:18px; }
.sec-lbl { font-size:10px; font-weight:800; letter-spacing:.12em; text-transform:uppercase; color:#374151; display:block; padding:0 14px; margin-bottom:4px; margin-top:2px; }
.nav-item { display:flex; align-items:center; gap:10px; padding:9px 14px; border-radius:9px; cursor:pointer; color:#94a3b8; font-size:13px; transition:all .15s; border-left:3px solid transparent; }
.nav-item:hover { background:rgba(255,255,255,.04); color:#cbd5e1; }
.nav-item.active { background:rgba(234,179,8,.1); border-left-color:#EAB308; color:#EAB308; font-weight:700; }
.spinner-ring { width:62px; height:62px; border-radius:50%; border:5px solid rgba(234,179,8,.15); border-top-color:#EAB308; flex-shrink:0; }
@keyframes spin { to { transform:rotate(360deg); } }
.spinner-ring.spinning { animation:spin .8s linear infinite; }
.spinner-ring.paused { border-top-color:#ca8a04; animation:spin 2s linear infinite; }
.spinner-ring.stopped { border-top-color:#ef4444; }
.stat-box { flex:1; min-width:0; background:#0f172a; border:1px solid #1e293b; border-radius:12px; padding:14px; display:flex; align-items:center; gap:10px; }
.stat-icon { width:34px; height:34px; border-radius:9px; background:#1e293b; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.prog-track { background:#1e293b; border-radius:4px; height:5px; width:100%; margin-top:5px; overflow:hidden; }
.prog-fill { background:linear-gradient(90deg,#ca8a04,#EAB308); height:5px; width:0%; transition:width .4s; border-radius:4px; }
@keyframes pulse-glow { 0%,100% { box-shadow:0 4px 14px rgba(234,179,8,.3); } 50% { box-shadow:0 4px 26px rgba(234,179,8,.65); transform:translateY(-1px); } }
.btn-ini { flex:1; min-width:0; background:linear-gradient(135deg,#EAB308,#ca8a04) !important; color:#0f172a !important; font-weight:800 !important; border-radius:10px !important; padding:12px !important; text-transform:none !important; font-size:14px !important; animation:pulse-glow 2s ease-in-out infinite; }
.btn-ini[disabled] { opacity:.4 !important; animation:none !important; }
.btn-ini.running { animation:none !important; background:linear-gradient(135deg,#166534,#15803d) !important; color:#fff !important; }
.btn-ctrl { flex:1; min-width:0; background:#1e293b !important; border:1px solid #2d3748 !important; color:#cbd5e1 !important; font-weight:600 !important; border-radius:10px !important; padding:12px !important; text-transform:none !important; font-size:14px !important; transition:all .2s !important; }
.btn-ctrl[disabled] { opacity:.35 !important; }
.btn-resume { flex:1; min-width:0; background:linear-gradient(135deg,#16a34a,#15803d) !important; color:#fff !important; font-weight:700 !important; border-radius:10px !important; padding:12px !important; text-transform:none !important; font-size:14px !important; }
.btn-stop-sm { background:#ef4444 !important; color:#fff !important; font-weight:700 !important; border-radius:8px !important; padding:8px 16px !important; text-transform:none !important; font-size:13px !important; flex-shrink:0; }
.btn-stop-sm[disabled] { opacity:.35 !important; }
.log-area { background:#080e1a; border-radius:10px; padding:14px; overflow-y:auto; }
.log-line { display:flex; align-items:flex-start; gap:8px; padding:2px 0; line-height:1.6; }
.log-ts { color:#22c55e; flex-shrink:0; font-size:12px; }
.log-msg { font-size:12px; word-break:break-word; font-family:'Courier New',monospace; }
.coord-item { background:#131c2e; border:1px solid #1e2d45; border-radius:12px; padding:14px; margin-bottom:10px; }
.btn-cap-sm { flex:1; background:rgba(234,179,8,.12) !important; border:1px solid rgba(234,179,8,.4) !important; color:#EAB308 !important; border-radius:7px !important; font-size:12px !important; text-transform:none !important; padding:6px 10px !important; font-weight:700 !important; }
.btn-edit-sm { flex:1; background:#1e293b !important; border:1px solid #2d3748 !important; color:#94a3b8 !important; border-radius:7px !important; font-size:12px !important; text-transform:none !important; padding:6px 10px !important; }
</style>
""")

    dark = ui.dark_mode(); dark.enable()

    # ── COORD DRAWER ────────────────────────────────────────────────────────
    coord_drawer = ui.right_drawer(value=False, fixed=True).style(
        'width:300px; background:#0d1526; border-left:1px solid #1a2540;'
    )
    with coord_drawer:
        with ui.element('div').style('padding:20px; display:flex; flex-direction:column; height:100%; overflow-y:auto;'):
            with ui.element('div').style('display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;'):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('my_location').style('color:#EAB308; font-size:20px;')
                    ui.label('Coordenadas').style('font-size:16px; font-weight:800; color:#f1f5f9;')
                ui.button(icon='close', on_click=lambda: coord_drawer.hide()).props('flat round dense').style('color:#6b7280;')
            ui.label('Mova o mouse e clique Capturar. Aguarda 2 segundos.').style('font-size:12px; color:#6b7280; line-height:1.6; display:block; margin-bottom:16px;')
            for key, lbl_txt in COORD_KEYS:
                x, y = state[key]
                with ui.element('div').classes('coord-item'):
                    with ui.element('div').style('display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;'):
                        with ui.element('div'):
                            ui.label(lbl_txt).style('font-size:11px; font-weight:700; color:#6b7280; display:block;')
                            cl = ui.label(f'{x},  {y}').style('font-size:18px; font-weight:800; color:#EAB308; font-family:monospace; display:block;')
                            coord_labels[key] = cl
                        ui.element('div').style('width:8px;height:8px;border-radius:50%;background:#22c55e;margin-top:4px;flex-shrink:0;')
                    with ui.row().classes('gap-2 w-full'):
                        cb = ui.button(on_click=lambda k=key: _capturar_coord(k)).classes('btn-cap-sm')
                        with cb: ui.icon('my_location',size='xs'); ui.label('Capturar')
                        coord_btns[key] = cb
                        eb = ui.button(on_click=lambda k=key: _editar_coord(k)).classes('btn-edit-sm')
                        with eb: ui.icon('edit',size='xs'); ui.label('Editar')
            with ui.element('div').style('margin-top:auto; padding-top:16px; border-top:1px solid #1a2540;'):
                ui.label('Salvo em config/coordenadas_alt_preco.json').style('font-size:11px; color:#4b5563; display:block;')

    # ── HEADER ──────────────────────────────────────────────────────────────
    with ui.header(elevated=False).style(
        'background:#0d1526; border-bottom:1px solid #1a2540; padding:0 20px; height:52px; z-index:300;'
    ):
        with ui.row().classes('items-center justify-between w-full h-full'):
            with ui.row().classes('items-center gap-2'):
                ui.icon('price_change', size='sm').style('color:#EAB308;')
                ui.html('<span style="font-size:17px;font-weight:800;color:#EAB308;">99Food</span>'
                        '<span style="font-size:17px;font-weight:300;color:#f1f5f9;margin-left:4px;">Alt. Preço</span>')
                ui.html('<span style="background:rgba(234,179,8,.15);border:1px solid rgba(234,179,8,.4);border-radius:5px;padding:2px 8px;font-size:11px;font-weight:700;color:#EAB308;">v1.0</span>')
            with ui.row().classes('items-center gap-3'):
                ui.icon('light_mode',size='xs').style('color:#6b7280;')
                ui.switch('',value=True,on_change=lambda e: dark.enable() if e.value else dark.disable()).props('color=yellow dense')
                ui.icon('dark_mode',size='xs').style('color:#6b7280;')

    # ── SIDEBAR ─────────────────────────────────────────────────────────────
    with ui.left_drawer(value=True, bordered=False).style(
        'width:240px; background:#0d1526; border-right:1px solid #1a2540; padding:14px 10px;'
    ):
        with ui.element('div').classes('nav-item active'):
            ui.icon('home',size='xs').style('color:inherit;'); ui.label('Dashboard').style('color:inherit;')
        ui.element('div').style('height:10px;')

        ui.label('CONFIGURAÇÕES').classes('sec-lbl')
        with ui.element('div').classes('nav-item').on('click', lambda: coord_drawer.toggle()):
            ui.icon('my_location',size='xs').style('color:inherit;'); ui.label('Coordenadas').style('color:inherit;font-size:13px;')
        ui.element('div').style('height:10px;')

        ui.label('COMANDOS').classes('sec-lbl')
        with ui.element('div').classes('nav-item active').on('click', lambda: _iniciar()):
            ui.icon('play_arrow',size='xs').style('color:inherit;'); ui.label('Executar').style('color:inherit;font-size:13px;')

        with ui.element('div').style('position:absolute;bottom:16px;left:10px;right:10px;background:#131c2e;border:1px solid #1e2d45;border-radius:12px;padding:14px;'):
            with ui.row().classes('items-center justify-between'):
                status_sidebar_lbl = ui.label('Pronto').style('font-size:13px;font-weight:600;color:#f1f5f9;')
                ui.element('div').style('width:8px;height:8px;border-radius:50%;background:#22c55e;box-shadow:0 0 8px #22c55e;flex-shrink:0;')
            ui.label('Para em GABARITO.').style('font-size:11px;color:#6b7280;margin-top:4px;display:block;')

    # ── PAGE ─────────────────────────────────────────────────────────────────
    with ui.element('div').style('padding:20px; width:100%;'):

        with ui.element('div').style('display:flex;align-items:center;gap:12px;margin-bottom:18px;'):
            with ui.element('div').style('width:48px;height:48px;border-radius:12px;background:#1e293b;display:flex;align-items:center;justify-content:center;border:1px solid #2d3748;flex-shrink:0;'):
                ui.icon('price_change').style('color:#EAB308;font-size:22px;')
            with ui.element('div'):
                ui.label('Alteração de Preço em Lote').style('font-size:22px;font-weight:700;color:#f1f5f9;display:block;')
                ui.label('Duplica, ajusta preço e exclui o original. Para em GABARITO.').style('font-size:13px;color:#64748b;display:block;margin-top:2px;')

        with ui.element('div').style('display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:20px;align-items:start;'):

            # ── CENTER ──────────────────────────────────────────────────
            with ui.element('div').style('display:flex;flex-direction:column;gap:14px;'):

                # STATUS
                with ui.element('div').classes('card'):
                    with ui.element('div').style('display:flex;align-items:center;gap:16px;margin-bottom:16px;'):
                        spinner = ui.element('div').classes('spinner-ring').props('id=status-spinner')
                        with ui.element('div').style('flex:1;min-width:0;'):
                            ui.label('Status Atual').style('font-size:11px;color:#6b7280;font-weight:600;letter-spacing:.06em;text-transform:uppercase;display:block;margin-bottom:4px;')
                            status_txt = ui.label('Aguardando comando...').style('font-size:20px;font-weight:700;color:#EAB308;display:block;')
                        btn_par_status = ui.button(on_click=lambda: _parar()).classes('btn-stop-sm')
                        with btn_par_status: ui.icon('stop',size='xs'); ui.label('Parar').style('font-size:13px;font-weight:700;')
                        btn_par_status.disable()

                    with ui.element('div').style('display:flex;gap:10px;'):
                        for icon_nm, lbl_txt, ref_key, init in [
                            ('timer',      'Tempo',      'tempo_lbl', '00:00:00'),
                            ('grid_view',  'Processados','itens_lbl', '0'),
                            ('show_chart', 'Média',      'media_lbl', '—'),
                        ]:
                            with ui.element('div').classes('stat-box'):
                                with ui.element('div').classes('stat-icon'):
                                    ui.icon(icon_nm,size='xs').style('color:#64748b;')
                                with ui.element('div').style('flex:1;min-width:0;'):
                                    ui.label(lbl_txt).style('font-size:10px;color:#6b7280;font-weight:700;letter-spacing:.06em;text-transform:uppercase;display:block;')
                                    lbl = ui.label(init).style('font-size:18px;font-weight:800;color:#f1f5f9;display:block;')
                                    ui_refs[ref_key] = lbl

                # CONTROLES
                with ui.element('div').classes('card'):
                    with ui.row().classes('items-center gap-2').style('margin-bottom:14px;'):
                        ui.icon('tune').style('color:#EAB308;font-size:18px;')
                        ui.label('Controles').style('font-size:14px;font-weight:700;color:#f1f5f9;')
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
                            ui.icon('terminal').style('color:#EAB308;font-size:18px;')
                            ui.label('Log de Execução').style('font-size:14px;font-weight:700;color:#f1f5f9;')
                        with ui.button(on_click=lambda: _limpar_log()).props('flat dense').style('color:#6b7280;padding:4px;'):
                            ui.icon('delete',size='xs')
                    log_scroll = ui.scroll_area().classes('log-area').style('height:calc(100vh - 500px);min-height:280px;')
                    with log_scroll:
                        log_container = ui.column().classes('w-full gap-0')
                    log_ref['container'] = log_container
                    log_ref['scroll']    = log_scroll
                    _push('info', '99Food Alt. Preço — Pronto para iniciar')

            # ── RIGHT ────────────────────────────────────────────────────
            with ui.element('div').style('display:flex;flex-direction:column;gap:14px;'):

                # PREÇO
                with ui.element('div').classes('card'):
                    with ui.row().classes('items-center gap-2').style('margin-bottom:14px;'):
                        ui.icon('attach_money').style('color:#EAB308;font-size:18px;')
                        ui.label('Preço a Aplicar').style('font-size:14px;font-weight:700;color:#f1f5f9;')
                    preco_display = ui.label('R$ 0,00').style('font-size:32px;font-weight:800;color:#EAB308;display:block;text-align:center;margin-bottom:12px;')
                    def on_preco(e):
                        v = str(e.value or '0')
                        # formata como centavos
                        digits = ''.join(c for c in v if c.isdigit())
                        if not digits: digits = '0'
                        cents = int(digits)
                        reais = cents // 100
                        cent_part = cents % 100
                        state['preco'] = f'{reais}.{cent_part:02d}'
                        preco_display.set_text(f'R$ {reais},{cent_part:02d}')
                    ui.input(placeholder='Digite o preço em centavos (ex: 2990 = R$29,90)', on_change=on_preco).props('outlined dense').classes('w-full').style('font-size:14px;')
                    ui.label('Digite sem vírgula: 2990 = R$ 29,90').style('font-size:11px;color:#6b7280;display:block;margin-top:6px;')

                # DELAYS
                with ui.element('div').classes('card'):
                    with ui.row().classes('items-center gap-2').style('margin-bottom:14px;'):
                        ui.icon('speed').style('color:#EAB308;font-size:18px;')
                        ui.label('Velocidade').style('font-size:14px;font-weight:700;color:#f1f5f9;')

                    with ui.element('div').style('display:flex;justify-content:space-between;margin-bottom:6px;'):
                        ui.label('Delay após duplicar').style('font-size:13px;color:#94a3b8;')
                        dup_val = ui.label('2.0s').style('font-size:13px;font-weight:700;color:#EAB308;')
                    def on_dup(e): state['delay_dup']=e.value; dup_val.set_text(f'{e.value:.1f}s')
                    ui.slider(min=0.5,max=8,step=0.5,value=2.0,on_change=on_dup).props('color=yellow').classes('w-full')

                    ui.element('div').style('height:10px;')

                    with ui.element('div').style('display:flex;justify-content:space-between;margin-bottom:6px;'):
                        ui.label('Delay após enviar').style('font-size:13px;color:#94a3b8;')
                        env_val = ui.label('2.0s').style('font-size:13px;font-weight:700;color:#EAB308;')
                    def on_env(e): state['delay_env']=e.value; env_val.set_text(f'{e.value:.1f}s')
                    ui.slider(min=0.5,max=8,step=0.5,value=2.0,on_change=on_env).props('color=yellow').classes('w-full')

                    ui.element('div').style('height:10px;')

                    with ui.element('div').style('display:flex;justify-content:space-between;margin-bottom:6px;'):
                        ui.label('Delay excluir → confirmar').style('font-size:13px;color:#94a3b8;')
                        exc_val = ui.label('1.0s').style('font-size:13px;font-weight:700;color:#EAB308;')
                    def on_exc(e): state['delay_exc']=e.value; exc_val.set_text(f'{e.value:.1f}s')
                    ui.slider(min=0.5,max=8,step=0.5,value=1.0,on_change=on_exc).props('color=yellow').classes('w-full')

                    ui.element('div').style('height:10px;')

                    with ui.element('div').style('display:flex;justify-content:space-between;margin-bottom:6px;'):
                        ui.label('Delay após confirmar exclusão').style('font-size:13px;color:#94a3b8;')
                        pos_exc_val = ui.label('1.0s').style('font-size:13px;font-weight:700;color:#EAB308;')
                    def on_pos_exc(e): state['delay_pos_exc']=e.value; pos_exc_val.set_text(f'{e.value:.1f}s')
                    ui.slider(min=0.5,max=8,step=0.5,value=1.0,on_change=on_pos_exc).props('color=yellow').classes('w-full')

                # INFO
                with ui.element('div').classes('card'):
                    with ui.row().classes('items-center gap-2').style('margin-bottom:10px;'):
                        ui.icon('info').style('color:#EAB308;font-size:18px;')
                        ui.label('Fluxo').style('font-size:14px;font-weight:700;color:#f1f5f9;')
                    for step in [
                        '1. Abre menu → clica Duplicar',
                        '2. Copia nome, remove " Copiar"',
                        '3. Cola nome limpo',
                        '4. 9 tabs → digita preço',
                        '5. Clica Enviar',
                        '6. Abre menu → clica Excluir',
                        '7. Repete até achar GABARITO',
                    ]:
                        ui.label(step).style('font-size:12px;color:#64748b;display:block;padding:3px 0;')

    # ── AUXILIARES ──────────────────────────────────────────────────────────
    def _capturar_coord(key):
        import pyautogui
        btn = coord_btns.get(key)
        if btn: btn.disable()
        _push('aviso', f'Capturando "{key}" em 2s...')
        def _run():
            for i in range(2, 0, -1):
                _push('info', f'{i}s...'); time.sleep(1.0)
            x, y = pyautogui.position()
            coord_queue.put(('update', key, x, y))
            coord_queue.put(('enable_btn', key))
            _salvar_coordenadas()
            _push('sucesso', f'"{key}" → ({x}, {y})')
        threading.Thread(target=_run, daemon=True).start()

    def _editar_coord(key):
        lbl_txt = next((l for k, l in COORD_KEYS if k==key), key)
        x0, y0 = state[key]
        with ui.dialog() as dlg, ui.card().style('min-width:300px;background:#131c2e;border:1px solid #1e2d45;'):
            with ui.row().classes('items-center gap-2').style('margin-bottom:12px;'):
                ui.icon('edit_location').style('color:#EAB308;')
                ui.label(f'Editar — {lbl_txt}').style('font-weight:700;font-size:15px;')
            inp_x = ui.number('X', value=x0, format='%d').classes('w-full')
            inp_y = ui.number('Y', value=y0, format='%d').classes('w-full')
            with ui.row().classes('gap-2 justify-end').style('margin-top:12px;'):
                ui.button('Cancelar', on_click=dlg.close).props('flat color=grey')
                def salvar():
                    nx, ny = int(inp_x.value or 0), int(inp_y.value or 0)
                    coord_queue.put(('update', key, nx, ny)); _salvar_coordenadas()
                    _push('info', f'"{key}" → ({nx}, {ny})'); dlg.close()
                ui.button('Salvar', on_click=salvar).props('color=yellow')
        dlg.open()

    # ── SYNC ────────────────────────────────────────────────────────────────
    prev_fase = {'v': 'parado'}

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
                            ui.icon(icon_nm,size='xs').style(f'color:{color};flex-shrink:0;margin-top:3px;')
                            ui.label(msg).classes('log-msg').style(f'color:{tc};')
                log_ref['scroll'].scroll_to(percent=1.0)
            except Exception:
                pass

        while not notif_queue.empty():
            try:
                tipo_n, processados = notif_queue.get_nowait()
                if tipo_n == 'gabarito':
                    ui.notify(f'✅ GABARITO encontrado! {processados} itens processados.', type='positive', position='top', timeout=10000)
            except Exception:
                pass

        while not coord_queue.empty():
            try:
                msg = coord_queue.get_nowait()
                if msg[0]=='update':
                    _, key, x, y = msg; state[key]=(x,y)
                    if key in coord_labels: coord_labels[key].set_text(f'{x},  {y}')
                elif msg[0]=='enable_btn':
                    key=msg[1]
                    if key in coord_btns: coord_btns[key].enable()
            except Exception:
                pass

        if state['inicio_tempo'] is not None:
            pe = (time.time()-state['pausa_inicio']) if state['fase']=='pausado' and state['pausa_inicio'] else 0.0
            elapsed = max(0.0, time.time()-state['inicio_tempo']-state['tempo_pausado']-pe)
            h,r=divmod(int(elapsed),3600); m,s=divmod(r,60)
            ui_refs['tempo_lbl'].set_text(f'{h:02d}:{m:02d}:{s:02d}')
            itens = state['itens_ok']
            ui_refs['itens_lbl'].set_text(str(itens))
            if elapsed>=5 and itens>0: ui_refs['media_lbl'].set_text(f'{itens/(elapsed/60):.1f}/min')

        fase = state['fase']
        if fase != prev_fase['v']:
            prev_fase['v'] = fase
            if fase=='rodando':
                status_txt.set_text('Automação em andamento...')
                status_txt.style('font-size:20px;font-weight:700;color:#EAB308;display:block;')
                status_sidebar_lbl.set_text('Em execução')
                ui.run_javascript("var s=document.getElementById('status-spinner');if(s){s.classList.remove('paused','stopped');s.classList.add('spinning');}")
                btn_par_status.enable()
                _btn_ini_global['el'].disable(); _btn_ini_global['el'].classes(add='running')
                _btn_ini_global['el'].clear()
                with _btn_ini_global['el']: ui.icon('pending',size='sm'); ui.label('Rodando...')
                _btn_pau_global['el'].enable(); _btn_par_global['el'].enable()
            elif fase=='pausado':
                status_txt.set_text('Pausado...')
                status_txt.style('font-size:20px;font-weight:700;color:#ca8a04;display:block;')
                ui.run_javascript("var s=document.getElementById('status-spinner');if(s){s.classList.remove('spinning','stopped');s.classList.add('paused');}")
            elif fase=='parando':
                status_txt.set_text('Encerrando...')
                status_txt.style('font-size:20px;font-weight:700;color:#ef4444;display:block;')
                ui.run_javascript("var s=document.getElementById('status-spinner');if(s){s.classList.remove('spinning','paused');s.classList.add('stopped');}")
            else:
                status_txt.set_text('Aguardando comando...')
                status_txt.style('font-size:20px;font-weight:700;color:#EAB308;display:block;')
                status_sidebar_lbl.set_text('Pronto')
                ui.run_javascript("var s=document.getElementById('status-spinner');if(s)s.className='spinner-ring';")
                btn_par_status.disable()
                _btn_ini_global['el'].enable(); _btn_ini_global['el'].classes(remove='running')
                _btn_ini_global['el'].clear()
                with _btn_ini_global['el']: ui.icon('play_arrow',size='sm'); ui.label('Iniciar')
                _btn_pau_global['el'].disable()
                _btn_pau_global['el'].classes(remove='btn-resume',add='btn-ctrl')
                _btn_pau_global['el'].clear()
                with _btn_pau_global['el']: ui.icon('pause',size='sm'); ui.label('Pausar')
                _btn_par_global['el'].disable()

    ui.timer(0.3, _sync_ui)

    # ── CONTROLES ────────────────────────────────────────────────────────────
    def _iniciar():
        if state['fase'] != 'parado': return
        stop_event.clear(); pause_event.set()
        state.update({'fase':'rodando','inicio_tempo':time.time(),'tempo_pausado':0.0,'pausa_inicio':None,'itens_ok':0})
        ui_refs['tempo_lbl'].set_text('00:00:00')
        ui_refs['itens_lbl'].set_text('0')
        ui_refs['media_lbl'].set_text('—')
        threading.Thread(target=_thread_automacao, daemon=True).start()

    def _pausar_retomar():
        if state['fase']=='rodando':
            pause_event.clear(); state['fase']='pausado'; state['pausa_inicio']=time.time()
            btn_pau.classes(remove='btn-ctrl',add='btn-resume'); btn_pau.clear()
            with btn_pau: ui.icon('play_arrow',size='sm'); ui.label('Retomar')
        elif state['fase']=='pausado':
            if state['pausa_inicio']: state['tempo_pausado']+=time.time()-state['pausa_inicio']; state['pausa_inicio']=None
            pause_event.set(); state['fase']='rodando'
            btn_pau.classes(remove='btn-resume',add='btn-ctrl'); btn_pau.clear()
            with btn_pau: ui.icon('pause',size='sm'); ui.label('Pausar')

    def _parar():
        if state['fase'] not in ('rodando','pausado'): return
        state['fase']='parando'; pause_event.set(); stop_event.set()
        btn_pau.disable(); btn_par.disable(); btn_par_status.disable()
        _push('parada','Encerrando após a etapa atual...')

    def _limpar_log():
        log_ref['container'].clear()

    ui.run(title='99Food Alt. Preço', port=8085, reload=False, favicon='')


if __name__ in {"__main__", "__mp_main__"}:
    iniciar_painel()
