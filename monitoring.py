import tkinter as tk
from tkinter import ttk
import time
import math
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Variáveis globais para armazenar os drivers e os tempos iniciais de carregamento
drivers = []
initial_navstart = {}
stop_monitor = False  # Flag para parar o monitoramento

def open_session(i, url, auto_arrange, window_width, window_height, cols):
    """Abre uma sessão do Chrome e retorna o driver e o timestamp de navegação."""
    chrome_options = Options()
    # Estratégias para reduzir a detecção de automação (para minimizar o captcha)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    if auto_arrange:
        row = i // cols
        col = i % cols
        x = col * window_width
        y = row * window_height
        chrome_options.add_argument(f"--window-size={window_width},{window_height}")
        chrome_options.add_argument(f"--window-position={x},{y}")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    try:
        nav_start = driver.execute_script("return window.performance.timing.navigationStart")
    except Exception:
        nav_start = None
    return driver, nav_start

def launch_sessions(url, num_sessions, auto_arrange, auto_close):
    global drivers, initial_navstart, stop_monitor
    stop_monitor = False
    drivers.clear()
    initial_navstart.clear()
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    if auto_arrange:
        rows = math.ceil(math.sqrt(num_sessions))
        cols = math.ceil(num_sessions / rows)
        window_width = int(screen_width / cols)
        window_height = int(screen_height / rows)
    else:
        window_width = window_height = cols = None
    
    # Abre as sessões em paralelo para acelerar o processo
    with ThreadPoolExecutor(max_workers=num_sessions) as executor:
        futures = []
        for i in range(num_sessions):
            futures.append(executor.submit(open_session, i, url, auto_arrange, window_width, window_height, cols if cols else 0))
        for future in futures:
            try:
                driver, nav_start = future.result()
                drivers.append(driver)
                initial_navstart[driver] = nav_start
            except Exception as e:
                print("Erro ao abrir uma sessão:", e)
    
    if auto_close:
        root.after(1000, monitor_refresh)

def monitor_refresh():
    """Monitora as janelas e fecha as que foram recarregadas. Se todas as janelas forem fechadas manualmente, encerra a GUI."""
    global drivers, initial_navstart, stop_monitor
    if stop_monitor:
        return
    
    # Verifica se alguma janela foi fechada manualmente e remove o driver correspondente
    for driver in drivers.copy():
        try:
            _ = driver.title
        except Exception:
            drivers.remove(driver)
    
    if not drivers:
        stop_monitor = True
        root.quit()  # Encerra a GUI se não houver mais janelas abertas
        return

    for driver in drivers.copy():
        try:
            current_navstart = driver.execute_script("return window.performance.timing.navigationStart")
        except Exception:
            drivers.remove(driver)
            continue
        if initial_navstart.get(driver) is not None and current_navstart != initial_navstart[driver]:
            # Se a página foi recarregada, fecha todas as janelas, exceto a atual
            for d in drivers.copy():
                if d != driver:
                    try:
                        d.quit()
                    except Exception:
                        pass
                    drivers.remove(d)
            initial_navstart[driver] = current_navstart
            break
    
    root.after(1000, monitor_refresh)

def start_button_clicked():
    """Função chamada quando o botão 'Iniciar' é pressionado."""
    url = url_entry.get()
    try:
        num_sessions = int(sessions_entry.get())
    except ValueError:
        print("Número de sessões inválido!")
        return
    auto_arrange = auto_arrange_var.get()
    auto_close = auto_close_var.get()
    launch_sessions(url, num_sessions, auto_arrange, auto_close)

def on_closing():
    """Encerra todas as instâncias do Chrome e finaliza a aplicação."""
    global stop_monitor
    stop_monitor = True
    for driver in drivers.copy():
        try:
            driver.quit()
        except Exception:
            pass
    root.destroy()

def on_alt_f4(event):
    """Captura o atalho ALT+F4 para fechar a aplicação."""
    on_closing()

# --- Criação da GUI com Tkinter ---
root = tk.Tk()
root.title("Testador de Sessões - Chrome")
root.geometry("400x250")

# Vincula o atalho ALT+F4 à função de fechamento
root.bind_all("<Alt-F4>", on_alt_f4)

style = ttk.Style(root)
style.theme_use('clam')

tk.Label(root, text="URL do site:").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(padx=10)

tk.Label(root, text="Número de sessões:").pack(pady=5)
sessions_entry = tk.Entry(root, width=10)
sessions_entry.pack(padx=10)

auto_arrange_var = tk.BooleanVar()
auto_close_var = tk.BooleanVar()

cb1 = tk.Checkbutton(root, text="Auto-arranjar janelas (window manager)", variable=auto_arrange_var)
cb1.pack(anchor="w", padx=10, pady=5)

cb2 = tk.Checkbutton(root, text="Fechar janelas ao recarregar", variable=auto_close_var)
cb2.pack(anchor="w", padx=10)

start_button = tk.Button(root, text="Iniciar", command=start_button_clicked)
start_button.pack(pady=15)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
