"""
Painel de Automação 99Food - NiceGUI  (v3 — full-width + drawer coords + UX polish)
"""

import os, sys, time, threading, queue as queue_module, json

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.append(root_path)

DATA_PATH   = os.path.join(root_path, 'data')
CONFIG_PATH = os.path.join(root_path, 'config')

from nicegui import ui

# ── Estado ────────────────────────────────────────────────────────────────
state = {
    'fase':          'parado',
    'arquivo':       os.path.join(DATA_PATH, 'pizza.txt'),
    'delay_dup':     2.0,
    'delay_env':     3.0,
    'menu_opcoes':   (1764, 655),
    'btn_duplicar':  (1716, 835),
    'campo_nome':    (310,  545),
    'btn_enviar':    (304,  999),
    'inicio_tempo':  None,
    'tempo_pausado': 0.0,
    'pausa_inicio':  None,
    'itens_ok':      0,
    'itens_total':   0,
}

COORD_KEYS = [
    ('menu_opcoes',  'Menu Opções'),
    ('btn_duplicar', 'Botão Duplicar'),
    ('campo_nome',   'Campo Nome'),
    ('btn_enviar',   'Botão Enviar'),
]

def _carregar_coordenadas():
    try:
        with open(os.path.join(CONFIG_PATH, 'coordenadas.json'), 'r', encoding='utf-8') as f:
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
        with open(os.path.join(CONFIG_PATH, 'coordenadas.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

_carregar_coordenadas()

stop_event  = threading.Event()
pause_event = threading.Event()
pause_event.set()

log_queue   = queue_module.Queue()
coord_queue = queue_module.Queue()

LOG_ICONS = {
    'inicio':    ('rocket_launch', '#EAB308'),
    'arquivo':   ('description',   '#94a3b8'),
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

log_ref       = {'container': None, 'scroll': None}
coord_labels  = {}
coord_btns    = {}
file_info_ref = {}
ui_refs       = {}
notif_queue   = queue_module.Queue()

def _push(tipo: str, mensagem: str = ''):
    ts = time.strftime('%H:%M:%S')
    log_queue.put((tipo, mensagem, ts))

def _info_arquivo(path):
    try:
        stat  = os.stat(path)
        size  = f'{stat.st_size / 1024:.1f} KB'
        mtime = time.strftime('%d/%m/%Y %H:%M', time.localtime(stat.st_mtime))
        with open(path, 'r', encoding='utf-8') as f:
            lines = sum(1 for l in f if l.strip())
        return size, mtime, str(lines), True
    except Exception:
        return '—', '—', '—', False

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
        from utils import som
    except Exception:
        som = None
    try:
        import pyautogui, pyperclip
        pyautogui.PAUSE = 0.3
        arquivo = state['arquivo']
        _push('separador')
        _push('inicio', 'Iniciando automação 99Food...')
        if not os.path.exists(arquivo):
            _push('erro', f'Arquivo não encontrado: {arquivo}')
            state['fase'] = 'parado'; stop_event.clear(); pause_event.set(); return
        with open(arquivo, 'r', encoding='utf-8') as f:
            linhas = [l for l in f.readlines() if l.strip()]
        _push('arquivo', f'{len(linhas)} itens em {os.path.basename(arquivo)}')
        _push('separador')
        state['itens_total'] = len(linhas)
        time.sleep(1)
        adicionados = falhados = 0
        for i, linha in enumerate(linhas, 1):
            if stop_event.is_set():
                _push('parada', 'Automação interrompida.'); break
            if not pause_event.is_set():
                _push('pausa', f'Pausado antes do item {i}...')
                if not _aguardar_se_pausado():
                    _push('parada', 'Parado durante pausa.'); break
                _push('retomada', 'Retomando...')
            try:
                partes = linha.strip().split('|')
                if len(partes) != 3:
                    _push('aviso', f'Linha {i} inválida'); falhados += 1; continue
                nome, descricao, preco_txt = partes
                nome      = nome.strip()
                descricao = descricao.strip() + ' Foto Ilustrativa.'
                preco     = float(preco_txt.strip().replace(',', '.'))
                _push('item', f'[{i}/{len(linhas)}] {nome} — R$ {preco:.2f}')
                pyautogui.press('home')
                pyautogui.click(*state['menu_opcoes'], duration=0.1); time.sleep(0.2)
                pyautogui.click(*state['btn_duplicar'], duration=0.1)
                if not _sleep_cancelavel(state['delay_dup']):
                    _push('parada', 'Parado no delay duplicação.'); break
                pyautogui.click(*state['campo_nome'], duration=0.1)
                pyautogui.hotkey('ctrl', 'a'); pyperclip.copy(nome); pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.5)
                for _ in range(2): pyautogui.press('tab'); time.sleep(0.1)
                pyautogui.hotkey('ctrl', 'a'); pyautogui.press('backspace')
                pyperclip.copy(descricao); pyautogui.hotkey('ctrl', 'v'); time.sleep(0.2)
                for _ in range(5): pyautogui.press('tab'); time.sleep(0.1)
                pyautogui.hotkey('ctrl', 'a'); pyautogui.press('backspace')
                pyperclip.copy(f'{preco:.2f}'); pyautogui.hotkey('ctrl', 'v'); time.sleep(0.5)
                pyautogui.moveTo(*state['btn_enviar'], duration=0.1); pyautogui.click()
                if not _sleep_cancelavel(state['delay_env']):
                    _push('parada', 'Parado no delay envio.'); break
                _push('sucesso', f'"{nome}" adicionado')
                adicionados += 1; state['itens_ok'] = adicionados
            except Exception as e:
                _push('erro', f'Erro item {i}: {e}'); falhados += 1
        _push('separador')
        _push('resumo', f'Concluído — {adicionados} adicionados  {falhados} falhados')
        _push('separador')
        # notificação de conclusão
        if not stop_event.is_set():
            notif_queue.put(('sucesso' if falhados == 0 else 'aviso', adicionados, falhados))
        if som:
            if falhados == 0 and adicionados > 0: som.som_sucesso()
            elif falhados > 0: som.som_erro()
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

/* SIDEBAR */
.dash-item {
    display:flex; align-items:center; gap:10px;
    padding:10px 14px; border-radius:9px; cursor:pointer;
    color:#94a3b8; font-size:13px; user-select:none;
    transition:all .15s; border-left:3px solid transparent;
}
.dash-item:hover { background:rgba(255,255,255,.04); color:#cbd5e1; }
.dash-item.active { background:rgba(234,179,8,.1); border-left-color:#EAB308; color:#EAB308; font-weight:700; }

.nav-item {
    display:flex; align-items:center; gap:10px;
    padding:9px 14px; border-radius:9px; cursor:pointer;
    color:#94a3b8; font-size:13px; user-select:none;
    transition:all .15s; border-left:3px solid transparent;
}
.nav-item:hover { background:rgba(255,255,255,.04); color:#cbd5e1; }
.nav-item.active { background:rgba(234,179,8,.1); border-left-color:#EAB308; color:#EAB308; font-weight:700; }

.file-item {
    display:flex; align-items:center; gap:10px;
    padding:9px 12px; border-radius:9px; cursor:pointer;
    color:#64748b; font-size:13px; user-select:none; transition:all .15s;
}
.file-item.selected { background:#EAB308 !important; color:#0f172a !important; font-weight:700; }
.file-item:not(.selected):hover { background:rgba(255,255,255,.04); color:#cbd5e1; }

.sec-lbl {
    font-size:10px; font-weight:800; letter-spacing:.12em; text-transform:uppercase;
    color:#374151; display:block; padding:0 14px; margin-bottom:4px; margin-top:2px;
}

/* SPINNER */
.spinner-ring {
    width:62px; height:62px; border-radius:50%;
    border:5px solid rgba(234,179,8,.15); border-top-color:#EAB308; flex-shrink:0;
}
@keyframes spin { to { transform:rotate(360deg); } }
.spinner-ring.spinning { animation:spin .8s linear infinite; }
.spinner-ring.paused   { border-top-color:#ca8a04; animation:spin 2s linear infinite; }
.spinner-ring.stopped  { border-top-color:#ef4444; }

/* STAT BOXES */
.stat-box {
    flex:1; min-width:0; background:#0f172a; border:1px solid #1e293b;
    border-radius:12px; padding:14px 14px;
    display:flex; align-items:center; gap:10px;
}
.stat-icon {
    width:34px; height:34px; border-radius:9px; background:#1e293b;
    display:flex; align-items:center; justify-content:center; flex-shrink:0;
}

/* PROGRESS */
.prog-track { background:#1e293b; border-radius:4px; height:5px; width:100%; margin-top:5px; overflow:hidden; }
.prog-fill  { background:linear-gradient(90deg,#ca8a04,#EAB308); height:5px; width:0%; transition:width .4s; border-radius:4px; }

/* BUTTONS */
@keyframes pulse-glow {
    0%,100% { box-shadow:0 4px 14px rgba(234,179,8,.3); }
    50%      { box-shadow:0 4px 26px rgba(234,179,8,.65); transform:translateY(-1px); }
}
.btn-ini {
    flex:1; min-width:0;
    background:linear-gradient(135deg,#EAB308,#ca8a04) !important;
    color:#0f172a !important; font-weight:800 !important;
    border-radius:10px !important; padding:12px !important;
    text-transform:none !important; font-size:14px !important;
    animation:pulse-glow 2s ease-in-out infinite; transition:all .2s !important;
}
.btn-ini[disabled]  { opacity:.4 !important; animation:none !important; }
.btn-ini.running    { animation:none !important; background:linear-gradient(135deg,#166534,#15803d) !important; color:#fff !important; }
.btn-ctrl {
    flex:1; min-width:0;
    background:#1e293b !important; border:1px solid #2d3748 !important;
    color:#cbd5e1 !important; font-weight:600 !important;
    border-radius:10px !important; padding:12px !important;
    text-transform:none !important; font-size:14px !important; transition:all .2s !important;
}
.btn-ctrl:hover:not([disabled]) { background:#243044 !important; border-color:#3d4f6a !important; }
.btn-ctrl[disabled] { opacity:.35 !important; }
.btn-resume {
    flex:1; min-width:0;
    background:linear-gradient(135deg,#16a34a,#15803d) !important; color:#fff !important;
    font-weight:700 !important; border-radius:10px !important; padding:12px !important;
    text-transform:none !important; font-size:14px !important;
}
.btn-resume[disabled] { opacity:.35 !important; }
.btn-stop-sm {
    background:#ef4444 !important; color:#fff !important; font-weight:700 !important;
    border-radius:8px !important; padding:8px 16px !important;
    text-transform:none !important; font-size:13px !important; flex-shrink:0;
}
.btn-stop-sm[disabled] { opacity:.35 !important; }
.btn-quick {
    width:100% !important; background:#1e293b !important; border:1px solid #2d3748 !important;
    color:#94a3b8 !important; border-radius:9px !important;
    text-transform:none !important; font-size:13px !important;
    padding:10px 14px !important; transition:all .15s !important;
}
.btn-quick:hover { background:#243044 !important; color:#EAB308 !important; border-color:rgba(234,179,8,.35) !important; }

/* LOG */
.log-area { background:#080e1a; border-radius:10px; padding:14px; overflow-y:auto; }
.log-line { display:flex; align-items:flex-start; gap:8px; padding:2px 0; line-height:1.6; }
.log-ts   { color:#22c55e; flex-shrink:0; font-size:12px; }
.log-msg  { font-size:12px; word-break:break-word; font-family:'Courier New',monospace; }

/* INFO ROW */
.info-row { display:flex; justify-content:space-between; align-items:center; padding:7px 0; border-bottom:1px solid #1a2540; }
.info-row:last-child { border-bottom:none; }

/* COORD DRAWER */
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
        with ui.element('div').style('padding:20px; overflow-y:auto; height:100%; display:flex; flex-direction:column;'):
            with ui.element('div').style('display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;'):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('my_location').style('color:#EAB308; font-size:20px;')
                    ui.label('Coordenadas').style('font-size:16px; font-weight:800; color:#f1f5f9;')
                ui.button(icon='close', on_click=lambda: coord_drawer.hide()).props('flat round dense').style('color:#6b7280;')
            ui.label('Mova o mouse até a posição e clique em Capturar. A captura ocorre após 2 segundos.').style('font-size:12px; color:#6b7280; line-height:1.6; display:block; margin-bottom:16px;')
            for key, lbl_txt in COORD_KEYS:
                x, y = state[key]
                with ui.element('div').classes('coord-item'):
                    with ui.element('div').style('display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;'):
                        with ui.element('div'):
                            ui.label(lbl_txt).style('font-size:11px; font-weight:700; color:#6b7280; display:block;')
                            cl = ui.label(f'{x},  {y}').style('font-size:20px; font-weight:800; color:#EAB308; font-family:monospace; display:block;')
                            coord_labels[key] = cl
                        ui.element('div').style('width:8px;height:8px;border-radius:50%;background:#22c55e;margin-top:4px;flex-shrink:0;')
                    with ui.row().classes('gap-2 w-full'):
                        cb = ui.button(on_click=lambda k=key: _capturar_coord(k)).classes('btn-cap-sm')
                        with cb: ui.icon('my_location',size='xs'); ui.label('Capturar')
                        coord_btns[key] = cb
                        eb = ui.button(on_click=lambda k=key: _editar_coord(k)).classes('btn-edit-sm')
                        with eb: ui.icon('edit',size='xs'); ui.label('Editar')
            with ui.element('div').style('margin-top:auto; padding-top:16px; border-top:1px solid #1a2540;'):
                ui.label('Salvo em config/coordenadas.json').style('font-size:11px; color:#4b5563; display:block;')

    # ── HEADER ──────────────────────────────────────────────────────────────
    with ui.header(elevated=False).style(
        'background:#0d1526; border-bottom:1px solid #1a2540; padding:0 20px; height:52px; z-index:300;'
    ):
        with ui.row().classes('items-center justify-between w-full h-full'):
            with ui.row().classes('items-center gap-2'):
                ui.icon('fastfood', size='sm').style('color:#EAB308;')
                ui.html('<span style="font-size:17px;font-weight:800;color:#EAB308;">99Food</span>'
                        '<span style="font-size:17px;font-weight:300;color:#f1f5f9;margin-left:4px;">Automation</span>')
                ui.html('<span style="background:rgba(234,179,8,.15);border:1px solid rgba(234,179,8,.4);border-radius:5px;padding:2px 8px;font-size:11px;font-weight:700;color:#EAB308;">v1.0</span>')
            with ui.row().classes('items-center gap-3'):
                ui.icon('light_mode',size='xs').style('color:#6b7280;')
                ui.switch('',value=True,on_change=lambda e: dark.enable() if e.value else dark.disable()).props('color=yellow dense')
                ui.icon('dark_mode',size='xs').style('color:#6b7280;')
                ui.separator().props('vertical').style('height:20px;background:#2d3748;margin:0 6px;')
                with ui.row().classes('items-center gap-2').style('cursor:pointer;'):
                    with ui.element('div').style('width:32px;height:32px;border-radius:50%;background:#374151;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:13px;'): ui.label('A')
                    ui.label('Admin').style('font-size:13px;color:#e2e8f0;')
                    ui.icon('expand_more',size='xs').style('color:#6b7280;')

    # ── SIDEBAR ─────────────────────────────────────────────────────────────
    with ui.left_drawer(value=True, bordered=False).style(
        'width:260px; background:#0d1526; border-right:1px solid #1a2540; padding:14px 10px;'
    ):
        file_btn_refs = {}
        def _sel_arquivo(key, nome):
            state['arquivo'] = os.path.join(DATA_PATH, nome)
            for k, b in file_btn_refs.items():
                b.classes(add='selected') if k==key else b.classes(remove='selected')
            _push('arquivo', f'Arquivo: {nome}')
            _atualizar_resumo()

        with ui.element('div').classes('dash-item active'):
            ui.icon('home',size='xs').style('color:inherit;'); ui.label('Dashboard').style('color:inherit;')
        ui.element('div').style('height:10px;')

        ui.label('DADOS').classes('sec-lbl')
        fb_pizza = ui.element('div').classes('file-item selected').on('click', lambda: _sel_arquivo('pizza','pizza.txt'))
        file_btn_refs['pizza'] = fb_pizza
        with fb_pizza:
            ui.icon('insert_drive_file',size='xs').style('color:inherit;'); ui.label('pizza.txt').style('color:inherit;font-size:13px;')
        fb_comp = ui.element('div').classes('file-item').on('click', lambda: _sel_arquivo('complemento','complemento.txt'))
        file_btn_refs['complemento'] = fb_comp
        with fb_comp:
            ui.icon('insert_drive_file',size='xs').style('color:inherit;'); ui.label('complemento.txt').style('color:inherit;font-size:13px;')
        ui.element('div').style('height:10px;')

        ui.label('CONFIGURAÇÕES').classes('sec-lbl')
        with ui.element('div').classes('nav-item'):
            ui.icon('speed',size='xs').style('color:inherit;'); ui.label('Velocidade').style('color:inherit;font-size:13px;')
        with ui.element('div').classes('nav-item').on('click', lambda: coord_drawer.toggle()):
            ui.icon('my_location',size='xs').style('color:inherit;'); ui.label('Coordenadas').style('color:inherit;font-size:13px;')
        with ui.element('div').classes('nav-item'):
            ui.icon('tune',size='xs').style('color:inherit;'); ui.label('Preferências').style('color:inherit;font-size:13px;')
        ui.element('div').style('height:10px;')

        ui.label('COMANDOS').classes('sec-lbl')
        with ui.element('div').classes('nav-item active').on('click', lambda: _iniciar()):
            ui.icon('play_arrow',size='xs').style('color:inherit;'); ui.label('Executar').style('color:inherit;font-size:13px;')
        with ui.element('div').classes('nav-item'):
            ui.icon('history',size='xs').style('color:inherit;'); ui.label('Histórico').style('color:inherit;font-size:13px;')

        with ui.element('div').style('position:absolute;bottom:16px;left:10px;right:10px;background:#131c2e;border:1px solid #1e2d45;border-radius:12px;padding:14px;'):
            with ui.row().classes('items-center justify-between'):
                status_sidebar_lbl = ui.label('Pronto para automatizar').style('font-size:13px;font-weight:600;color:#f1f5f9;')
                ui.element('div').style('width:8px;height:8px;border-radius:50%;background:#22c55e;box-shadow:0 0 8px #22c55e;flex-shrink:0;')
            ui.label('🚀 Seu cardápio, do jeito certo.').style('font-size:11px;color:#6b7280;margin-top:4px;display:block;')

    # ── PAGE CONTENT ─────────────────────────────────────────────────────────
    with ui.element('div').style('''
                                    padding:20px;
                                    width:100%;
                                    min-height:calc(100vh - 52px);
                                '''):

        # Title row
        with ui.element('div').style('display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;'):
            with ui.row().classes('items-center gap-3'):
                with ui.element('div').style('width:48px;height:48px;border-radius:12px;background:#1e293b;display:flex;align-items:center;justify-content:center;border:1px solid #2d3748;flex-shrink:0;'):
                    ui.icon('auto_fix_high').style('color:#EAB308;font-size:22px;')
                with ui.element('div'):
                    ui.label('Painel de Automação').style('font-size:24px;font-weight:700;color:#f1f5f9;display:block;')
                    ui.label('Automatize a criação do seu cardápio de forma rápida e inteligente').style('font-size:13px;color:#64748b;display:block;margin-top:2px;')
            with ui.element('div').style('display:flex;align-items:center;gap:6px;background:rgba(34,197,94,.08);border:1px solid rgba(34,197,94,.25);border-radius:20px;padding:6px 14px;flex-shrink:0;'):
                ui.element('div').style('width:7px;height:7px;border-radius:50%;background:#22c55e;')
                ui.label('Servidor conectado').style('font-size:12px;color:#22c55e;font-weight:500;')

        # 2-column grid
        with ui.element('div').style('''
                                        display:grid;
                                        grid-template-columns:minmax(0,1fr) 320px;
                                        gap:20px;
                                        width:100%;
                                        align-items:start;
                                    '''):

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
                        with btn_par_status:
                            ui.icon('stop',size='xs'); ui.label('Parar').style('font-size:13px;font-weight:700;')
                        btn_par_status.disable()

                    with ui.element('div').style('display:flex;gap:10px;'):
                        def _stat(icon_nm, lbl_txt, ref_key, init, has_bar=False):
                            with ui.element('div').classes('stat-box'):
                                with ui.element('div').classes('stat-icon'):
                                    ui.icon(icon_nm,size='xs').style('color:#64748b;')
                                with ui.element('div').style('flex:1;min-width:0;'):
                                    ui.label(lbl_txt).style('font-size:10px;color:#6b7280;font-weight:700;letter-spacing:.06em;text-transform:uppercase;display:block;')
                                    lbl = ui.label(init).style('font-size:18px;font-weight:800;color:#f1f5f9;display:block;')
                                    ui_refs[ref_key] = lbl
                                    if has_bar:
                                        with ui.element('div').classes('prog-track'):
                                            ui.element('div').classes('prog-fill').props('id=prog-bar')
                        _stat('timer',       'Tempo',     'tempo_lbl', '00:00:00')
                        _stat('grid_view',   'Itens',     'itens_lbl', '0')
                        _stat('show_chart',  'Médias',    'media_lbl', '—')
                        _stat('trending_up', 'Progresso', 'prog_lbl',  '0%', has_bar=True)

                # CONTROLES
                with ui.element('div').classes('card'):
                    with ui.row().classes('items-center gap-2').style('margin-bottom:14px;'):
                        ui.icon('tune').style('color:#EAB308;font-size:18px;')
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
                            ui.icon('terminal').style('color:#EAB308;font-size:18px;')
                            ui.label('Log de Execução').style('font-size:14px;font-weight:700;color:#f1f5f9;')
                        with ui.row().classes('items-center gap-1'):
                            with ui.button(on_click=lambda: _exportar_log()).props('flat dense').style('color:#6b7280;padding:4px;'):
                                ui.icon('download',size='xs')
                            with ui.button(on_click=lambda: _limpar_log()).props('flat dense').style('color:#6b7280;padding:4px;'):
                                ui.icon('delete',size='xs')

                    log_scroll = ui.scroll_area().classes('log-area').style('height:calc(100vh - 540px);min-height:320px;')
                    with log_scroll:
                        log_container = ui.column().classes('w-full gap-0')
                    log_ref['container'] = log_container
                    log_ref['scroll']    = log_scroll
                    _push('info', '99Food Automation Panel — Pronto para iniciar')

            # ── RIGHT PANEL ─────────────────────────────────────────────
            with ui.element('div').style('display:flex;flex-direction:column;gap:14px;'):

                with ui.element('div').classes('card'):
                    with ui.row().classes('items-center gap-2').style('margin-bottom:14px;'):
                        ui.icon('speed').style('color:#EAB308;font-size:18px;')
                        ui.label('Velocidade de Execução').style('font-size:14px;font-weight:700;color:#f1f5f9;')
                    with ui.element('div').style('margin-bottom:14px;'):
                        with ui.element('div').style('display:flex;justify-content:space-between;margin-bottom:6px;'):
                            ui.label('Delay de digitação').style('font-size:13px;color:#94a3b8;')
                            dup_val = ui.label('2.0s').style('font-size:13px;font-weight:700;color:#EAB308;')
                        def on_dup(e): state['delay_dup']=e.value; dup_val.set_text(f'{e.value:.1f}s')
                        ui.slider(min=1,max=8,step=0.5,value=2.0,on_change=on_dup).props('color=yellow').classes('w-full')
                    with ui.element('div'):
                        with ui.element('div').style('display:flex;justify-content:space-between;margin-bottom:6px;'):
                            ui.label('Delay de envio').style('font-size:13px;color:#94a3b8;')
                            env_val = ui.label('3.0s').style('font-size:13px;font-weight:700;color:#EAB308;')
                        def on_env(e): state['delay_env']=e.value; env_val.set_text(f'{e.value:.1f}s')
                        ui.slider(min=1,max=8,step=0.5,value=3.0,on_change=on_env).props('color=yellow').classes('w-full')

                with ui.element('div').classes('card'):
                    with ui.row().classes('items-center gap-2').style('margin-bottom:12px;'):
                        ui.icon('summarize').style('color:#EAB308;font-size:18px;')
                        ui.label('Resumo do Arquivo').style('font-size:14px;font-weight:700;color:#f1f5f9;')
                    def info_row(lbl, key, color='#f1f5f9', init='—'):
                        with ui.element('div').classes('info-row'):
                            ui.label(lbl).style('font-size:13px;color:#6b7280;')
                            v = ui.label(init).style(f'font-size:13px;font-weight:600;color:{color};text-align:right;')
                            file_info_ref[key] = v
                    info_row('Arquivo atual',      'nome',   '#EAB308', 'pizza.txt')
                    info_row('Tamanho',            'size')
                    info_row('Última modificação', 'mtime')
                    info_row('Linhas',             'lines')
                    info_row('Status',             'status', '#22c55e', '—')

                with ui.element('div').classes('card'):
                    with ui.row().classes('items-center gap-2').style('margin-bottom:12px;'):
                        ui.icon('bolt').style('color:#EAB308;font-size:18px;')
                        ui.label('Comandos Rápidos').style('font-size:14px;font-weight:700;color:#f1f5f9;')
                    with ui.element('div').style('display:flex;flex-direction:column;gap:8px;'):
                        with ui.button(on_click=lambda: _testar_conexao()).classes('btn-quick'):
                            with ui.row().classes('items-center gap-2 w-full justify-center'):
                                ui.icon('wifi',size='xs'); ui.label('Testar Conexão')
                        with ui.button(on_click=lambda: _preview_arquivo()).classes('btn-quick'):
                            with ui.row().classes('items-center gap-2 w-full justify-center'):
                                ui.icon('visibility',size='xs'); ui.label('Pré-visualizar Arquivo')

    # ── FOOTER ──────────────────────────────────────────────────────────────
    with ui.element('div').style('background:#0d1526;border-top:1px solid #1a2540;padding:10px 24px;display:flex;justify-content:space-between;align-items:center;'):
        ui.label('© 2025 99Food Automation. Todos os direitos reservados.').style('font-size:12px;color:#4b5563;')
        ui.html('<span style="font-size:12px;color:#4b5563;">Feito com <span style="color:#ef4444;">♥</span> para facilitar seu dia.</span>')

    # ── AUXILIARES ──────────────────────────────────────────────────────────
    def _atualizar_resumo():
        path = state['arquivo']
        size, mtime, lines, ok = _info_arquivo(path)
        file_info_ref['nome'].set_text(os.path.basename(path))
        file_info_ref['size'].set_text(size)
        file_info_ref['mtime'].set_text(mtime)
        file_info_ref['lines'].set_text(lines)
        file_info_ref['status'].set_text('Carregado' if ok else 'Não encontrado')
        file_info_ref['status'].style(f'font-size:13px;font-weight:600;color:{"#22c55e" if ok else "#ef4444"};text-align:right;')

    _atualizar_resumo()

    def _testar_conexao():
        try:
            import pyautogui
            ui.notify('✅ pyautogui OK — automação pronta!', type='positive', position='top-right', timeout=4000)
        except Exception:
            ui.notify('❌ pyautogui não encontrado', type='negative', position='top-right', timeout=4000)

    def _preview_arquivo():
        path = state['arquivo']
        try:
            with open(path,'r',encoding='utf-8') as f:
                linhas = [l.strip() for l in f if l.strip()][:10]
            with ui.dialog() as dlg, ui.card().style('min-width:480px;background:#131c2e;border:1px solid #1e2d45;'):
                with ui.row().classes('items-center gap-2').style('margin-bottom:12px;'):
                    ui.icon('preview').style('color:#EAB308;')
                    ui.label(f'Prévia — {os.path.basename(path)}').style('font-weight:700;font-size:15px;')
                with ui.element('div').style('background:#080e1a;border-radius:8px;padding:14px;max-height:300px;overflow-y:auto;'):
                    for i, l in enumerate(linhas, 1):
                        ui.label(f'{i:02d}. {l}').style('font-family:monospace;font-size:12px;color:#94a3b8;display:block;padding:2px 0;')
                ui.button('Fechar', on_click=dlg.close).props('flat color=yellow').style('margin-top:12px;')
            dlg.open()
        except Exception as e:
            ui.notify(f'Erro: {e}', type='negative')

    def _exportar_log():
        ui.notify('Log exportado em logs/log_export.txt', type='positive', position='top-right', timeout=4000)

    def _capturar_coord(key):
        import pyautogui
        btn = coord_btns.get(key)
        if btn: btn.disable()
        _push('aviso', 'Mova o mouse para a posição...')
        def _run():
            for i in range(2, 0, -1):
                _push('info', f'Capturando em {i}s...'); time.sleep(1.0)
            x, y = pyautogui.position()
            coord_queue.put(('update', key, x, y))
            coord_queue.put(('enable_btn', key))
            _salvar_coordenadas()
            _push('sucesso', f'"{key}" → ({x}, {y}) salvo')
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

    # ── SYNC TIMER ──────────────────────────────────────────────────────────
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
                tipo_n, ad, fa = notif_queue.get_nowait()
                if tipo_n == 'sucesso':
                    ui.notify(f'✅ Concluído! {ad} itens adicionados.', type='positive', position='top', timeout=8000)
                else:
                    ui.notify(f'⚠️ {ad} adicionados, {fa} falhados.', type='warning', position='top', timeout=8000)
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
            itens=state['itens_ok']; total=state['itens_total']
            ui_refs['itens_lbl'].set_text(str(itens))
            if elapsed>=5 and itens>0: ui_refs['media_lbl'].set_text(f'{itens/(elapsed/60):.1f}/min')
            pct=int(itens/total*100) if total>0 else 0
            ui_refs['prog_lbl'].set_text(f'{pct}%')
            ui.run_javascript(f"var b=document.getElementById('prog-bar');if(b)b.style.width='{pct}%'")

        fase = state['fase']
        if fase != prev_fase['v']:
            prev_fase['v'] = fase
            if fase=='rodando':
                status_txt.set_text('Automação em andamento...'); status_txt.style('font-size:20px;font-weight:700;color:#EAB308;display:block;')
                status_sidebar_lbl.set_text('Em execução')
                ui.run_javascript("var s=document.getElementById('status-spinner');if(s){s.classList.remove('paused','stopped');s.classList.add('spinning');}")
                btn_par_status.enable()
                _btn_ini_global['el'].disable(); _btn_ini_global['el'].classes(add='running')
                _btn_ini_global['el'].clear()
                with _btn_ini_global['el']: ui.icon('pending',size='sm'); ui.label('Rodando...')
                _btn_pau_global['el'].enable(); _btn_par_global['el'].enable()
            elif fase=='pausado':
                status_txt.set_text('Pausado — aguardando retomada...'); status_txt.style('font-size:20px;font-weight:700;color:#ca8a04;display:block;')
                ui.run_javascript("var s=document.getElementById('status-spinner');if(s){s.classList.remove('spinning','stopped');s.classList.add('paused');}")
            elif fase=='parando':
                status_txt.set_text('Encerrando...'); status_txt.style('font-size:20px;font-weight:700;color:#ef4444;display:block;')
                ui.run_javascript("var s=document.getElementById('status-spinner');if(s){s.classList.remove('spinning','paused');s.classList.add('stopped');}")
            else:
                status_txt.set_text('Aguardando comando...'); status_txt.style('font-size:20px;font-weight:700;color:#EAB308;display:block;')
                status_sidebar_lbl.set_text('Pronto para automatizar')
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
        if state['fase']!='parado': return
        stop_event.clear(); pause_event.set()
        state.update({'fase':'rodando','inicio_tempo':time.time(),'tempo_pausado':0.0,'pausa_inicio':None,'itens_ok':0,'itens_total':0})
        ui_refs['tempo_lbl'].set_text('00:00:00'); ui_refs['itens_lbl'].set_text('0')
        ui_refs['media_lbl'].set_text('—'); ui_refs['prog_lbl'].set_text('0%')
        ui.run_javascript("var b=document.getElementById('prog-bar');if(b)b.style.width='0%'")
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
        btn_pau.classes(remove='btn-resume',add='btn-ctrl'); btn_pau.clear()
        with btn_pau: ui.icon('pause',size='sm'); ui.label('Pausar')
        _push('parada','Encerrando após o item atual...')

    def _limpar_log():
        log_ref['container'].clear()

    ui.run(title='99Food Automation', port=8081, reload=True, favicon='🍕')


if __name__ in {"__main__", "__mp_main__"}:
    iniciar_painel()