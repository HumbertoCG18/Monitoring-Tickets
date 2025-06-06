import tkinter as tk
from tkinter import ttk, messagebox
import threading
import math
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import concurrent.futures
import ctypes
import sys
from screeninfo import get_monitors

# Temas de cores
THEMES = {
    'light': {
        'bg': '#f0f0f0',
        'fg': '#333333',
        'button': '#3498db',
        'button_hover': '#2980b9',
        'canvas_bg': '#ecf0f1',
        'grid_outline': '#666666',
        'grid_fill': '#d0d0d0',
        'monitor_outline': '#000000',
        'monitor_fill': '#eaeaea',
        'accent': '#3498db',
    },
    'dark': {
        'bg': '#333333',
        'fg': '#f0f0f0',
        'button': '#2980b9',
        'button_hover': '#3498db',
        'canvas_bg': '#2c3e50',
        'grid_outline': '#dddddd',
        'grid_fill': '#555555',
        'monitor_outline': '#bbbbbb',
        'monitor_fill': '#444444',
        'accent': '#3498db',
    }
}

# Função para detectar monitores com identificação
def get_screen_info():
    monitors_info = []
    taskbar_height = 40  # Altura estimada da taskbar

    # Usar screeninfo para obter informações dos monitores
    screen_monitors = get_monitors()

    for i, monitor in enumerate(screen_monitors):
        # Definir o primeiro monitor como primário (ou usar propriedade is_primary se disponível)
        is_primary = getattr(monitor, 'is_primary', i == 0)

        # Extrair o identificador do monitor
        # Screeninfo não fornece os nomes DISPLAY1, DISPLAY2, então usamos números sequenciais
        monitor_id = str(i + 1)

        # Detectar orientação
        if monitor.width > monitor.height:
            default_orientation = "Paisagem"
        else:
            default_orientation = "Retrato"

        # Adicionar informações do monitor à lista
        monitors_info.append({
            'width': monitor.width,
            'height': monitor.height - taskbar_height if is_primary else monitor.height,
            'x_offset': monitor.x,
            'y_offset': monitor.y,
            'is_primary': is_primary,
            'id': monitor_id,
            'default_orientation': default_orientation,
            'orientation': default_orientation  # Orientação atual (pode ser modificada pelo usuário)
        })

    # Ordenar para que o monitor principal seja o primeiro
    monitors_info.sort(key=lambda x: not x['is_primary'])

    return monitors_info

# Variáveis globais
drivers = []  # Lista de drivers
driver_urls = {}  # Dicionário para armazenar URLs atuais de cada driver
stop_monitor = False
closing_in_progress = False
current_theme = 'light'
monitor_orientations = {}  # Armazenar orientações selecionadas

def open_session(url, position, incognito, service=None):
    chrome_options = Options()
    chrome_options.add_argument(f"--window-size={position[0]},{position[1]}")
    chrome_options.add_argument(f"--window-position={position[2]},{position[3]}")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

    if incognito:
        chrome_options.add_argument('--incognito')

    try:
        if service:
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)

        driver.get(url)
        return driver
    except Exception as e:
        print(f"Erro ao abrir sessão: {e}")
        return None

def maximize_window_on_primary(driver):
    """Maximiza a janela no monitor principal"""
    monitors = get_screen_info()
    primary = monitors[0]

    # Primeiro mover para o monitor principal
    driver.set_window_position(primary['x_offset'], primary['y_offset'])

    # Pequena pausa para permitir que a janela seja movida
    time.sleep(0.1)

    # Depois maximizar
    driver.maximize_window()

    # Trazer para frente
    driver.execute_script("window.focus();")

def calculate_positions(num_sessions, auto_arrange):
    if not auto_arrange:
        return [(800, 600, 0, 0)] * num_sessions

    # Detectar monitores e aplicar orientações selecionadas pelo usuário
    monitors = get_screen_info()

    # Aplicar orientações selecionadas pelo usuário
    for i, monitor in enumerate(monitors):
        monitor_id = monitor['id']
        if monitor_id in monitor_orientations:
            monitors[i]['orientation'] = monitor_orientations[monitor_id]

            # Ajustar dimensões se a orientação for diferente da padrão
            if monitor['orientation'] != monitor['default_orientation']:
                monitors[i]['width'], monitors[i]['height'] = monitors[i]['height'], monitors[i]['width']

    monitor_principal = monitors[0]
    monitor_secundario = monitors[1] if len(monitors) > 1 else None

    positions = []

    # Distribuir no monitor principal ou em ambos os monitores
    if num_sessions <= 9 or not monitor_secundario:
        # Usar apenas o monitor principal
        cols = rows = math.ceil(math.sqrt(num_sessions))
        margin = 5

        width = (monitor_principal['width'] - (cols+1)*margin) // cols
        height = (monitor_principal['height'] - (rows+1)*margin) // rows

        for i in range(num_sessions):
            row = i // cols
            col = i % cols
            x = monitor_principal['x_offset'] + margin + col * (width + margin)
            y = monitor_principal['y_offset'] + margin + row * (height + margin)
            positions.append((width, height, x, y))
    else:
        # Primeiras 9 sessões no monitor principal
        cols = rows = 3
        margin = 5

        width = (monitor_principal['width'] - (cols+1)*margin) // cols
        height = (monitor_principal['height'] - (rows+1)*margin) // rows

        for i in range(9):
            row = i // cols
            col = i % cols
            x = monitor_principal['x_offset'] + margin + col * (width + margin)
            y = monitor_principal['y_offset'] + margin + row * (height + margin)
            positions.append((width, height, x, y))

        # Restante no monitor secundário
        remaining = num_sessions - 9

        # Ajustar a grade com base na orientação do monitor secundário
        if monitor_secundario['orientation'] == "Retrato":
            rows_s = max(2, math.ceil(math.sqrt(remaining) * 2))
            cols_s = math.ceil(remaining / rows_s)
        else:
            rows_s = math.ceil(math.sqrt(remaining))
            cols_s = math.ceil(remaining / rows_s)

        width = (monitor_secundario['width'] - (cols_s+1)*margin) // cols_s
        height = (monitor_secundario['height'] - (rows_s+1)*margin) // rows_s

        for i in range(remaining):
            row = i // cols_s
            col = i % cols_s
            x = monitor_secundario['x_offset'] + margin + col * (width + margin)
            y = monitor_secundario['y_offset'] + margin + row * (height + margin)
            positions.append((width, height, x, y))

    return positions

def launch_sessions(url, num_sessions, auto_close, incognito, auto_arrange):
    global drivers, driver_urls, stop_monitor
    stop_monitor = False

    if not url:
        messagebox.showerror("Erro", "Por favor, insira uma URL válida")
        return

    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    # Limpar sessões anteriores
    close_sessions()
    drivers.clear()
    driver_urls.clear()

    # Calcular posições
    positions = calculate_positions(num_sessions, auto_arrange)

    # Atualizar status
    status_var.set(f"Iniciando {num_sessions} sessões...")
    root.update()

    # Preparar o serviço Chrome uma única vez para reuso
    service = Service(ChromeDriverManager().install())

    # Iniciar sessões com ThreadPoolExecutor para máxima velocidade
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_sessions) as executor:
        batch_size = min(5, num_sessions)  # Processar em lotes de 5 para evitar sobrecarga

        for i in range(0, num_sessions, batch_size):
            batch_positions = positions[i:i+batch_size]

            # Iniciar este lote em paralelo
            batch_futures = []
            for pos in batch_positions:
                future = executor.submit(open_session, url, pos, incognito, service)
                batch_futures.append(future)

            # Coletar resultados deste lote
            for future in concurrent.futures.as_completed(batch_futures):
                driver = future.result()
                if driver:
                    drivers.append(driver)
                    # Armazenar a URL inicial
                    driver_urls[driver] = driver.current_url

            # Pequena pausa entre lotes
            if i + batch_size < num_sessions:
                time.sleep(0.2)

    status_var.set(f"{len(drivers)} sessões ativas")

    # Iniciar monitoramento
    if auto_close:
        threading.Thread(target=monitor_refresh, daemon=True).start()

def monitor_refresh():
    global drivers, driver_urls, stop_monitor

    while not stop_monitor:
        time.sleep(1)

        if stop_monitor:
            break

        active_drivers = []
        url_changed = False
        changed_driver = None

        # Primeiro, verificar se há alguma mudança de URL
        for driver in drivers:
            try:
                current_url = driver.current_url
                # Se o driver existe no dicionário e a URL mudou
                if driver in driver_urls and driver_urls[driver] != current_url:
                    # Verificar se é apenas um reload ou uma mudança para outro site
                    base_url_old = driver_urls[driver].split('://')[1].split('/')[0] if '://' in driver_urls[driver] else ""
                    base_url_new = current_url.split('://')[1].split('/')[0] if '://' in current_url else ""

                    # Se o domínio mudou, considerar como mudança de URL
                    if base_url_old != base_url_new:
                        url_changed = True
                        changed_driver = driver
                        status_var.set(f"URL alterada: {current_url}")
                        # Atualizar a URL no dicionário
                        driver_urls[driver] = current_url
                        break  # Encontramos uma mudança significativa, interromper a verificação

                # Atualizar URL atual em todos os casos
                driver_urls[driver] = current_url
                active_drivers.append(driver)
            except:
                try:
                    driver.quit()
                except:
                    pass

        # Se uma URL mudou significativamente
        if url_changed and changed_driver:
            # Maximizar a janela que mudou
            try:
                maximize_window_on_primary(changed_driver)

                # Se auto_close estiver ativado, fecha as outras janelas
                if auto_close_var.get():
                    for driver in drivers:
                        if driver != changed_driver:
                            try:
                                driver.quit()
                            except:
                                pass
                    # Manter apenas o driver que mudou
                    drivers = [changed_driver]
                    active_drivers = [changed_driver]
            except Exception as e:
                print(f"Erro ao maximizar janela: {e}")

        # Atualizar a lista de drivers ativos
        drivers.clear()
        drivers.extend(active_drivers)

        status_var.set(f"{len(drivers)} sessões ativas")
        root.update_idletasks()

        if not active_drivers:
            status_var.set("Todas as sessões foram fechadas")
            stop_monitor = True
            break

def close_sessions():
    global drivers, driver_urls, stop_monitor
    stop_monitor = True

    if drivers:
        for driver in drivers:
            try:
                driver.quit()
            except:
                pass

        drivers.clear()
        driver_urls.clear()

    status_var.set("Todas as sessões foram fechadas")

def draw_grid(canvas, num_sessions, width, height, auto_arrange):
    canvas.delete("all")
    theme = THEMES[current_theme]

    if num_sessions <= 0:
        canvas.create_text(width/2, height/2, text="Insira o número de sessões", fill=theme['fg'])
        return

    if not auto_arrange:
        canvas.create_text(width/2, height/2,
                         text=f"{num_sessions} janelas serão abertas\nsem organização automática",
                         fill=theme['fg'], justify=tk.CENTER)
        return

    # Detectar monitores para a prévia e aplicar orientações selecionadas
    monitors = get_screen_info()

    # Aplicar orientações selecionadas pelo usuário
    for i, monitor in enumerate(monitors):
        monitor_id = monitor['id']
        if monitor_id in monitor_orientations:
            monitors[i]['orientation'] = monitor_orientations[monitor_id]

            # Ajustar dimensões se a orientação for diferente da padrão
            if monitor['orientation'] != monitor['default_orientation']:
                monitors[i]['width'], monitors[i]['height'] = monitors[i]['height'], monitors[i]['width']

    # Se temos múltiplos monitores, garantir que renderizamos todos
    if len(monitors) > 1:
        # Determinar dimensões totais considerando todos os monitores
        min_x = min([m['x_offset'] for m in monitors])
        min_y = min([m['y_offset'] for m in monitors])
        max_x = max([m['x_offset'] + m['width'] for m in monitors])
        max_y = max([m['y_offset'] + m['height'] for m in monitors])

        total_width = max_x - min_x
        total_height = max_y - min_y

        # Calcular escala para visualização
        scale_x = width / total_width
        scale_y = (height - 30) / total_height
        scale = min(scale_x, scale_y) * 0.9  # Ligeira redução para garantir espaço

        # Calcular deslocamento para centralizar
        offset_x = (width - (total_width * scale)) / 2
        offset_y = 30  # Espaço para os rótulos dos monitores

        # Desenhar cada monitor
        for i, monitor in enumerate(monitors):
            # Ajustar coordenadas relativas ao canto superior esquerdo
            mon_x = offset_x + (monitor['x_offset'] - min_x) * scale
            mon_y = offset_y + (monitor['y_offset'] - min_y) * scale
            mon_w = monitor['width'] * scale
            mon_h = monitor['height'] * scale

            # Desenhar contorno do monitor
            canvas.create_rectangle(mon_x, mon_y, mon_x + mon_w, mon_y + mon_h,
                                outline=theme['monitor_outline'], fill=theme['monitor_fill'])

            # Rótulo do monitor
            label = f"Monitor {monitor['id']}" + (" (Principal)" if monitor['is_primary'] else "")
            canvas.create_text(mon_x + mon_w/2, mon_y - 15, text=label, fill=theme['fg'])

        # Desenhar posições das janelas
        positions = calculate_positions(num_sessions, auto_arrange)

        for i, (w, h, x, y) in enumerate(positions):
            # Ajustar coordenadas conforme a mesma escala dos monitores
            win_x = offset_x + (x - min_x) * scale
            win_y = offset_y + (y - min_y) * scale
            win_w = w * scale
            win_h = h * scale

            canvas.create_rectangle(win_x, win_y, win_x + win_w, win_y + win_h,
                                outline=theme['grid_outline'], fill=theme['grid_fill'])
            canvas.create_text(win_x + win_w/2, win_y + win_h/2, text=f"{i+1}", fill=theme['fg'])

        # Adicionar legenda explicativa quando há mais de 9 sessões
        if num_sessions > 9:
            canvas.create_text(width/2, height - 15,
                               text=f"Sessões 1-9 no Monitor Principal, 10-{num_sessions} no Monitor Secundário",
                               fill=theme['fg'], font=('Helvetica', 8))
    else:
        # Código original para um único monitor
        # ...resto do código para um monitor...
        total_width = monitors[0]['width']
        total_height = monitors[0]['height']

        scale_x = width / total_width
        scale_y = (height - 30) / total_height
        scale = min(scale_x, scale_y)

        # Desenhar monitor
        monitor = monitors[0]
        mon_x = (width - monitor['width'] * scale) / 2
        mon_y = 30
        mon_w = monitor['width'] * scale
        mon_h = monitor['height'] * scale

        canvas.create_rectangle(mon_x, mon_y, mon_x + mon_w, mon_y + mon_h,
                              outline=theme['monitor_outline'], fill=theme['monitor_fill'])
        canvas.create_text(mon_x + mon_w/2, mon_y - 15, text=f"Monitor {monitor['id']} (Principal)",
                          fill=theme['fg'])

        # Desenhar posições das janelas
        positions = calculate_positions(num_sessions, auto_arrange)
        for i, (w, h, x, y) in enumerate(positions):
            # Ajustar para centralizar no canvas
            win_x = mon_x + (x - monitor['x_offset']) * scale
            win_y = mon_y + (y - monitor['y_offset']) * scale
            win_w = w * scale
            win_h = h * scale

            canvas.create_rectangle(win_x, win_y, win_x + win_w, win_y + win_h,
                                 outline=theme['grid_outline'], fill=theme['grid_fill'])
            canvas.create_text(win_x + win_w/2, win_y + win_h/2, text=f"{i+1}", fill=theme['fg'])

def update_preview(event=None):
    try:
        num_sessions = int(num_entry.get()) if num_entry.get() else 0
        auto_arrange = auto_arrange_var.get()
        draw_grid(preview_canvas, num_sessions, 350, 250, auto_arrange)
    except ValueError:
        draw_grid(preview_canvas, 0, 350, 250, auto_arrange_var.get())

def update_monitor_orientation(monitor_id, orientation):
    """Atualiza a orientação de um monitor específico"""
    global monitor_orientations
    monitor_orientations[monitor_id] = orientation
    update_preview()

def refresh_monitor_settings():
    """Atualiza as configurações dos monitores na interface"""
    # Limpar frame de configurações
    for widget in monitor_settings_frame.winfo_children():
        widget.destroy()

    # Obter informações dos monitores
    monitors = get_screen_info()

    # Se tivermos mais de um monitor, mostrar o frame de configurações
    if len(monitors) > 1:
        monitor_settings_frame.pack(fill=tk.X, pady=10)

        # Título
        ttk.Label(
            monitor_settings_frame,
            text="Configuração de Monitores:",
            font=('Helvetica', 10, 'bold')
        ).pack(anchor=tk.W, pady=(0, 5))

        # Para cada monitor, criar uma linha com seu ID e combobox de orientação
        for monitor in monitors:
            monitor_frame = ttk.Frame(monitor_settings_frame)
            monitor_frame.pack(fill=tk.X, pady=2)

            # Label com ID do monitor
            ttk.Label(
                monitor_frame,
                text=f"Monitor {monitor['id']}" + (" (Principal)" if monitor['is_primary'] else "")
            ).pack(side=tk.LEFT, padx=(0, 10))

            # Combobox para orientação
            orientation_combo = ttk.Combobox(
                monitor_frame,
                values=["Paisagem", "Retrato"],
                width=10,
                state="readonly"
            )
            orientation_combo.pack(side=tk.LEFT)

            # Definir valor padrão
            current_orientation = monitor_orientations.get(
                monitor['id'],
                monitor['default_orientation']
            )
            orientation_combo.set(current_orientation)

            # Criar uma função de callback que captura o ID do monitor
            def make_callback(monitor_id):
                return lambda event: update_monitor_orientation(monitor_id, event.widget.get())

            # Associar callback
            orientation_combo.bind("<<ComboboxSelected>>", make_callback(monitor['id']))
    else:
        # Se tiver apenas um monitor, não mostrar as configurações
        monitor_settings_frame.pack_forget()

    # Atualizar a prévia
    update_preview()

def start():
    try:
        url = url_entry.get()
        num = int(num_entry.get()) if num_entry.get() else 0

        if num <= 0:
            messagebox.showerror("Erro", "O número de sessões deve ser maior que zero")
            return

        auto_close = auto_close_var.get()
        incognito = incognito_var.get()
        auto_arrange = auto_arrange_var.get()

        # Desativar botões temporariamente
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.DISABLED)

        # Iniciar em thread separada
        threading.Thread(
            target=lambda: launch_sessions(url, num, auto_close, incognito, auto_arrange),
            daemon=True
        ).start()

        # Reativar botões após um curto período
        root.after(1000, lambda: [
            start_button.config(state=tk.NORMAL),
            stop_button.config(state=tk.NORMAL)
        ])

    except ValueError:
        messagebox.showerror("Erro", "Por favor, insira um número válido de sessões")

def toggle_theme():
    global current_theme
    current_theme = 'dark' if current_theme == 'light' else 'light'
    apply_theme()
    update_preview()  # Atualizar a grid com as cores novas

def apply_theme():
    theme = THEMES[current_theme]

    # Atualizar cor da janela principal
    root.configure(bg=theme['bg'])

    # Atualizar estilos
    style.configure('TFrame', background=theme['bg'])
    style.configure('TLabel', background=theme['bg'], foreground=theme['fg'])
    style.configure('TCheckbutton', background=theme['bg'], foreground=theme['fg'])
    style.configure('TButton', background=theme['button'], foreground='white')
    style.map('TButton', background=[('active', theme['button_hover'])])

    # Configurar estilo para comboboxes
    style.configure('TCombobox', fieldbackground=theme['bg'], background=theme['bg'])
    style.map('TCombobox', fieldbackground=[('readonly', theme['bg'])])
    style.map('TCombobox', selectbackground=[('readonly', theme['accent'])])
    style.map('TCombobox', selectforeground=[('readonly', 'white')])

    # Atualizar canvas
    preview_canvas.configure(bg=theme['canvas_bg'])

    # Atualizar texto do botão de tema
    theme_button.config(text='Tema Claro' if current_theme == 'dark' else 'Tema Escuro')

def perform_safe_close():
    """Implementa um fechamento seguro para evitar que a interface trave"""
    global closing_in_progress, drivers, stop_monitor

    if closing_in_progress:
        return

    closing_in_progress = True
    status_var.set("Fechando o programa, aguarde...")
    root.update_idletasks()

    # Desabilitar todos os botões
    for widget in root.winfo_children():
        if isinstance(widget, ttk.Button):
            widget.config(state=tk.DISABLED)

    # Criar uma janela de progresso
    progress_window = tk.Toplevel(root)
    progress_window.title("Fechando")
    progress_window.geometry("300x100")
    progress_window.transient(root)
    progress_window.resizable(False, False)

    if current_theme == 'dark':
        progress_window.configure(bg=THEMES['dark']['bg'])

    # Centralizar a janela
    x = root.winfo_x() + (root.winfo_width() // 2) - 150
    y = root.winfo_y() + (root.winfo_height() // 2) - 50
    progress_window.geometry(f"+{x}+{y}")

    # Adicionar um label e uma barra de progresso
    ttk.Label(
        progress_window,
        text="Fechando as sessões do Chrome...",
        style='TLabel'
    ).pack(pady=10)

    progress = ttk.Progressbar(progress_window, mode="indeterminate")
    progress.pack(fill=tk.X, padx=20, pady=10)
    progress.start()

    # Executar o fechamento em uma thread
    def close_thread():
        global drivers, stop_monitor

        stop_monitor = True

        # Fechar cada driver com timeout
        for driver in list(drivers):
            try:
                driver.quit()
            except:
                pass

        drivers.clear()

        # Fechar janelas
        progress_window.destroy()
        root.destroy()

        # Forçar saída em caso de bloqueio
        try:
            sys.exit(0)
        except:
            pass

    # Iniciar thread de fechamento
    threading.Thread(target=close_thread, daemon=True).start()

    # Definir um timeout para forçar o fechamento se demorar muito
    root.after(3000, lambda: sys.exit(0))

# Configuração da interface
root = tk.Tk()
root.geometry('500x700')  # Aumentado para acomodar as configurações de monitor
root.title('Multi Chrome Tester')
root.protocol("WM_DELETE_WINDOW", perform_safe_close)

# Variáveis
auto_close_var = tk.BooleanVar(value=True)
incognito_var = tk.BooleanVar(value=False)
auto_arrange_var = tk.BooleanVar(value=True)
status_var = tk.StringVar(value="Pronto para iniciar")

# Estilo
style = ttk.Style(root)
style.theme_use('clam')

# Layout
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill=tk.BOTH, expand=True)

# URL
url_frame = ttk.Frame(main_frame)
url_frame.pack(fill=tk.X, pady=5)

ttk.Label(url_frame, text='URL do site:').pack(anchor=tk.W)
url_entry = ttk.Entry(url_frame, width=50)
url_entry.pack(fill=tk.X, pady=5)

# Sessões
num_frame = ttk.Frame(main_frame)
num_frame.pack(fill=tk.X, pady=5)

ttk.Label(num_frame, text='Número de sessões:').pack(anchor=tk.W)
num_entry = ttk.Entry(num_frame)
num_entry.pack(fill=tk.X, pady=5)
num_entry.bind('<KeyRelease>', update_preview)

# Opções
options_frame = ttk.Frame(main_frame)
options_frame.pack(fill=tk.X, pady=5)

ttk.Checkbutton(
    options_frame,
    text='Organizar janelas automaticamente',
    variable=auto_arrange_var,
    command=update_preview
).pack(anchor=tk.W, pady=2)

ttk.Checkbutton(
    options_frame,
    text='Fechar outras janelas quando uma recarregar',
    variable=auto_close_var
).pack(anchor=tk.W, pady=2)

ttk.Checkbutton(
    options_frame,
    text='Modo anônimo',
    variable=incognito_var
).pack(anchor=tk.W, pady=2)

# Botão de tema
theme_button = ttk.Button(options_frame, text="Tema Escuro", command=toggle_theme)
theme_button.pack(anchor=tk.W, pady=5)

# Botão para atualizar as configurações de monitor
refresh_button = ttk.Button(options_frame, text="Atualizar Monitores", command=refresh_monitor_settings)
refresh_button.pack(anchor=tk.W, pady=5)

# Frame para configurações de monitor
monitor_settings_frame = ttk.Frame(main_frame)
# Será exibido apenas se houver mais de um monitor

# Prévia
preview_frame = ttk.Frame(main_frame)
preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)

ttk.Label(preview_frame, text='Prévia da distribuição:').pack(anchor=tk.W)
preview_canvas = tk.Canvas(preview_frame, width=350, height=250, bg=THEMES['light']['canvas_bg'])
preview_canvas.pack(pady=5)

# Botões
button_frame = ttk.Frame(main_frame)
button_frame.pack(fill=tk.X, pady=10)

start_button = ttk.Button(button_frame, text='Iniciar Teste', command=start)
start_button.pack(side=tk.LEFT, padx=5)

stop_button = ttk.Button(button_frame, text='Fechar Todas', command=close_sessions)
stop_button.pack(side=tk.LEFT, padx=5)

# Status
status_frame = ttk.Frame(main_frame)
status_frame.pack(fill=tk.X, pady=5)

status_label = ttk.Label(status_frame, textvariable=status_var)
status_label.pack(anchor=tk.W)

# Aplicar tema inicial
apply_theme()

# Inicializar as configurações de monitor
refresh_monitor_settings()

# Inicializar a prévia
update_preview()

# Iniciar a interface
root.mainloop()