"""
Painel de Automação Keeta - NiceGUI
Tema: Dark/Light com destaque laranja (cor Keeta)
Funcionalidades: Iniciar / Pausar / Retomar / Parar + Captura de Coordenadas
"""

import os
import sys
import time
import threading
import queue as queue_module
import json

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.append(root_path)

DATA_PATH   = os.path.join(root_path, 'data')
CONFIG_PATH = os.path.join(root_path, 'config')

from nicegui import ui

# ── Estado global ──────────────────────────────────────────────────────────
state = {
    'fase':         'parado',
    'arquivo':      os.path.join(DATA_PATH, 'pizza.txt'),
    'delay_dup':    3.0,
    'delay_env':    3.0,
    # Coordenadas
    'campo_nome':   (746,  407),
    'editar_preco': (1537, 551),
    'campo_preco':  (812,  693),
    'concluir':     (1539, 819),
    'enviar':       (1514, 971),
    # Métricas
    'inicio_tempo': None,
    'tempo_pausado': 0.0,
    'pausa_inicio': None,
    'itens_ok':     0,
    'itens_total':  0,
}

COORD_KEYS = [
    ('campo_nome',   'Campo nome'),
    ('editar_preco', 'Editar preço'),
    ('campo_preco',  'Campo preço'),
    ('concluir',     'Btn Concluir'),
    ('enviar',       'Btn Enviar'),
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
        data = {key: list(state[key]) for key, _ in COORD_KEYS}
        with open(os.path.join(CONFIG_PATH, 'coordenadas.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

_carregar_coordenadas()

stop_event  = threading.Event()
pause_event = threading.Event()
pause_event.set()

log_queue   = queue_module.Queue()
coord_queue = queue_module.Queue()

LOG_ICONS = {
    'inicio':    ('rocket_launch',  '#F97316'),
    'arquivo':   ('description',    '#94a3b8'),
    'item':      ('play_arrow',     '#F97316'),
    'sucesso':   ('check_circle',   '#22c55e'),
    'erro':      ('cancel',         '#ef4444'),
    'aviso':     ('warning',        '#facc15'),
    'parada':    ('block',          '#ef4444'),
    'pausa':     ('pause_circle',   '#facc15'),
    'retomada':  ('play_circle',    '#22c55e'),
    'resumo':    ('bar_chart',      '#F97316'),
    'info':      ('info',           '#94a3b8'),
    'separador': ('remove',         '#1e293b'),
}

log_ref      = {'container': None, 'scroll': None}
coord_labels = {}
coord_btns   = {}


def _push(tipo: str, mensagem: str = ''):
    log_queue.put((tipo, mensagem))


def _aguardar_se_pausado() -> bool:
    while not pause_event.is_set():
        if stop_event.is_set():
            return False
        time.sleep(0.1)
    return True


def _sleep_cancelavel(segundos: float) -> bool:
    fim = time.time() + segundos
    while time.time() < fim:
        if stop_event.is_set():
            return False
        if not pause_event.is_set():
            tempo_restante = fim - time.time()
            if not _aguardar_se_pausado():
                return False
            fim = time.time() + tempo_restante
        time.sleep(0.1)
    return True


# ── Thread de automação ────────────────────────────────────────────────────
def _thread_automacao():
    from utils import som
    try:
        import pyautogui
        import pyperclip
        pyautogui.PAUSE = 0.3

        arquivo = state['arquivo']
        _push('separador')
        _push('inicio', 'Iniciando automação Keeta...')

        if not os.path.exists(arquivo):
            _push('erro', f'Arquivo não encontrado: {arquivo}')
            return

        with open(arquivo, 'r', encoding='utf-8') as f:
            linhas = [l for l in f.readlines() if l.strip()]

        _push('arquivo', f'{len(linhas)} itens encontrados em {os.path.basename(arquivo)}')
        _push('separador')
        state['itens_total'] = len(linhas)
        time.sleep(1)

        adicionados = 0
        falhados    = 0

        for i, linha in enumerate(linhas, start=1):
            if stop_event.is_set():
                _push('parada', 'Automação interrompida pelo usuário.')
                break
            if not pause_event.is_set():
                _push('pausa', f'Pausado antes do item {i} — aguardando retomada...')
                if not _aguardar_se_pausado():
                    _push('parada', 'Parado durante pausa.')
                    break
                _push('retomada', 'Retomando automação...')

            try:
                partes = linha.strip().split('|')
                if len(partes) != 3:
                    _push('aviso', f'Linha {i} — formato inválido: {linha.strip()}')
                    falhados += 1
                    continue

                nome, descricao, preco_txt = partes
                nome       = nome.strip()
                descricao  = descricao.strip() + ' Foto Ilustrativa.'
                preco_base = float(preco_txt.strip().replace(',', '.'))

                _push('item', f'[{i}/{len(linhas)}]  {nome}  —  R$ {preco_base:.2f}')

                pyautogui.press('home')

                # ⚠️ COORDENADA: campo_nome — edite na sidebar ou config/coordenadas.json
                pyperclip.copy(nome)
                pyautogui.click(*state['campo_nome'], duration=0.1)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(1)

                # Descrição (2 TABs)
                pyautogui.press('tab')
                pyautogui.press('tab')
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                pyperclip.copy(descricao)
                pyautogui.hotkey('ctrl', 'v')

                pyautogui.press('tab')

                # ⚠️ COORDENADA: editar_preco
                pyautogui.click(*state['editar_preco'], duration=0.1)

                # ⚠️ COORDENADA: campo_preco
                pyautogui.click(*state['campo_preco'], duration=0.1)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                pyautogui.write(f'{preco_base:.2f}', interval=0.05)
                pyautogui.press('tab')
                pyautogui.press('backspace')
                pyautogui.write(f'{preco_base:.2f}', interval=0.05)
                pyautogui.scroll(-600)
                time.sleep(0.5)

                # ⚠️ COORDENADA: concluir
                pyautogui.moveTo(*state['concluir'], duration=0.1)
                pyautogui.click()

                if not _sleep_cancelavel(state['delay_dup']):
                    _push('parada', 'Parado durante delay de duplicação.')
                    break

                # ⚠️ COORDENADA: enviar
                pyautogui.moveTo(*state['enviar'], duration=0.1)
                pyautogui.click()

                if not _sleep_cancelavel(state['delay_env']):
                    _push('parada', 'Parado durante delay de envio.')
                    break

                _push('sucesso', f'"{nome}" adicionado com sucesso')
                adicionados += 1
                state['itens_ok'] = adicionados

            except Exception as e:
                _push('erro', f'Erro no item {i}: {e}')
                falhados += 1

        _push('separador')
        _push('resumo', f'Concluído — {adicionados} adicionados   {falhados} falhados')
        _push('separador')
        if falhados == 0 and adicionados > 0:
            som.som_sucesso()
        elif falhados > 0:
            som.som_erro()

    except Exception as e:
        _push('erro', f'Erro fatal: {e}')
    finally:
        state['fase'] = 'parado'
        stop_event.clear()
        pause_event.set()


_btn_ini_global = {'el': None}
_btn_pau_global = {'el': None}
_btn_par_global = {'el': None}


def iniciar_painel():

    ui.add_head_html('''
    <style>
      .btn-start {
        background: linear-gradient(135deg, #F97316, #ea6d10) !important;
        color: #fff !important; font-weight: 700 !important; font-size: 14px !important;
        border-radius: 10px !important; padding: 10px 22px !important;
        text-transform: none !important; letter-spacing: 0 !important;
        box-shadow: 0 4px 14px rgba(249,115,22,.35) !important; transition: all .2s !important;
      }
      .btn-start:hover:not([disabled]) { transform: translateY(-2px) !important; box-shadow: 0 6px 20px rgba(249,115,22,.5) !important; }
      .btn-start[disabled] { opacity: .4 !important; }
      .btn-pause {
        background: linear-gradient(135deg, #ca8a04, #a16207) !important;
        color: #fff !important; font-weight: 700 !important; font-size: 14px !important;
        border-radius: 10px !important; padding: 10px 22px !important;
        text-transform: none !important; transition: all .2s !important;
      }
      .btn-resume {
        background: linear-gradient(135deg, #16a34a, #15803d) !important;
        color: #fff !important; font-weight: 700 !important; font-size: 14px !important;
        border-radius: 10px !important; padding: 10px 22px !important;
        text-transform: none !important; transition: all .2s !important;
      }
      .btn-pause[disabled], .btn-resume[disabled] { opacity: .3 !important; }
      .btn-stop {
        background: linear-gradient(135deg, #ef4444, #dc2626) !important;
        color: #fff !important; font-weight: 700 !important; font-size: 14px !important;
        border-radius: 10px !important; padding: 10px 22px !important;
        text-transform: none !important; transition: all .2s !important;
      }
      .btn-stop[disabled] { opacity: .3 !important; }
      .section-lbl { font-size:10px !important; font-weight:800 !important; letter-spacing:.14em !important; text-transform:uppercase !important; color:#6b7280 !important; }
      .status-card { border-left: 4px solid #F97316 !important; border-radius: 10px !important; }
      .chip-ativo { background:rgba(249,115,22,.15) !important; color:#F97316 !important; border:1px solid rgba(249,115,22,.4) !important; border-radius:6px !important; padding:2px 10px !important; font-size:13px !important; font-weight:600 !important; }
      .log-row { display:flex; align-items:center; gap:8px; min-height:26px; padding:1px 0; }
      .log-msg  { font-family:"Courier New",Consolas,monospace; font-size:13px; line-height:1.6; }
      .btn-cap  { min-width:0 !important; padding:2px 6px !important; font-size:11px !important; border-radius:6px !important; text-transform:none !important; }
    </style>
    ''')

    dark = ui.dark_mode()
    dark.enable()

    # ── HEADER ────────────────────────────────────────────────────────────
    with ui.header(elevated=True).style('background:#0f172a; border-bottom:1px solid #1e293b; padding:8px 20px; z-index:200;'):
        with ui.row().classes('items-center justify-between w-full'):
            with ui.row().classes('items-center gap-2'):
                ui.icon('restaurant_menu', size='sm').style('color:#F97316')
                ui.label('Keeta').style('font-size:20px; font-weight:800; color:#fff; letter-spacing:-.03em')
                ui.label('Automation Panel').style('font-size:20px; font-weight:300; color:#94a3b8')
                ui.badge('v1.0', color='orange').classes('ml-1')
            with ui.row().classes('items-center gap-1'):
                ui.icon('light_mode', size='xs').style('color:#94a3b8')
                ui.switch('', value=True, on_change=lambda e: dark.enable() if e.value else dark.disable()).props('color=orange dense')
                ui.icon('dark_mode', size='xs').style('color:#94a3b8')

    # ── SIDEBAR ───────────────────────────────────────────────────────────
    with ui.left_drawer(value=True, bordered=True).style('width:280px; background:#0a0f1e; padding:0;'):
        with ui.column().classes('p-5 gap-5 w-full'):

            ui.label('Arquivo de Dados').classes('section-lbl')
            arquivo_chip = ui.label('pizza.txt').classes('chip-ativo')

            def sel_pizza():
                state['arquivo'] = os.path.join(DATA_PATH, 'pizza.txt')
                arquivo_chip.set_text('pizza.txt')
                _push('arquivo', 'Selecionado: pizza.txt')

            def sel_complemento():
                state['arquivo'] = os.path.join(DATA_PATH, 'complemento.txt')
                arquivo_chip.set_text('complemento.txt')
                _push('arquivo', 'Selecionado: complemento.txt')

            with ui.row().classes('gap-2 flex-wrap'):
                with ui.button(on_click=sel_pizza).props('flat dense').style('color:#F97316; text-transform:none;'):
                    ui.icon('local_pizza', size='xs')
                    ui.label('pizza.txt').style('font-size:12px;')
                with ui.button(on_click=sel_complemento).props('flat dense').style('color:#F97316; text-transform:none;'):
                    ui.icon('add_circle_outline', size='xs')
                    ui.label('complemento.txt').style('font-size:12px;')

            ui.separator().style('opacity:.15')

            ui.label('Velocidade').classes('section-lbl')
            with ui.column().classes('gap-4 w-full'):
                with ui.row().classes('items-center justify-between w-full'):
                    with ui.row().classes('items-center gap-1'):
                        ui.icon('content_copy', size='xs').style('color:#6b7280')
                        ui.label('Delay duplicação').style('font-size:13px; color:#94a3b8;')
                    dup_lbl = ui.label('3.0s').style('color:#F97316; font-weight:700; font-size:13px;')

                def on_dup(e):
                    state['delay_dup'] = e.value
                    dup_lbl.set_text(f'{e.value:.1f}s')

                ui.slider(min=1, max=8, step=0.5, value=3.0, on_change=on_dup).props('color=orange').classes('w-full')

                with ui.row().classes('items-center justify-between w-full'):
                    with ui.row().classes('items-center gap-1'):
                        ui.icon('send', size='xs').style('color:#6b7280')
                        ui.label('Delay envio').style('font-size:13px; color:#94a3b8;')
                    env_lbl = ui.label('3.0s').style('color:#F97316; font-weight:700; font-size:13px;')

                def on_env(e):
                    state['delay_env'] = e.value
                    env_lbl.set_text(f'{e.value:.1f}s')

                ui.slider(min=1, max=8, step=0.5, value=3.0, on_change=on_env).props('color=orange').classes('w-full')

            ui.separator().style('opacity:.15')

            # ── COORDENADAS ──────────────────────────────────────────────
            ui.label('Coordenadas').classes('section-lbl')

            for key, lbl_txt in COORD_KEYS:
                x, y = state[key]
                with ui.column().classes('gap-1 w-full mb-1'):
                    with ui.row().classes('items-center justify-between w-full'):
                        ui.label(lbl_txt).style('font-size:11px; color:#6b7280; font-weight:600;')
                        coord_lbl = ui.label(f'{x}, {y}').style(
                            'font-size:11px; font-family:monospace; color:#F97316;'
                        )
                        coord_labels[key] = coord_lbl

                    with ui.row().classes('gap-1'):
                        cap_btn = ui.button(
                            on_click=lambda k=key: _capturar_coord(k)
                        ).classes('btn-cap').props('color=orange outline dense')
                        with cap_btn:
                            ui.icon('my_location', size='xs')
                            ui.label('Capturar').style('font-size:10px;')
                        coord_btns[key] = cap_btn

                        with ui.button(
                            on_click=lambda k=key: _editar_coord(k)
                        ).classes('btn-cap').props('flat dense').style('color:#94a3b8; text-transform:none;'):
                            ui.icon('edit', size='xs')
                            ui.label('Editar').style('font-size:10px;')

            ui.separator().style('opacity:.15')

            ui.label('Formato do Arquivo').classes('section-lbl')
            ui.label('Nome | Descrição | Preço').style(
                'font-family:monospace; font-size:12px; color:#F97316; background:#1e293b; padding:6px 10px; border-radius:6px;'
            )

    # ── ÁREA PRINCIPAL ────────────────────────────────────────────────────
    with ui.column().classes('w-full p-6 gap-4').style('max-width:900px; margin:0 auto;'):

        with ui.card().classes('w-full status-card'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('radio_button_unchecked', size='xs').style('color:#6b7280')
                    status_txt = ui.label('Aguardando comando...').style('font-size:14px; font-weight:500;')
                status_badge = ui.badge('Parado', color='red')

        with ui.card().classes('w-full').style('background:#0f172a; border:1px solid #1e293b;'):
            with ui.row().classes('items-center gap-6 flex-wrap'):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('timer', size='xs').style('color:#F97316')
                    ui.label('Tempo:').style('font-size:13px; color:#6b7280;')
                    tempo_lbl = ui.label('00:00').style('font-size:18px; font-weight:700; font-family:monospace; color:#fff;')
                with ui.row().classes('items-center gap-2'):
                    ui.icon('check_circle', size='xs').style('color:#22c55e')
                    ui.label('Itens:').style('font-size:13px; color:#6b7280;')
                    itens_lbl = ui.label('0').style('font-size:18px; font-weight:700; font-family:monospace; color:#22c55e;')
                with ui.row().classes('items-center gap-2'):
                    ui.icon('speed', size='xs').style('color:#F97316')
                    ui.label('Média:').style('font-size:13px; color:#6b7280;')
                    media_lbl = ui.label('—').style('font-size:18px; font-weight:700; font-family:monospace; color:#F97316;')

        with ui.row().classes('gap-3 items-center flex-wrap'):
            btn_ini = ui.button(on_click=lambda: _iniciar()).classes('btn-start')
            with btn_ini:
                ui.icon('play_arrow', size='sm')
                ui.label('Iniciar').style('font-size:14px; font-weight:700;')
            _btn_ini_global['el'] = btn_ini

            btn_pau = ui.button(on_click=lambda: _pausar_retomar()).classes('btn-pause')
            with btn_pau:
                ui.icon('pause', size='sm')
                ui.label('Pausar').style('font-size:14px; font-weight:700;')
            btn_pau.disable()
            _btn_pau_global['el'] = btn_pau

            btn_par = ui.button(on_click=lambda: _parar()).classes('btn-stop')
            with btn_par:
                ui.icon('stop', size='sm')
                ui.label('Parar').style('font-size:14px; font-weight:700;')
            btn_par.disable()
            _btn_par_global['el'] = btn_par

            with ui.button(on_click=lambda: _limpar_log()).props('flat color=grey').style('text-transform:none;'):
                ui.icon('delete_sweep', size='sm')
                ui.label('Limpar Log').style('font-size:13px;')

        with ui.card().classes('w-full'):
            with ui.row().classes('items-center gap-2 mb-2'):
                ui.icon('terminal').style('color:#F97316')
                ui.label('Log de Execução').style('font-weight:700; font-size:15px;')

            log_scroll = ui.scroll_area().classes('w-full').style(
                'height:420px; background:#0f172a; border-radius:8px; padding:12px;'
            )
            with log_scroll:
                log_container = ui.column().classes('w-full gap-0')

            log_ref['container'] = log_container
            log_ref['scroll']    = log_scroll
            _push('info', 'Keeta Automation Panel  —  Pronto para iniciar')

    # ── Timer ─────────────────────────────────────────────────────────────
    def _sync_ui():
        while not log_queue.empty():
            try:
                tipo, msg = log_queue.get_nowait()
                icon_name, color = LOG_ICONS.get(tipo, LOG_ICONS['info'])
                with log_ref['container']:
                    if tipo == 'separador':
                        ui.separator().style('opacity:.15; margin:4px 0;')
                    else:
                        txt_color = '#e2e8f0' if tipo not in ('erro', 'aviso', 'parada', 'pausa') else color
                        with ui.row().classes('log-row'):
                            ui.icon(icon_name, size='xs').style(f'color:{color}; flex-shrink:0;')
                            ui.label(msg).classes('log-msg').style(f'color:{txt_color};')
                log_ref['scroll'].scroll_to(percent=1.0)
            except Exception:
                pass

        while not coord_queue.empty():
            try:
                msg = coord_queue.get_nowait()
                if msg[0] == 'update':
                    _, key, x, y = msg
                    state[key] = (x, y)
                    if key in coord_labels:
                        coord_labels[key].set_text(f'{x}, {y}')
                elif msg[0] == 'enable_btn':
                    key = msg[1]
                    if key in coord_btns:
                        coord_btns[key].enable()
            except Exception:
                pass

        if state['inicio_tempo'] is not None:
            pausado_extra = 0.0
            if state['fase'] == 'pausado' and state['pausa_inicio'] is not None:
                pausado_extra = time.time() - state['pausa_inicio']
            elapsed = max(0.0, time.time() - state['inicio_tempo'] - state['tempo_pausado'] - pausado_extra)
            mins, secs = divmod(int(elapsed), 60)
            tempo_lbl.set_text(f'{mins:02d}:{secs:02d}')
            itens = state['itens_ok']
            itens_lbl.set_text(str(itens))
            if elapsed >= 5 and itens > 0:
                media_lbl.set_text(f'{itens / (elapsed / 60):.1f}/min')

        fase = state['fase']
        if fase == 'rodando':
            status_badge.props('color=orange'); status_badge.set_text('Rodando')
        elif fase == 'pausado':
            status_badge.props('color=yellow'); status_badge.set_text('Pausado')
        elif fase == 'parando':
            status_badge.props('color=grey');   status_badge.set_text('Parando...')
        else:
            status_badge.props('color=red');    status_badge.set_text('Parado')
            status_txt.set_text('Aguardando comando...')
            _btn_ini_global['el'].enable()
            _btn_pau_global['el'].disable()
            _btn_par_global['el'].disable()

    ui.timer(0.3, _sync_ui)

    # ── Captura de coordenada ──────────────────────────────────────────────
    def _capturar_coord(key):
        import pyautogui
        btn = coord_btns.get(key)
        if btn:
            btn.disable()
        _push('aviso', 'Mova o mouse para a posição desejada...')

        def _run():
            for i in range(2, 0, -1):
                _push('info', f'Capturando em {i}s...')
                time.sleep(1.0)
            x, y = pyautogui.position()
            coord_queue.put(('update', key, x, y))
            coord_queue.put(('enable_btn', key))
            _salvar_coordenadas()
            _push('sucesso', f'"{key}" capturado: ({x}, {y}) — salvo em config/coordenadas.json')

        threading.Thread(target=_run, daemon=True).start()

    # ── Edição manual ──────────────────────────────────────────────────────
    def _editar_coord(key):
        label_txt = next((l for k, l in COORD_KEYS if k == key), key)
        x0, y0 = state[key]

        with ui.dialog() as dlg, ui.card().style('min-width:280px;'):
            with ui.row().classes('items-center gap-2 mb-2'):
                ui.icon('edit_location', size='sm').style('color:#F97316')
                ui.label(f'Editar — {label_txt}').style('font-weight:700;')

            inp_x = ui.number('X', value=x0, format='%d').classes('w-full')
            inp_y = ui.number('Y', value=y0, format='%d').classes('w-full')

            with ui.row().classes('gap-2 justify-end mt-2'):
                ui.button('Cancelar', on_click=dlg.close).props('flat color=grey')

                def salvar():
                    nx, ny = int(inp_x.value or 0), int(inp_y.value or 0)
                    coord_queue.put(('update', key, nx, ny))
                    _salvar_coordenadas()
                    _push('info', f'"{key}" atualizado para ({nx}, {ny})')
                    dlg.close()

                ui.button('Salvar', on_click=salvar).props('color=orange')

        dlg.open()

    # ── Controles ─────────────────────────────────────────────────────────
    def _iniciar():
        if state['fase'] != 'parado': return
        stop_event.clear()
        pause_event.set()
        state['fase'] = 'rodando'
        state['inicio_tempo']  = time.time()
        state['tempo_pausado'] = 0.0
        state['pausa_inicio']  = None
        state['itens_ok']      = 0
        state['itens_total']   = 0
        tempo_lbl.set_text('00:00')
        itens_lbl.set_text('0')
        media_lbl.set_text('—')
        btn_ini.disable()
        btn_pau.enable()
        btn_par.enable()
        status_txt.set_text('Automação em andamento...')
        threading.Thread(target=_thread_automacao, daemon=True).start()

    def _pausar_retomar():
        if state['fase'] == 'rodando':
            pause_event.clear()
            state['fase'] = 'pausado'
            state['pausa_inicio'] = time.time()
            btn_pau.classes(remove='btn-pause', add='btn-resume')
            btn_pau.clear()
            with btn_pau:
                ui.icon('play_arrow', size='sm')
                ui.label('Retomar').style('font-size:14px; font-weight:700;')
            status_txt.set_text('Pausado — clique em Retomar para continuar')
        elif state['fase'] == 'pausado':
            if state['pausa_inicio'] is not None:
                state['tempo_pausado'] += time.time() - state['pausa_inicio']
                state['pausa_inicio'] = None
            pause_event.set()
            state['fase'] = 'rodando'
            btn_pau.classes(remove='btn-resume', add='btn-pause')
            btn_pau.clear()
            with btn_pau:
                ui.icon('pause', size='sm')
                ui.label('Pausar').style('font-size:14px; font-weight:700;')
            status_txt.set_text('Automação em andamento...')

    def _parar():
        if state['fase'] not in ('rodando', 'pausado'): return
        state['fase'] = 'parando'
        pause_event.set()
        stop_event.set()
        btn_pau.disable()
        btn_par.disable()
        btn_pau.classes(remove='btn-resume', add='btn-pause')
        btn_pau.clear()
        with btn_pau:
            ui.icon('pause', size='sm')
            ui.label('Pausar').style('font-size:14px; font-weight:700;')
        _push('parada', 'Sinal de parada enviado — encerrando após item atual...')
        status_txt.set_text('Parando...')

    def _limpar_log():
        log_ref['container'].clear()

    ui.run(title='Keeta Automation', port=8080, reload=True, favicon='🛵')


if __name__ in {"__main__", "__mp_main__"}:
    iniciar_painel()
