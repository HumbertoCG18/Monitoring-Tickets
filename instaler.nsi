; Script gerado pelo NSIS Script Wizard

!include "MUI2.nsh"

; Definições gerais
!define APPNAME "Multi Chrome Tester"
!define COMPANYNAME "Sua Empresa"
!define DESCRIPTION "Ferramenta para testar sites em múltiplas instâncias do Chrome"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://www.seusite.com/help"
!define UPDATEURL "https://www.seusite.com/update"
!define ABOUTURL "https://www.seusite.com/about"

; Nome do instalador
Name "${APPNAME}"
OutFile "MultiChromeTesterSetup.exe"

; Diretório de instalação padrão
InstallDir "$PROGRAMFILES\${APPNAME}"

; Solicitar privilégios de administrador
RequestExecutionLevel admin

; Interface
!define MUI_ABORTWARNING
!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"

; Páginas do instalador
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"  ; Você precisará criar este arquivo
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Páginas do desinstalador
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Idiomas
!insertmacro MUI_LANGUAGE "PortugueseBR"

; Seção principal de instalação
Section "Instalar" SecInstall
  SetOutPath "$INSTDIR"
  
  ; Arquivos a serem instalados
  File "dist\MultiChromeTester.exe"
  File "LICENSE.txt"
  File "README.txt"  ; Você precisará criar este arquivo
  
  ; Criar atalho no menu iniciar
  CreateDirectory "$SMPROGRAMS\${APPNAME}"
  CreateShortcut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\MultiChromeTester.exe"
  CreateShortcut "$SMPROGRAMS\${APPNAME}\Desinstalar.lnk" "$INSTDIR\uninstall.exe"
  
  ; Criar atalho na área de trabalho
  CreateShortcut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\MultiChromeTester.exe"
  
  ; Instalar o Chrome se não estiver instalado
  Call CheckAndInstallChrome
  
  ; Criar desinstalador
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  ; Informações no painel de controle
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$\"$INSTDIR\MultiChromeTester.exe$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "HelpLink" "${HELPURL}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
  
  ; Estimar o tamanho
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" "$0"
SectionEnd

; Função para verificar e instalar o Chrome
Function CheckAndInstallChrome
  ; Verificar se o Chrome está instalado
  ReadRegStr $0 HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" ""
  IfErrors 0 ChromeInstalled
    MessageBox MB_YESNO "O Google Chrome não parece estar instalado. Deseja baixá-lo agora?" IDNO ChromeInstalled
    ExecShell "open" "https://www.google.com/chrome/"
  ChromeInstalled:
FunctionEnd

; Seção de desinstalação
Section "Uninstall"
  ; Remover arquivos
  Delete "$INSTDIR\MultiChromeTester.exe"
  Delete "$INSTDIR\LICENSE.txt"
  Delete "$INSTDIR\README.txt"
  Delete "$INSTDIR\uninstall.exe"
  
  ; Remover atalhos
  Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
  Delete "$SMPROGRAMS\${APPNAME}\Desinstalar.lnk"
  Delete "$DESKTOP\${APPNAME}.lnk"
  
  ; Remover diretórios
  RMDir "$SMPROGRAMS\${APPNAME}"
  RMDir "$INSTDIR"
  
  ; Remover registro
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd