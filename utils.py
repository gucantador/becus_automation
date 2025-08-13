import requests
import os
from datetime import datetime

def check_cep(cep):
    cep = str(cep)
    cep = cep.replace("-", "").strip()  # Remove traços e espaços
    url = f"https://viacep.com.br/ws/{cep}/json/"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        dados = response.json()
        if "erro" in dados:
            print("CEP não encontrado.")
            return None
        return dados
    else:
        print(f"Erro na requisição: {response.status_code}")
        return None
    

def get_adress_info(cep):
    dados = check_cep(cep)
    print(dados)
    if dados:
        return {
            "logradouro": dados.get("logradouro"),
            "bairro": dados.get("bairro"),
        }
    return None



def generate_log(folder_path, name=None,  log_file="upload/log.txt"):
    # Garante que o caminho existe
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Pasta não encontrada: {folder_path}")

    # Pega data/hora para registrar
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Lista conteúdo
    items = os.listdir(folder_path)

    # Cria o log
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"Log gerado em {now}\n")
        f.write(f"Pasta: {folder_path}\n\n")
        f.write(f"Upload feito por {name}\n")
        for item in items:
            full_path = os.path.join(folder_path, item)
            if os.path.isdir(full_path):
                f.write(f"[DIR]  {item}\n")
            else:
                f.write(f"[FILE] {item}\n")
    
    print(f"Log salvo em: {os.path.abspath(log_file)}")


