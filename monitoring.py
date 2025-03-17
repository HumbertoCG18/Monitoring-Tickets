import tkinter as tk
from tkinter import ttk
import threading
import math
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Variáveis globais para armazenar os drivers e os tempos iniciais de carregamento
drivers = []
stop_monitor = False

# Obtenha resolução das telas (ajuste conforme seus monitores)
MONITOR_PRINCIPAL = {'width': 1920, 'height': 1080, 'x_offset': 0, 'y_offset': 0}
MONITOR_VERTICAL = {'width': 1080, 'height': 1920, 'x_offset': 1920, 'y_offset': 0}


def open_session(url, position, incognito):
    chrome_options = Options()
    chrome_options.add_argument(f"--window-size={position[0]},{position[1]}")
    chrome_options.add_argument(f"--window-position={position[2]},{position[3]}")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    if incognito:
        chrome_options.add_argument('--incognito')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    return driver


def launch_sessions(url, num_sessions, auto_close, incognito):
    global drivers, stop_monitor
    stop_monitor = False

    drivers.clear()
    positions = []

    for i in range(num_sessions):
        if i < 9:
            cols = 3
            width = MONITOR_PRINCIPAL['width'] // 3
            height = MONITOR_PRINCIPAL['height'] // 3
            x = MONITOR_PRINCIPAL['x_offset'] + (i % cols) * width
            y = MONITOR_PRINCIPAL['y_offset'] + (i // cols) * height
        else:
            width = MONITOR_VERTICAL['width']
            height = MONITOR_VERTICAL['height'] // (num_sessions - 9)
            x = MONITOR_VERTICAL['x_offset']
            y = MONITOR_VERTICAL['y_offset'] + (i - 9) * height
        positions.append((width, height, x, y))

    with ThreadPoolExecutor(max_workers=num_sessions) as executor:
        drivers.extend(executor.map(lambda pos: open_session(url, pos, incognito), positions))

    if auto_close:
        root.after(1000, monitor_refresh)


def monitor_refresh():
    global stop_monitor
    if stop_monitor:
        return

    active_drivers = []
    for driver in drivers:
        try:
            driver.title
            active_drivers.append(driver)
        except:
            continue

    if not active_drivers:
        root.quit()
        return

    root.after(1000, monitor_refresh)


def draw_grid(canvas, num_sessions, width, height):
    canvas.delete("all")
    if num_sessions <= 9:
        rows = cols = math.ceil(math.sqrt(num_sessions))
        cell_width = width / cols
        cell_height = height / rows
        for i in range(num_sessions):
            row = i // cols
            col = i % cols
            x0 = col * cell_width
            y0 = row * cell_height
            x1 = x0 + cell_width
            y1 = y0 + cell_height
            canvas.create_rectangle(x0, y0, x1, y1, outline="black", fill="lightgrey")
    else:
        for monitor, sessions in [("Monitor 1", 9), ("Monitor 2", num_sessions - 9)]:
            rows = cols = math.ceil(math.sqrt(sessions))
            cell_width = width / cols
            cell_height = height / rows
            y_offset = 0 if monitor == "Monitor 1" else height + 10
            canvas.create_text(width / 2, y_offset - 10, text=monitor)
            for i in range(sessions):
                row = i // cols
                col = i % cols
                x0 = col * cell_width
                y0 = y_offset + row * cell_height
                x1 = x0 + cell_width
                y1 = y0 + cell_height
                canvas.create_rectangle(x0, y0, x1, y1, outline="black", fill="lightgrey")


def update_preview(event=None):
    try:
        num_sessions = int(num_entry.get())
        draw_grid(preview_canvas, num_sessions, 350, 150)
    except:
        pass


def start():
    url = url_entry.get()
    num = int(num_entry.get())
    auto_close = auto_close_var.get()
    incognito = incognito_var.get()
    launch_sessions(url, num, auto_close, incognito)


def close_all():
    global stop_monitor
    stop_monitor = True
    threading.Thread(target=lambda: [driver.quit() for driver in drivers], daemon=True).start()
    root.destroy()


root = tk.Tk()
root.geometry('400x450')
root.title('Multi Chrome Tester')

style = ttk.Style(root)
style.theme_use('clam')

tk.Label(root, text='URL:').pack()
url_entry = tk.Entry(root, width=50)
url_entry.pack()

tk.Label(root, text='Sessões:').pack()
num_entry = tk.Entry(root)
num_entry.pack()
num_entry.bind('<KeyRelease>', update_preview)

auto_close_var = tk.BooleanVar()
incognito_var = tk.BooleanVar()

tk.Checkbutton(root, text='Fechar ao recarregar', variable=auto_close_var).pack()
tk.Checkbutton(root, text='Modo anônimo', variable=incognito_var).pack()

preview_canvas = tk.Canvas(root, width=350, height=320)
preview_canvas.pack(pady=10)

tk.Button(root, text='Iniciar', command=start).pack(pady=10)

root.protocol("WM_DELETE_WINDOW", close_all)
root.bind_all('<Alt-F4>', lambda event: close_all())

root.mainloop()
