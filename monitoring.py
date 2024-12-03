import time
import requests
import json
from datetime import datetime

def menu_principal():
    print("===== Configuração do Monitor de Ingressos =====")
    email = input("Insira seu email do Seated: ")
    senha = input("Insira sua senha do Seated: ")
    quantidade_ingressos_desejada = input("Quantidade de ingressos a comprar: ")
    intervalo_atualizacao = 300  # 5 minutos em segundos

    return {
        'email': email,
        'senha': senha,
        'quantidade_ingressos_desejada': quantidade_ingressos_desejada,
        'intervalo_atualizacao': intervalo_atualizacao
    }

def verificar_disponibilidade():
    # Link da API fixo no código
    api_link = "https://api.seated.com/api/v1/tour-events/645f7ccd-36bc-44a7-b9d5-7c5e536c37c7?include=artist%2Cartist.artist-optins%2Con-sale-dates.event%2Cvenue"

    try:
        response = requests.get(api_link)
        response.raise_for_status()  # Verifica se a requisição foi bem-sucedida
    except requests.exceptions.HTTPError as err:
        print(f"Erro ao acessar a API: {err}")
        return None

    # Analisa o conteúdo JSON da resposta
    data = response.json()

    # Extrai as informações necessárias
    try:
        # Extrai as informações principais
        event_data = data.get('data', {})
        attributes = event_data.get('attributes', {})
        starts_at = attributes.get('starts-at')
        is_sold_out = attributes.get('is-sold-out')

        # Formata a data de início do evento
        if starts_at:
            starts_at_formatted = datetime.strptime(starts_at, "%Y-%m-%dT%H:%M:%SZ")
            starts_at_str = starts_at_formatted.strftime("%d/%m/%Y %H:%M:%S")
        else:
            starts_at_str = "Data de início do evento não disponível"

        # Verifica se há datas de início de vendas em 'included'
        included = data.get('included', [])
        sale_starts_at_str = "Data de início das vendas não disponível"
        for item in included:
            if item.get('type') == 'on-sale-dates':
                on_sale_dates = item.get('attributes', {})
                sale_starts_at = on_sale_dates.get('starts-at')
                if sale_starts_at:
                    sale_starts_at_formatted = datetime.strptime(sale_starts_at, "%Y-%m-%dT%H:%M:%SZ")
                    sale_starts_at_str = sale_starts_at_formatted.strftime("%d/%m/%Y %H:%M:%S")
                break

        # A quantidade de ingressos não está presente no JSON fornecido
        quantidade_ingressos = "Informação não disponível"

        # Retorna um dicionário com as informações
        return {
            'data_inicio_evento': starts_at_str,
            'data_inicio_vendas': sale_starts_at_str,
            'quantidade_ingressos': quantidade_ingressos,
            'esgotado': is_sold_out
        }
    except Exception as e:
        print(f"Erro ao processar os dados da API: {e}")
        return None

def monitorar_ingressos(config):
    print("\nIniciando monitoramento...")
    while True:
        print("\nVerificando disponibilidade para o evento...")
        info_ingressos = verificar_disponibilidade()
        
        if info_ingressos:
            print(f"Data de início do evento: {info_ingressos['data_inicio_evento']}")
            print(f"Data de início das vendas: {info_ingressos['data_inicio_vendas']}")
            print(f"Quantidade de ingressos disponíveis: {info_ingressos['quantidade_ingressos']}")
            esgotado = "Sim" if info_ingressos['esgotado'] else "Não"
            print(f"Ingressos esgotados: {esgotado}")

            if not info_ingressos['esgotado']:
                print("\nIngressos disponíveis! Você pode prosseguir com a compra.")
                # Aqui você pode adicionar lógica para iniciar o processo de compra ou notificar o usuário
            else:
                print("\nOs ingressos estão esgotados no momento.")
        else:
            print("Não foi possível obter as informações do evento.")

        # Aguardar o intervalo definido antes de verificar novamente
        time.sleep(config['intervalo_atualizacao'])

if __name__ == "__main__":
    configuracao = menu_principal()
    monitorar_ingressos(configuracao)
