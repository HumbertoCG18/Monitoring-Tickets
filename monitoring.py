import time
import requests
import logging
import os
from datetime import datetime
import pytz
import json
import smtplib
from email.mime.text import MIMEText
import signal
import sys

def configurar_logger():
    if not os.path.exists('Logs'):
        os.makedirs('Logs')
    logging.basicConfig(
        filename='Logs/monitoramento.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def menu_principal():
    print("===== Configuração do Monitor de Ingressos =====")
    email = input("Insira seu email para notificações: ")
    evento = input("Insira o nome do artista ou evento a ser monitorado: ")
    intervalo_input = input("Intervalo de verificação em segundos (padrão 300): ") or 300
    try:
        intervalo_atualizacao = int(intervalo_input)
        if intervalo_atualizacao <= 0:
            raise ValueError
    except ValueError:
        print("Intervalo inválido. Usando o valor padrão de 300 segundos.")
        intervalo_atualizacao = 300
    return {
        'email': email,
        'evento': evento,
        'intervalo_atualizacao': intervalo_atualizacao
    }

def converter_data_para_brasilia(data_iso):
    tz = pytz.timezone('America/Sao_Paulo')
    data_utc = datetime.strptime(data_iso, "%Y-%m-%dT%H:%M:%SZ")
    data_local = data_utc.astimezone(tz)
    return data_local.strftime("%d/%m/%Y %H:%M:%S")

def verificar_disponibilidade(evento):
    base_url = "https://app.ticketmaster.com/discovery/v2/events.json"
    api_key = os.getenv("TICKETMASTER_API_KEY")
    params = {
        'keyword': evento,
        'countryCode': 'BR',
        'apikey': api_key
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao acessar a API do Ticketmaster: {e}")
        print(f"Erro ao acessar a API do Ticketmaster: {e}")
        return None
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        logging.error(f"Erro ao decodificar JSON: {e}")
        print(f"Erro ao decodificar JSON: {e}")
        return None
    try:
        events = data.get('_embedded', {}).get('events', [])
        if not events:
            logging.info("Nenhum evento encontrado.")
            return None
        for event in events:
            if event['name'].lower() == evento.lower():
                event_name = event['name']
                event_date = event['dates']['start']['dateTime']
                venue = event['_embedded']['venues'][0]['name']
                city = event['_embedded']['venues'][0]['city']['name']
                country = event['_embedded']['venues'][0]['country']['name']
                url = event['url']
                status = event['dates']['status']['code']
                esgotado = status != 'onsale'
                event_date_str = converter_data_para_brasilia(event_date)
                return {
                    'nome_evento': event_name,
                    'data_evento': event_date_str,
                    'local': f"{venue}, {city}, {country}",
                    'esgotado': esgotado,
                    'url': url
                }
        logging.info("Evento específico não encontrado.")
        return None
    except Exception as e:
        logging.error(f"Erro ao processar os dados da API: {e}")
        print(f"Erro ao processar os dados da API: {e}")
        return None

def enviar_notificacao_email(config, info_evento):
    try:
        msg = MIMEText(f"Ingressos disponíveis para {info_evento['nome_evento']} em {info_evento['data_evento']}!\nLink: {info_evento['url']}")
        msg['Subject'] = 'Ingressos Disponíveis!'
        msg['From'] = 'seu_email@example.com'
        msg['To'] = config['email']
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        smtp_user = 'seu_email@example.com'
        smtp_password = 'sua_senha'
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        logging.info("Email de notificação enviado com sucesso.")
        print("Email de notificação enviado com sucesso.")
    except Exception as e:
        logging.error(f"Falha ao enviar email: {e}")
        print(f"Falha ao enviar email: {e}")

def monitorar_ingressos(config):
    ingressos_disponiveis_anteriormente = False
    logging.info("Iniciando monitoramento...")
    print("\nIniciando monitoramento...")
    while True:
        try:
            logging.info("Verificando disponibilidade para o evento...")
            print("\nVerificando disponibilidade para o evento...")
            info_evento = verificar_disponibilidade(config['evento'])
            if info_evento:
                print(f"Evento: {info_evento['nome_evento']}")
                print(f"Data do Evento: {info_evento['data_evento']}")
                print(f"Local: {info_evento['local']}")
                esgotado = "Sim" if info_evento['esgotado'] else "Não"
                print(f"Ingressos esgotados: {esgotado}")
                print(f"Link para compra: {info_evento['url']}")
                if not info_evento['esgotado']:
                    if not ingressos_disponiveis_anteriormente:
                        logging.info("Ingressos disponíveis! Enviando notificações.")
                        print("\nIngressos disponíveis! Você pode prosseguir com a compra.")
                        enviar_notificacao_email(config, info_evento)
                        ingressos_disponiveis_anteriormente = True
                    else:
                        logging.info("Ingressos ainda disponíveis.")
                else:
                    logging.info("Ingressos esgotados no momento.")
                    print("\nOs ingressos estão esgotados no momento.")
                    ingressos_disponiveis_anteriormente = False
            else:
                logging.info("Evento não encontrado ou informações indisponíveis.")
                print("Evento não encontrado ou informações indisponíveis.")
        except Exception as e:
            logging.error(f"Erro inesperado: {e}")
            print(f"Erro inesperado: {e}")
            print("Tentando novamente em alguns segundos...")
        time.sleep(config['intervalo_atualizacao'])

def signal_handler(sig, frame):
    print('\nEncerrando o monitoramento...')
    logging.info("Monitoramento encerrado pelo usuário.")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    configurar_logger()
    configuracao = menu_principal()
    monitorar_ingressos(configuracao)
