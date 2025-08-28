from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import os
import time
import concurrent.futures
from tqdm import tqdm  # <<--- Biblioteca nova
from .info import *

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os
import re



# API scope
SCOPES = ['https://www.googleapis.com/auth/drive']



def get_drive_service():
    creds = None
    # Reutiliza token se já existir
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    # Se não tiver token ou expirado → abre fluxo OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Salva token para reutilizar
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("drive", "v3", credentials=creds)

def retry(func):
    """Simple retry decorator for API operations."""
    def wrapper(*args, **kwargs):
        max_attempts = 3
        delay = 2
        for attempt in range(max_attempts):
            try:
                return func(*args, **kwargs)
            except HttpError as e:
                print(f"⚠️ Attempt {attempt+1} failed: {e}")
                if attempt == max_attempts - 1:
                    raise
                time.sleep(delay)
            except Exception as e:
                print(f"⚠️ Unexpected error: {e}")
                if attempt == max_attempts - 1:
                    raise
                time.sleep(delay)
    return wrapper

# === Create a folder on Google Drive ===
@retry
def create_folder(folder_name, parent_folder_id=None):
    service = get_drive_service()
    metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_folder_id:
        metadata['parents'] = [parent_folder_id]

    folder = service.files().create(body=metadata, fields='id').execute()
    print(f'📁 Folder created: {folder.get("id")}')
    return folder.get('id')

# === Upload a file to Google Drive with progress bar ===
@retry
def upload_file(file_path, file_name=None, parent_folder_id=None):
    service = get_drive_service()

    if not file_name:
        file_name = os.path.basename(file_path)

    ext = os.path.splitext(file_path)[1].lower()

    mime_types = {
        '.pdf': 'application/pdf',
        '.png': 'image/png',
        '.mp4': 'video/mp4',
        '.mov': 'video/quicktime',
        '.txt': 'text/plain',
        '.doc': 'application/msword',  # Word antigo
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # Word moderno
        '.gdoc': 'application/vnd.google-apps.document',  # Documento do Google Docs
        '.odt': 'application/vnd.oasis.opendocument.text',  # OpenDocument Text (LibreOffice, OpenOffice)
        '.rtf': 'application/rtf',  # Rich Text Format
        '.md': 'text/markdown',  # Markdown
        '.jpeg': 'image/jpeg',
        '.jpg': 'image/jpeg',
        '.dwg': 'application/acad',
    }


    mime_type = mime_types.get(ext, 'application/octet-stream')

    file_metadata = {
        'name': file_name,
        'parents': [parent_folder_id] if parent_folder_id else []
    }

    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

    request = service.files().create(body=file_metadata, media_body=media, fields='id')

    response = None
    progress_bar = tqdm(total=os.path.getsize(file_path), unit='B', unit_scale=True, desc=f"Uploading {file_name}")

    while response is None:
        status, response = request.next_chunk()
        if status:
            progress_bar.update(status.resumable_progress - progress_bar.n)

    progress_bar.close()
    print(f"✅ Uploaded: {file_name}")
    return response.get('id')

def list_files_to_upload(directory_path, allowed_extensions=None):
    """Helper to list files with allowed extensions."""
    if allowed_extensions is None:
        allowed_extensions = [
            '.pdf', '.png', '.mp4', '.mov', '.dwg', '.txt', '.jpeg', '.jpg',
            '.doc', '.docx', '.gdoc', '.odt', '.rtf', '.md'
        ]

    files = []
    for file in os.listdir(directory_path):
        path = os.path.join(directory_path, file)
        if os.path.isfile(path):
            ext = os.path.splitext(file)[1].lower()
            if ext in allowed_extensions:
                files.append(path)
    return files

def upload_by_type(directory_path, parent_folder_id, allowed_extensions=None, max_workers=1):
    """Upload files with parallelism."""
    print("🔍 Scanning directory...")
    files = list_files_to_upload(directory_path, allowed_extensions)

    print(f"📦 {len(files)} files found. Uploading with {max_workers} workers...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for file_path in files:
            futures.append(executor.submit(upload_file, file_path, None, parent_folder_id))

        # Wait for all uploads to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"❗ Upload failed: {e}")

@retry
def find_folder_by_name(folder_name, parent_folder_id=None):
    service = get_drive_service()

    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"

    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name)',
        pageSize=1
    ).execute()

    files = results.get('files', [])
    if files:
        print(f"📂 Folder found: {files[0]['name']} (ID: {files[0]['id']})")
        return files[0]['id']
    else:
        print("❌ Folder not found.")
        return None


@retry
def list_folders_with_prefix(parent_folder_id, prefix='CPL'):
    """
    Lista todas as pastas dentro de uma pasta pai que comecem com um determinado prefixo.
    """
    service = get_drive_service()
    folders = []

    query = (
        f"mimeType = 'application/vnd.google-apps.folder' and "
        f"trashed = false and '{parent_folder_id}' in parents and "
        f"name contains '{prefix}'"
    )

    page_token = None
    while True:
        response = service.files().list(
            q=query,
            spaces='drive',
            fields='nextPageToken, files(id, name)',
            pageToken=page_token
        ).execute()

        for file in response.get('files', []):
            if file['name'].startswith(prefix):  # Garante que começa com o prefixo
                folders.append({'id': file['id'], 'name': file['name']})

        page_token = response.get('nextPageToken', None)
        if not page_token:
            break

    print(f"📁 {len(folders)} folders found starting with '{prefix}'")
    return folders


@retry
def get_higher_folder(parent_folder_id, prefix):
    folder_list = list_folders_with_prefix(parent_folder_id, prefix)

    if not folder_list:
        return None  # ou raise Exception("Nenhuma pasta encontrada.")

    def extract_code(folder):
        try:
            return folder['name'].split('.')[1]
        except IndexError:
            return ""  # ou levante erro se preferir tratar nomes inválidos

    # Encontra a pasta com o maior código
    highest_folder = max(folder_list, key=extract_code)
    highest_code = extract_code(highest_folder)

    return dict(name=highest_folder['name'], code=highest_code)

@retry
def list_folder_contents(folder_id):
    """
    Lista todos os arquivos e pastas dentro de uma pasta do Google Drive.
    Retorna uma lista de dicionários com 'id', 'name' e 'mimeType'.
    """
    service = get_drive_service()
    items = []

    query = f"'{folder_id}' in parents and trashed = false"

    page_token = None
    while True:
        response = service.files().list(
            q=query,
            spaces='drive',
            fields='nextPageToken, files(id, name, mimeType)',
            pageToken=page_token
        ).execute()

        items.extend(response.get('files', []))
        page_token = response.get('nextPageToken', None)

        if not page_token:
            break

    print(f"📄 {len(items)} items found in folder {folder_id}")
    return items

def create_next_folder(unidade: str, tanque: str, quantidade: int, name:str) -> dict:
    """
    Cria a próxima pasta no padrão XYZ.AAAAA.BBBBBB.C.0 e retorna os IDs/link.

    
    """

    #TEM QUE CADASTRAR A CES, MELHOR FAZER PELA API
    parent_folder_id = get_drive_folder_id(unidade) if get_drive_folder_id(unidade) else None

    # 1️⃣ Listar todas as pastas dentro da unidade
    folders = list_folders_with_prefix(parent_folder_id, prefix=unidade)
    
    # 2️⃣ Filtrar pastas que correspondem ao padrão do código
    pattern = re.compile(rf"{re.escape(unidade)}\.(\d{{5}})\..+\.\d+\.0")
    
    codes = []
    for f in folders:
        match = pattern.match(f['name'])
        if match:
            codes.append(int(match.group(1)))
    
    # 3️⃣ Determinar o próximo código
    next_code = max(codes) + 1 if codes else 1
    code_str = str(next_code).zfill(5)
    
    # 4️⃣ Extrair apenas o número do tanque
    tanque_num = re.search(r'\d+', tanque)
    tanque_num_str = tanque_num.group(0) if tanque_num else tanque
    tanque_num_str = tanque_num_str.zfill(6)
    # 5️⃣ Montar o nome da pasta
    folder_name = f"{unidade}.{code_str}.{tanque_num_str}.{quantidade}.0 - {name}"
    
    # 6️⃣ Criar a pasta no Drive
    new_folder_id = create_folder(folder_name, parent_folder_id)
    
    # 7️⃣ Criar subpasta "Fotos"
    photos_folder_id = create_folder("Fotos", new_folder_id)
    
    # 8️⃣ Retorno customizado
    return {
        "becus_id": code_str,              # O código sequencial gerado
        "link_google_drive": f"https://drive.google.com/drive/folders/{new_folder_id}",
        "folder_name": folder_name,
        "folder_id": new_folder_id,
        "photos_folder_id": photos_folder_id
    }
    


def list_all_folders():
    service = get_drive_service()
    folders = []
    page_token = None
    while True:
        response = service.files().list(
            q="mimeType='application/vnd.google-apps.folder' and trashed=false",
            spaces='drive',
            fields="nextPageToken, files(id, name, parents)",
            pageSize=100,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            pageToken=page_token
        ).execute()

        folders.extend(response.get('files', []))
        page_token = response.get('nextPageToken')
        if not page_token:
            break

    print(f"📂 Total de pastas encontradas: {len(folders)}")
    for f in folders:
        print(f"Nome: {f['name']} | ID: {f['id']} | Pais: {f.get('parents')}")
    return folders


def create_folder_google_drive(parent_folder, prefix, client_name, tank, quantity):

    last_folder = get_higher_folder(parent_folder, prefix)

    folder_number = int(last_folder['code']) + 1

    folder_str = str(folder_number)

    while len(folder_str) < 5:
        folder_str = '0'+folder_str

    folder_name = f'{prefix}.{folder_str}.{tank}.{quantity}.0 - {client_name}'

    new_folder_id = create_folder(folder_name, parent_folder)

    photos_folder_id = create_folder("Fotos", new_folder_id)

    return dict(folder_name=folder_name, folder_id=new_folder_id, photos_folder_id=photos_folder_id)

