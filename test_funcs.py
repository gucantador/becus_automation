from data_collector.cpq_super import get_parent_folder, data_validation, get_becus_code, split_text
from gdrive_auto.drive_auto import find_folder_by_name, list_folder_contents, create_folder, upload_by_type, list_all_folders
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


def upload():
    folder_name = 'SPL.02120.000190.2.0 - Geisla Arislaine Souza Rafael'

    return find_folder_by_name(folder_name, parent_folder_id=None)

    # folder_id_drive = find_folder_by_name(folder_name, parent_folder_id=None)




try:
    print(upload())
    input("Aperte enter para encerrar")
except Exception as e:
    log.error(f"Erro ao executar o processo: {e}")
    log.error(traceback.format_exc())  # Mostra a stack trace completa
input("Pressione Enter para sair...")