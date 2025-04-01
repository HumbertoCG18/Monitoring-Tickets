import os
import sys
import subprocess
import importlib
import pkg_resources

def print_colored(text, color):
    """Imprime texto colorido no console"""
    colors = {
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'blue': '\033[94m',
        'end': '\033[0m'
    }
    print(f"{colors.get(color, '')}{text}{colors['end']}")

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    min_version = (3, 6)
    current_version = sys.version_info[:2]

    if current_version < min_version:
        print_colored(f"Erro: Python {min_version[0]}.{min_version[1]} ou superior é necessário. Você está usando {current_version[0]}.{current_version[1]}", "red")
        return False
    return True

def install_package(package_name):
    """Instala um pacote usando pip"""
    print_colored(f"Instalando {package_name}...", "yellow")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print_colored(f"✓ {package_name} instalado com sucesso!", "green")
        return True
    except subprocess.CalledProcessError:
        print_colored(f"× Falha ao instalar {package_name}.", "red")
        return False

def check_and_install():
    """Verifica e instala as dependências necessárias"""
    # Lista de dependências
    dependencies = [
        ("selenium", "selenium"),
        ("webdriver_manager", "webdriver-manager"),
        ("screeninfo", "screeninfo"),
        ("tkinter", "tk")  # tkinter geralmente já vem com Python, mas verificamos por precaução
    ]

    # Verificar instalação pip
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"], stdout=subprocess.DEVNULL)
    except:
        print_colored("Pip não está instalado ou não está funcionando corretamente.", "red")
        if sys.platform.startswith('win'):
            print_colored("Tente instalar o pip usando: curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python get-pip.py", "yellow")
        else:
            print_colored("Tente instalar o pip usando: sudo apt-get install python3-pip (Linux) ou brew install python (macOS)", "yellow")
        return False

    # Verificar e instalar cada dependência
    all_installed = True
    installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}

    print_colored("\n=== Verificando dependências do Multi Chrome Tester ===\n", "blue")

    for module_name, package_name in dependencies:
        try:
            if module_name == "tkinter":
                # Tkinter é um caso especial
                importlib.import_module(module_name)
                print_colored(f"✓ {module_name} já está instalado.", "green")
            else:
                # Verificar se o pacote está instalado
                if package_name.lower() in installed_packages:
                    print_colored(f"✓ {package_name} já está instalado (versão {installed_packages[package_name.lower()]}).", "green")
                else:
                    success = install_package(package_name)
                    if not success:
                        all_installed = False
        except ImportError:
            success = install_package(package_name)
            if not success:
                all_installed = False

    # Chrome driver e Chrome navegador verificação
    print_colored("\n=== Verificando Chrome ===\n", "blue")
    chrome_paths = []

    if sys.platform.startswith('win'):
        chrome_paths = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe")
        ]
    elif sys.platform.startswith('darwin'):  # macOS
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        ]
    else:  # Linux
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable"
        ]

    chrome_installed = any(os.path.exists(path) for path in chrome_paths)

    if chrome_installed:
        print_colored("✓ Google Chrome está instalado.", "green")
    else:
        print_colored("× Google Chrome não foi encontrado no caminho padrão.", "red")
        print_colored("  Por favor, instale o Google Chrome: https://www.google.com/chrome/", "yellow")
        all_installed = False

    return all_installed

def main():
    """Função principal"""
    banner = """
 __  __       _ _   _    _____ _                            _____         _
|  \/  |     | | | (_)  / ____| |                          |_   _|       | |
| \  / |_   _| | |_ _  | |    | |__  _ __ ___  _ __ ___   ___| | ___  ___| |_ ___ _ __
| |\/| | | | | | __| | | |    | '_ \| '__/ _ \| '_ ` _ \ / _ \ |/ _ \/ __| __/ _ \ '__|
| |  | | |_| | | |_| | | |____| | | | | | (_) | | | | | |  __/ |  __/\__ \ ||  __/ |
|_|  |_|\__,_|_|\__|_|  \_____|_| |_|_|  \___/|_| |_| |_|\___|_|\___||___/\__\___|_|

    """
    print_colored(banner, "blue")
    print_colored("Verificador e Instalador de Dependências", "blue")
    print_colored("==========================================\n", "blue")

    if not check_python_version():
        return

    success = check_and_install()

    if success:
        print_colored("\n✓ Todas as dependências foram instaladas com sucesso!", "green")
        print_colored("  Você pode agora executar o Multi Chrome Tester sem problemas.", "green")
    else:
        print_colored("\n× Algumas dependências não puderam ser instaladas automaticamente.", "red")
        print_colored("  Revise as mensagens acima e tente instalar manualmente as dependências faltantes.", "yellow")

if __name__ == "__main__":
    main()