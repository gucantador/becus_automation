from data_collector.cpq_super import get_parent_folder, data_validation, get_becus_code, split_text
from gdrive_auto.drive_auto import find_folder_by_name, list_folder_contents, create_folder, upload_by_type, upload_file
from utils import generate_log

import os
import sys

import logging
import traceback


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

log = logging.getLogger(__name__)

def check_dwg():
    if getattr(sys, 'frozen', False):  # executável com PyInstaller
        path = sys.executable
    else:
        path = os.path.abspath(__file__)

    dirs = os.listdir(os.path.dirname(path))
    
    arquivos_subidos = []  # lista para registrar arquivos enviados

    for dir in dirs:
        working_folder = os.path.join(os.path.dirname(path), dir)
        if os.path.isdir(working_folder):
            try:
                print(f'Procurando por pasta {dir}')
                folder_id_drive = find_folder_by_name(dir, parent_folder_id=None)
                folder_contents = list_folder_contents(folder_id_drive)
                has_dwg = any(
                    item["name"].lower().endswith(".dwg") or item["mimeType"] == "application/acad"
                    for item in folder_contents
                )

                if has_dwg:
                      arquivos_subidos.append(dir)

            except Exception as e:
                            logging.error(f"Error processing folder {dir}: {e}")

def upload_dwg():
    if getattr(sys, 'frozen', False):  # executável com PyInstaller
        path = sys.executable
    else:
        path = os.path.abspath(__file__)

    dirs = os.listdir(os.path.dirname(path))
    
    arquivos_subidos = [] 
    
    arquivos_ja_com_dwg = [] # lista para registrar arquivos enviados

    for dir in dirs:
        working_folder = os.path.join(os.path.dirname(path), dir)
        if os.path.isdir(working_folder):
            try:
                print(f'Procurando por pasta {dir}')
                folder_id_drive = find_folder_by_name(dir, parent_folder_id=None)
                folder_contents = list_folder_contents(folder_id_drive)
                has_dwg = any(
                    item["name"].lower().endswith(".dwg") or item["mimeType"] == "application/acad"
                    for item in folder_contents
                )

                if has_dwg:
                     arquivos_ja_com_dwg.append(dir)

                if not has_dwg:
                    logging.info(f"No DWG files found in folder: {dir}")
                    new_folder_id = create_folder("upload_BKP", folder_id_drive)
                    try:
                        for file in os.listdir(working_folder):
                            file_path = os.path.join(working_folder, file)
                            if os.path.isfile(file_path) and file.lower().endswith('.dwg'):
                                logging.info(f"Uploading {file_path} to Google Drive")
                                # Caminho longo compatível com Windows
                                upload_file(file_path, parent_folder_id=new_folder_id)
                                arquivos_subidos.append(file_path)  # registra no log

                    except Exception as e:
                        logging.error(f"Error uploading files from {working_folder}: {e}")
            except Exception as e:
                logging.error(f"Error processing folder {dir}: {e}")

    # Gera log dos arquivos subidos
    if arquivos_subidos:
        try:
            log_name = os.path.join(os.path.dirname(path), "upload_log.txt")
            with open(log_name, "a", encoding="utf-8") as f:
                f.write("===== UPLOAD LOG =====\n")
                for arquivo in arquivos_subidos:
                    f.write(f"{arquivo}\n")
                f.write("\n")
            logging.info(f"Log de upload salvo em {log_name}")
        except Exception as e:
            logging.error(f"Erro ao salvar log: {e}")


        if arquivos_ja_com_dwg:
            try:
                log_name = os.path.join(os.path.dirname(path), "upload_log.txt")
                with open(log_name, "a", encoding="utf-8") as f:
                    f.write("===== ARQUIVOS COM DWG LOG =====\n")
                    for arquivo in arquivos_ja_com_dwg:
                        f.write(f"{arquivo}\n")
                    f.write("\n")
                logging.info(f"Log salvo em {log_name}")
            except Exception as e:
                logging.error(f"Erro ao salvar log: {e}")


try:
    upload_dwg()
    input("Aperte Enter para encerrar")
except Exception as e:
    log.error(f"Erro ao executar o processo: {e}")
    log.error(traceback.format_exc())  # Mostra a stack trace completa
input("Pressione Enter para sair...")
