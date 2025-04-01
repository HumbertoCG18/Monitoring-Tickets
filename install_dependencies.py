import os
import sys
import subprocess
import importlib

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

def is_package_installed(package_name):
    """Verifica se um pacote está instalado"""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def get_package_version(package_name):
    """Obtém a versão de um pacote instalado"""
    try:
        return importlib.import_module(package_name).__version__
    except (ImportError, AttributeError):
        try:
            # Tenta obter versão usando pip
            result = subprocess.check_output([sys.executable, '-m', 'pip', 'show', package_name])
            for line in result.decode('utf-8').split('\n'):
                if line.startswith('Version:'):
                    return line.split(':')[1].strip()
        except:
            pass
    return "Desconhecida"

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
        ("tkinter", "")  # tkinter geralmente já vem com Python, não precisa instalar via pip
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
    print_colored("\n=== Verificando dependências do Multi Chrome Tester ===\n", "blue")

    for module_name, package_name in dependencies:
        try:
            # Tratamento especial para tkinter
            if module_name == "tkinter":
                try:
                    importlib.import_module(module_name)
                    print_colored(f"✓ {module_name} já está instalado.", "green")
                except ImportError:
                    print_colored(f"× {module_name} não está instalado. Ele vem com a instalação padrão do Python.", "red")
                    print_colored("  Talvez você precise reinstalar o Python ou instalar o pacote 'tk' pelo gerenciador de pacotes do seu sistema.", "yellow")
                    all_installed = False
            else:
                # Verificar se o pacote está instalado
                if is_package_installed(module_name):
                    version = get_package_version(module_name)
                    print_colored(f"✓ {package_name} já está instalado (versão {version}).", "green")
                else:
                    success = install_package(package_name)
                    if not success:
                        all_installed = False
        except Exception as e:
            print_colored(f"× Erro ao verificar {module_name}: {str(e)}", "red")
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