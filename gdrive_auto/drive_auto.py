from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import os
import time
import concurrent.futures
from tqdm import tqdm  # <<--- Biblioteca nova
from .info import *


credss = {
  "type": "service_account",
  "project_id": "becus-drive",
  "private_key_id": "74f1f746bc725ffa1547ecc1038e0df53d0fedd0",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEuwIBADANBgkqhkiG9w0BAQEFAASCBKUwggShAgEAAoIBAQCpr8ItlaAm4RMV\nL6LBaM82wr91OdA7v4f6VNfdkqQMDcFW0H4MuFqDZeTaYqr4kWez1Xn09UxVzTzN\nIyeHnN/0o6wPIMGMiTsVWJBL4y7KGIi6zdcocUZUbkVMbIn335BjnVJyMjayih18\n4C1h2guuz4cc0jgFwmyulPKMLaj5lkPJFk5326hzg7nqca876svHpk2kRWasiTwV\nQH5/bj3i7Bs2xA9VLwzw989h06OdLAMKKatcu7PxnnedYI6kpaVpg5TpzJo60Ww8\nNXPoBEskMpnSyQmqERq/aVG2suqe/FUZa3ePtwbCbJZkEfCLXclgiZhYxXSufhmS\nzE86OTS1AgMBAAECggEAJB2fPd4Ik/XYPqxgnvs8jUp2fxASyMC7g5Wey09cgJ9F\n3QErru/m/ewIQU36V0T1dkJzvmYePO3dqMi4b2X9ib9zTdX6M/v6WhD7R1effA6s\nPVw11OsFHc/JippYZCxOelE//MPAvg/k9lDtf9PtpCOR/ZmlqF4pDSBxHlJSkmpm\ndeoGreMwh9IrsnaflshGbbjzDZGDvB1dCnkiqJ7LwuPLubJjo/AS85YtTD+yhsI7\nFmhQcg/UrzUdlJxtOoy2bjai5O3iuC95VEfXq/bvA0FFQ/+wm2zbc3KEGqnqWNxn\ngeGQk2Pl9F4GEpYaShqFuJgrY8KJTCHVNiVb7HH3sQKBgQDrxsQSiwZ9jJGAuBqh\nLwoHKze0ZZ2nQA5qHbG0pGBgIoPCrdyqfrmiKKmMW/Z1betMVlMFBkpqFEHZ3QUq\n8I15fPFl2jT/RbiWngdwYYbIm4+mSwWVqbiet332H7AoV6i4EhfSETTgpGEES4rZ\nXeoyz/YBBOMvpwBc3asMyje8EQKBgQC4PcaTc6HusM+Ei+2uRdkPfa3swTPpllA6\nu6MMNLV7F5i5/3wExvlbryoaqDWQG3axP8f4Wr3AWa3G0QHtNoi9THyUmzYaUOiO\nj1ofCjYw4gAyiRTEruQ8I483Uj36mmotFZ9Q9ifwJVKQvYIDfq9VqrCr7O4Xqr86\nTSjR0+XiZQJ/YouxaA6zp8YZCrPobXY7usNVhRDz0/PyEmhW3inWHlhOug/xK1HM\nRPq54vCNEofe0QlDqdX3RF8zJtw6TLg+aYjPXMLXY9rATDPA6DfbHf3nDJpOuz80\n6yHGhBi6iCIbYtQtIKAQedQ6uJDad//I43QIXmSskD486JO96pqasQKBgAReYqEI\ncuSICMOp1b72JQl6/27HvgVh7REXdexKK6t5icOPTU+HsE3+P09Wgb6jCBN34bP/\n4tP2zGoUdqk7S87BS4ryizvgg0MuHwLxaQuLsFmCap2nT/4lEbZMGvAgTTg4dQik\nbZoCKI0KEVUn4dx0KbBJ8/NXtyUYw0kGb0MJAoGBAN+rS8s5h6E6zCgfVeEBnJqj\n1jc3m4ntrGvN+8XjZtii23ZYuKfpfeJf3mh0XCHE9HrV/5lfjw/W+3zkJHH+nsJ+\nSXo9WefNfOtQ76BseFyleALZptp/jQdwK9BuLw5lBl4tf79epfvafBrjoqNgF/Qn\nUTfKtrLMDcGSvpwRrrNu\n-----END PRIVATE KEY-----\n",
  "client_email": "becus-bot@becus-drive.iam.gserviceaccount.com",
  "client_id": "112826239196351120357",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/becus-bot%40becus-drive.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# Path to your service account credentials
SERVICE_ACCOUNT_FILE = 'credentials.json'

# API scope
SCOPES = ['https://www.googleapis.com/auth/drive']

# ====== GLOBAL SERVICE CONTROL =======
_service = None
_service_created_at = 0
SERVICE_TTL_SECONDS = 30 * 60  # 30 minutes

def get_drive_service():
    """Returns a fresh or existing Google Drive service."""
    global _service, _service_created_at

    now = time.time()

    if _service is None or now - _service_created_at > SERVICE_TTL_SECONDS:
        print("🔄 Building new Drive service...")
        # credentials = service_account.Credentials.from_service_account_file(
        #     SERVICE_ACCOUNT_FILE, scopes=SCOPES
        # )

        credentials = service_account.Credentials.from_service_account_info(credss, scopes=SCOPES)
        _service = build('drive', 'v3', credentials=credentials)
        _service_created_at = now
    else:
        print("✅ Reusing existing Drive service...")

    return _service

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
        allowed_extensions = ['.pdf', '.png', '.mp4', '.mov', '.dwg', '.txt', '.jpeg', '.jpg']

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

