import fitz  # PyMuPDF
import re
import os

def encontrar_ceps_em_pdf(doc):
    texto_total = ""
    for pagina in doc:
        texto_total += pagina.get_text()
    ceps = re.findall(r"\b\d{5}-\d{3}\b", texto_total)
    return ceps

def extrair_trechos_endereco(doc):
    trechos_endereco = []
    for pagina in doc:
        texto = pagina.get_text()
        padrao = re.compile(r'Endereço de entrega:(.*?)(?=Dados Contato:)', re.DOTALL | re.IGNORECASE)
        encontrados = padrao.findall(texto)
        for trecho in encontrados:
            trecho_limpo = trecho.strip()
            if trecho_limpo:
                trechos_endereco.append(trecho_limpo)
    return trechos_endereco

def extrair_numero_endereco(texto):
    match = re.search(r'(?:n[º°]?\s*|,\s*)?(\d{1,5}[A-Za-z\-]?)', texto, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def extrair_info_pdf(caminho_pdf):
    doc = fitz.open(caminho_pdf)

    ceps = encontrar_ceps_em_pdf(doc)
    trechos = extrair_trechos_endereco(doc)
    cnpjs = encontrar_cnpjs_em_pdf(caminho_pdf)

    numeros = []
    for trecho in trechos:
        numero = extrair_numero_endereco(trecho)
        if numero:
            numeros.append(numero)

    numeros_unicos = list(set(numeros))

    # Fecha o documento para liberar o arquivo
    doc.close()

    return {
        "ceps": ceps,
        "numeros_endereco": numeros_unicos,
        "documento": cnpjs[0]
    }



def encontrar_cnpjs_em_pdf(caminho_pdf):
    doc = fitz.open(caminho_pdf)
    cnpjs = []

    # Regex para encontrar o CNPJ
    # Pode ter pontos, barras e hífens, ou só números
    padrao = re.compile(
        r'Número do Documento:\s*([0-9]{2}\.?[0-9]{3}\.?[0-9]{3}/?[0-9]{4}-?[0-9]{2}|[0-9]{14})',
        re.IGNORECASE
    )

    for pagina in doc:
        texto = pagina.get_text()
        encontrados = padrao.findall(texto)
        for cnpj in encontrados:
            cnpjs.append(cnpj)

    doc.close()
    return cnpjs


def split_text(text):
    """Splits text into code and name, handling all types of dash spacing."""
    parts = re.split(r"\s*-\s*", text, maxsplit=1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    else:
        raise ValueError(f"Invalid format. Couldn't split: '{text}'")

def validate_code_format(code):
    """Checks if the code is in the valid BECUS format."""
    pattern = r"^[A-Z]{3}\.\d{5}\.\d{6}\.\d\.\d$"
    return re.match(pattern, code) is not None

def try_fix_code(code):
    """
    Attempts to fix the code by removing extra leading zeros
    only from the numeric parts, if any part is longer than it should be.
    """
    parts = code.split(".")
    if len(parts) != 5:
        return code  # Can't fix this

    prefix = parts[0]
    p1 = parts[1]
    p2 = parts[2]
    p3 = parts[3]
    p4 = parts[4]

    changed = False

    # Fix part 1 (should be 5 digits)
    if len(p1) > 5 and p1.startswith("0"):
        p1 = p1[1:]
        changed = True

    # Fix part 2 (should be 6 digits)
    if len(p2) > 6 and p2.startswith("0"):
        p2 = p2[1:]
        changed = True

    fixed_code = f"{prefix}.{p1}.{p2}.{p3}.{p4}"
    if changed:
        print(f"⚠️ Fixed code from '{code}' to '{fixed_code}' (removed extra leading zero)")
    return fixed_code

def get_becus_code(text):
    raw_code, _ = split_text(text)
    if validate_code_format(raw_code):
        return raw_code
    else:
        fixed_code = try_fix_code(raw_code)
        if validate_code_format(fixed_code):
            return fixed_code
        else:
            raise ValueError(f"🚫 Code '{raw_code}' is not in a valid format and could not be auto-fixed.")

def get_razao_social(text):
    _, name = split_text(text)
    return name

import re
from datetime import datetime

def extract_date(text):
    """
    Extracts an 8-digit number from the text and formats it as dd/mm/yyyy.
    If no valid date is found, raises an error.
    """
    match = re.search(r"\b(\d{8})\b", text)
    if not match:
        raise ValueError("🚫 No 8-digit date found in the text.")
    
    raw_date = match.group(1)

    try:
        date_obj = datetime.strptime(raw_date, "%d%m%Y")
        formatted_date = date_obj.strftime("%d/%m/%Y")
        return formatted_date
    except ValueError:
        raise ValueError(f"🚫 Invalid date format or impossible date: '{raw_date}'")





def get_parent_folder(file_path):
    """
    Returns the name of the parent directory of the given file path.


    use this to get the path: path = os.path.abspath(__file__)
    """
    parent_path = os.path.dirname(file_path)
    folder_name = os.path.basename(parent_path)

    if len(folder_name.split('.')) > 1:
        return folder_name
    
    return get_parent_folder(parent_path)

def data_validation(data):
    # Validar se todos os CEPs são iguais
    ceps = data.get("ceps", [])
    if ceps and not all(cep == ceps[0] for cep in ceps):
        raise ValueError("Os CEPs não são iguais.")

    # Validar se há apenas um número de endereço ou se todos são iguais
    numeros = data.get("numeros_endereco", [])
    if numeros:
        if len(numeros) > 1 and not all(num == numeros[0] for num in numeros):
            raise ValueError("Os números de endereço são diferentes.")
        
    return True


def gather_all_data(file_path, cpq_path, relatorio_path):
    cpq_info = extrair_info_pdf(cpq_path)
    folder_name = get_parent_folder(file_path)
    cpq_info["becus_code"] = get_becus_code(folder_name)
    cpq_info["razao_social"] = get_razao_social(folder_name)
    cpq_info["data"] = extract_date(relatorio_path)

    if data_validation(cpq_info):
        cpq_info["numeros_endereco"] = cpq_info["numeros_endereco"][0]
        cpq_info["ceps"] = cpq_info["ceps"][0]

    return cpq_info




if __name__ == "__main__":
    caminho_pdf = "cpq.pdf"
    path = os.path.abspath(__file__)


    files = os.listdir(os.path.dirname(path))

    relatorio = None

    for file in files:
        if "visita" in file.lower():
            relatorio = file
            break
    
    data = gather_all_data(path, caminho_pdf, relatorio)

    if data_validation(data):
        data["numeros_endereco"] = data["numeros_endereco"][0]
        data["ceps"] = data["ceps"][0]
