import sys
import os
import subprocess
import pkg_resources

def main():
    print("=== Preparando para empacotar o Multi Chrome Tester ===")

    # Verificar se PyInstaller está instalado
    try:
        pkg_resources.get_distribution("pyinstaller")
        print("PyInstaller já está instalado.")
    except pkg_resources.DistributionNotFound:
        print("Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Instalar outras dependências necessárias
    print("Instalando dependências...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium", "webdriver-manager"])

    # Criar arquivo spec básico se não existir
    if not os.path.exists("multi_chrome_tester.spec"):
        print("Criando arquivo spec básico...")
        with open("multi_chrome_tester.spec", "w") as f:
            f.write("""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['multi_chrome_tester.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['selenium', 'webdriver_manager', 'webdriver_manager.chrome'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MultiChromeTester',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
""")

    # Empacotar o aplicativo usando PyInstaller via módulo Python
    print("Empacotando o aplicativo...")
    import PyInstaller.__main__

    PyInstaller.__main__.run([
        'multi_chrome_tester.spec',
        '--noconfirm'
    ])

    print("\n=== Empacotamento concluído com sucesso! ===")
    print("O executável está disponível em: dist/MultiChromeTester.exe")

if __name__ == "__main__":
    main()