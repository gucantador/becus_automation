import requests
import json
import os
import traceback
from sheetHandler import sheetHandler
from art_jsons import *
import sys

from utils import get_adress_info
from data_collector.cpq_super import gather_all_data

from auth_crea import get_valid_token

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

log = logging.getLogger(__name__)


# ==== CONFIGURATION ====
BASE_API_URL = 'https://servicos.crea-pr.org.br/'
CREATE_ART_URL = f'{BASE_API_URL}services/api/art'
CONTRATO_URL = f'{BASE_API_URL}services/api/art/contrato'   
ENDERECO_URL = f'{BASE_API_URL}services/api/art/endereco'
ATIVIDADE_URL = f'{BASE_API_URL}services/api/art/atividade'





# ========================

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def send_request_POST(json_data, api_url):
    headers = {
        'Authorization': f'Bearer {get_valid_token()}',
        'Content-Type': 'application/json'
    }

    response = requests.post(api_url, headers=headers, json=json_data)
    return response




if __name__ == "__main__":


    #--------------------------------------------------------------------------------------------

    # CRIANDO ART

    def run_xls(handler):

        print("Criando ART...")

        response = send_request_POST(CREATE_ART_JSON, CREATE_ART_URL)

        print("Status code:", response.status_code)
        print("Response:")
        try:
            response_data = response.json()

        except ValueError:
            print(response.text)
            exit()

        art_id = response_data['id']

        print(f'ART criada com sucesso! ID: {art_id}')

        

        #--------------------------------------------------------------------------------------------
        #PREENCHENDO DADOS DO CONTRATO - EXCEL
        print("Preenchendo dados do contrato...")




        

        # Gerar os JSONs com base nos dados da planilha
        contrato_json = get_contrato_json_SLD(
            art_id=art_id,
            documento_cliente=handler.get_documento_cliente(),
            razao_social_cliente=handler.get_razao_social_cliente(),
            data_prevista_inicio=handler.get_data_prevista_inicio()  # ou outra lógica para conclusão
        )

        contrato = send_request_POST(contrato_json, CONTRATO_URL)



        print(f"Contrato preenchido com sucesso! ID: {contrato.json().get('id')}")


        

        #--------------------------------------------------------------------------------------------

        #PREENCHENDO ENDEREÇO DO CLIENTE

        print("Preenchendo endereço do cliente...")

        adress_info = get_adress_info(handler.get_cep())

        



        endereco_cliente_json = get_endereco_cliente_json(
            contrato_id=contrato.json().get('id'),  # Substitua com ID real se for necessário
            cep=handler.get_cep(),
            logradouro=adress_info.get('logradouro'),
            numero=handler.get_numero(),
            bairro=adress_info.get('bairro')
        )


        #--------------------------------------------------------------------------------------------


        endereco = send_request_POST(endereco_cliente_json, ENDERECO_URL)

        #PREENCHENDO ATIVIDADE

        print("Preenchendo atividade técnica...")

        atividade_json = get_atividade_tecnica_json(art_id=art_id, codigo_becus=str(handler.get_codigo_becus()))

        atividade = send_request_POST(atividade_json, ATIVIDADE_URL)

        x = handler.update_row()

        if x:
            run_xls(handler)
        else:
            print("Todas ARTs preenchidas com sucesso!")
            return
        
    def run_file_in_folder():
        caminho_pdf = "cpq.pdf"




        if getattr(sys, 'frozen', False):  # executável com PyInstaller
            path = sys.executable
        else:
            path = os.path.abspath(__file__)

            
        files = os.listdir(os.path.dirname(path))
        print(files)
        relatorio = None

        for file in files:
            if "visita" in file.lower():
                relatorio = file
                break

        

        dados = gather_all_data(path, caminho_pdf, relatorio)
        
        print("DADOS COLETADOS:")
        print("1 - " + dados.get("ceps", ""))
        print("2 - " + dados.get("numeros_endereco", ""))
        print("3 - " + dados.get("documento", ""))
        print("4 - " + dados.get("razao_social", ""))
        print("5 - " + dados.get("data", ""))
        print("6 - " + dados.get("becus_code", ""))

        answer = None

        while answer != "n":
            answer = input("Atualizar algum dado? (s/n): ").strip().lower()

            if answer == 's':
                print("\nDigite o número do dado que deseja atualizar:")
                print("1 - CEPs")
                print("2 - Números de Endereço")
                print("3 - Documento")
                print("4 - Razão Social")
                print("5 - Data")
                print("6 - Código Becus")

                opcao = input("Opção (1-6): ").strip()
                novo_valor = input("Novo valor: ").strip()

                if opcao == '1':
                    dados["ceps"] = novo_valor
                elif opcao == '2':
                    dados["numeros_endereco"] = novo_valor
                elif opcao == '3':
                    dados["documento"] = novo_valor
                elif opcao == '4':
                    dados["razao_social"] = novo_valor
                elif opcao == '5':
                    dados["data"] = novo_valor
                elif opcao == '6':
                    dados["becus_code"] = novo_valor
                else:
                    print("Opção inválida!")

                print("\nDado atualizado com sucesso!\n")


            

        # >>> Início do processo baseado nos dados <<<

        print("Criando ART...")

        response = send_request_POST(CREATE_ART_JSON, CREATE_ART_URL)

        print("Status code:", response.status_code)
        print("Response:")
        try:
            response_data = response.json()
        except ValueError:
            print(response.text)
            exit()

        art_id = response_data['id']
        print(f'ART criada com sucesso! ID: {art_id}')

        #--------------------------------------------------------------------------------------------
        # PREENCHENDO DADOS DO CONTRATO
        print("Preenchendo dados do contrato...")

        contrato_json = get_contrato_json_SLD(
            art_id=art_id,
            documento_cliente=dados.get("documento", ""),  # Adicione isso no gather_all_data se necessário
            razao_social_cliente=dados.get("razao_social", ""),
            data_prevista_inicio=dados.get("data", "")
        )

        contrato = send_request_POST(contrato_json, CONTRATO_URL)
        contrato_id = contrato.json().get('id')

        print(f"Contrato preenchido com sucesso! ID: {contrato_id}")

        #--------------------------------------------------------------------------------------------
        # PREENCHENDO ENDEREÇO DO CLIENTE
        print("Preenchendo endereço do cliente...")

        cep = dados.get("ceps")
        print(cep)
        numero = dados.get("numeros_endereco")
        
        adress_info = "anything"

        print(adress_info)

        endereco_cliente_json = get_endereco_cliente_json(
            contrato_id=contrato_id,
            cep=cep,
            numero=numero,
        )

        endereco = send_request_POST(endereco_cliente_json, ENDERECO_URL)

        #--------------------------------------------------------------------------------------------
        # PREENCHENDO ATIVIDADE
        print("Preenchendo atividade técnica...")

        atividade_json = get_atividade_tecnica_json(
            art_id=art_id,
            codigo_becus=dados.get("becus_code", "")
        )

        atividade = send_request_POST(atividade_json, ATIVIDADE_URL)

        print("Processo finalizado com sucesso.")

        return art_id


try:
    art_id = run_file_in_folder()
    print(f'https://servicos.crea-pr.org.br/restrito/art/obra-servico?artId={art_id}')
except Exception as e:
    log.error(f"Erro ao executar o processo: {e}")
    log.error(traceback.format_exc())  # Mostra a stack trace completa
input("Pressione Enter para sair...")

# DESCOBRIR COMO TESTAR PORQUE TEM QUE COLOCAR NUMA PASTA