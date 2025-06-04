; Script de instalação avançado para Multi Chrome Tester
!include "MUI2.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"

; Definições básicas
!define APPNAME "MultiChromeTester"
!define VERSION "1.0"
!define PUBLISHER "Seu Nome"

; Configurações gerais
Name "${APPNAME}"
OutFile "MultiChromeTesterSetup.exe"
InstallDir "$PROGRAMFILES\${APPNAME}"
RequestExecutionLevel admin

; Ícone do instalador/desinstalador
!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"

; Imagens personalizadas - será usado o ícone como imagem também
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "icon.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "icon.ico"

; Páginas do instalador
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "license.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_COMPONENTS ; Página de seleção de componentes
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Páginas do desinstalador
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Idioma
!insertmacro MUI_LANGUAGE "PortugueseBR"

; Proteção contra múltiplas instâncias
Function .onInit
  System::Call 'kernel32::CreateMutexA(i 0, i 0, t "MultiChromeTesterInstaller") i .r1 ?e'
  Pop $R0
  ${If} $R0 != 0
    MessageBox MB_OK|MB_ICONEXCLAMATION "O instalador ja esta sendo executado."
    Abort
  ${EndIf}
FunctionEnd

; Instalar arquivos principais
Section "Multi Chrome Tester (obrigatorio)" SecMain
  SectionIn RO ; Seção obrigatória (RO = Read-Only)
  
  SetOutPath "$INSTDIR"
  
  ; Arquivos principais
  File /nonfatal "dist\MultiChromeTester.exe"
  File /nonfatal "icon.ico"
  File /nonfatal "license.txt"
  
  ; Criar desinstalador
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  ; Registrar aplicativo
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$\"$INSTDIR\icon.ico$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${PUBLISHER}"
  
  ; Calcular e armazenar o tamanho da instalação
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" "$0"
SectionEnd

; Instalar dependências (opcional)
Section "Dependencias Python" SecDeps
  SetOutPath "$INSTDIR"
  File /nonfatal "install_dependencies.py"
  
  DetailPrint "Instalando dependencias Python..."
  nsExec::ExecToStack 'python "$INSTDIR\install_dependencies.py"'
  Pop $0 ; Código de retorno
  Pop $1 ; Saída do comando
  DetailPrint "Resultado: $1"
SectionEnd

; Criar atalhos (opcional)
Section "Atalhos de Acesso" SecShortcuts
  CreateDirectory "$SMPROGRAMS\${APPNAME}"
  CreateShortcut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\MultiChromeTester.exe" "" "$INSTDIR\icon.ico"
  CreateShortcut "$SMPROGRAMS\${APPNAME}\Desinstalar.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\icon.ico"
  CreateShortcut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\MultiChromeTester.exe" "" "$INSTDIR\icon.ico"
SectionEnd

; Iniciar com o Windows (opcional)
Section "Iniciar com Windows" SecStartup
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "${APPNAME}" "$\"$INSTDIR\MultiChromeTester.exe$\""
SectionEnd

; Descrições das seções
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecMain} "Arquivos principais do programa (obrigatorio)."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecDeps} "Instala automaticamente todas as dependencias Python necessarias."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecShortcuts} "Cria atalhos no menu Iniciar e na area de trabalho."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecStartup} "Startup on Windows."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Desinstalação
Section "Uninstall"
  ; Remover arquivos
  Delete "$INSTDIR\MultiChromeTester.exe"
  Delete "$INSTDIR\install_dependencies.py"
  Delete "$INSTDIR\icon.ico"
  Delete "$INSTDIR\license.txt"
  Delete "$INSTDIR\uninstall.exe"
  
  ; Remover atalhos
  Delete "$DESKTOP\${APPNAME}.lnk"
  Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
  Delete "$SMPROGRAMS\${APPNAME}\Desinstalar.lnk"
  RMDir "$SMPROGRAMS\${APPNAME}"
  
  ; Remover registro de inicialização com Windows
  DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "${APPNAME}"
  
  ; Remover registro de desinstalação
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
  
  ; Remover diretório de instalação
  RMDir "$INSTDIR"
SectionEnd