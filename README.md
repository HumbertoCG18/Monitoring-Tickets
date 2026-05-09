# Monitoring Tickets / Multi Chrome Tester

![GitHub repo size](https://img.shields.io/github/repo-size/HumbertoCG18/Monitoring-Tickets)
![GitHub stars](https://img.shields.io/github/stars/HumbertoCG18/Monitoring-Tickets?style=social)
![GitHub forks](https://img.shields.io/github/forks/HumbertoCG18/Monitoring-Tickets?style=social)
![GitHub license](https://img.shields.io/github/license/HumbertoCG18/Monitoring-Tickets)

Aplicação desktop desenvolvida em Python para abrir, organizar e monitorar múltiplas sessões do Google Chrome simultaneamente.

O projeto foi pensado para cenários em que é necessário testar ou acompanhar várias instâncias de uma mesma página web ao mesmo tempo, como validação de sistemas, testes de comportamento em múltiplas sessões, monitoramento de tickets, painéis internos, fluxos web e simulações de acesso concorrente.

---

## 📌 Sobre o projeto

O **Monitoring Tickets / Multi Chrome Tester** é uma ferramenta com interface gráfica que permite ao usuário informar uma URL, definir o número de sessões desejadas e abrir várias janelas do Chrome automaticamente.

A aplicação também oferece recursos para organização visual das janelas, suporte a múltiplos monitores, modo anônimo, tema claro/escuro e fechamento automático de sessões quando uma janela muda de URL.

---

## ✨ Funcionalidades

- Abertura automática de múltiplas sessões do Google Chrome.
- Interface gráfica simples e intuitiva com Tkinter.
- Organização automática das janelas na tela.
- Suporte a múltiplos monitores.
- Configuração de orientação dos monitores: paisagem ou retrato.
- Pré-visualização da distribuição das janelas antes da execução.
- Modo anônimo opcional.
- Tema claro e tema escuro.
- Monitoramento de mudança de URL.
- Fechamento automático das demais janelas quando uma sessão muda de domínio.
- Encerramento seguro das sessões abertas.
- Script auxiliar para verificação e instalação de dependências.
- Suporte a empacotamento por instalador.

---

## 🖥️ Demonstração de uso

Fluxo básico da aplicação:

1. Informe a URL que deseja abrir.
2. Defina a quantidade de sessões.
3. Escolha as opções desejadas:
   - organizar janelas automaticamente;
   - abrir em modo anônimo;
   - fechar outras janelas quando uma sessão mudar de URL.
4. Confira a prévia da distribuição.
5. Clique em **Iniciar Teste**.
6. Para encerrar, clique em **Fechar Todas**.

---

## 🧰 Tecnologias utilizadas

- **Python**
- **Tkinter** — interface gráfica.
- **Selenium** — automação do Google Chrome.
- **WebDriver Manager** — gerenciamento automático do ChromeDriver.
- **ScreenInfo** — detecção de monitores e resolução.
- **Threading / Concurrent Futures** — execução paralela das sessões.
- **NSIS** — criação de instalador para Windows.

---

## 📁 Estrutura do repositório

```txt
Monitoring-Tickets/
├── build/
├── dist/
├── .gitattributes
├── LICENSE.txt
├── MultiChromeTesterSetup.exe
├── chromedriver-win64.zip
├── icon.ico
├── install_dependencies.py
├── installer.nsi
└── multi_chrome_tester.py
