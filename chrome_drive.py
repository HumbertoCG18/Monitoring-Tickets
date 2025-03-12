import requests
import zipfile
import io
import platform

# URL do endpoint do Chrome for Testing (CfT)
endpoint = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions.json"

# Requisição para obter os dados JSON
response = requests.get(endpoint)
response.raise_for_status()  # Garante que a requisição foi bem-sucedida
data = response.json()

# Tenta obter a URL do ChromeDriver do canal Stable
try:
    stable = data["channels"]["Stable"]
    chromedriver_url = stable["downloads"]["chromedriver"]["url"]
    version = stable["version"]
except Exception as e:
    # Caso não encontre no canal Stable, identifica pelo sistema operacional
    sys_platform = platform.system().lower()
    if "windows" in sys_platform:
        current_platform = "win64"
    elif "linux" in sys_platform:
        current_platform = "linux64"
    elif "darwin" in sys_platform or "mac" in sys_platform:
        current_platform = "mac64"
    else:
        raise Exception("Sistema operacional não suportado.")

    chromedriver_url = None
    version = None
    for ver in data.get("versions", []):
        try:
            platforms = ver["platforms"]
            if current_platform in platforms:
                chromedriver_url = platforms[current_platform]["chromedriver"]["url"]
                version = ver["version"]
                break
        except Exception:
            continue
    if chromedriver_url is None:
        raise Exception("Não foi possível encontrar a URL do ChromeDriver para o seu sistema.")

print(f"Baixando ChromeDriver versão {version} para {current_platform} a partir de:")
print(chromedriver_url)

# Faz o download do arquivo ZIP do ChromeDriver
r = requests.get(chromedriver_url)
r.raise_for_status()

# Extrai o conteúdo do ZIP para o diretório 'chromedriver_extracted'
with zipfile.ZipFile(io.BytesIO(r.content)) as z:
    z.extractall("chromedriver_extracted")

print("ChromeDriver extraído para o diretório 'chromedriver_extracted'.")
