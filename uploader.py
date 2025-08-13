from data_collector.cpq_super import get_parent_folder, data_validation, get_becus_code, split_text
from gdrive_auto.drive_auto import find_folder_by_name, list_folder_contents, create_folder, upload_by_type
from utils import generate_log

import os
import sys


def upload():


    # PEGANDO CODIGO BECUS

    if getattr(sys, 'frozen', False):  # executável com PyInstaller
            path = sys.executable
    else:
            path = os.path.abspath(__file__)

    name = input("Digite seu nome: ")


    parent_folder = get_parent_folder(path)
    becus_code = get_becus_code(parent_folder)
    

    folder_id_drive = find_folder_by_name(parent_folder, parent_folder_id=None)

    folder_contents = list_folder_contents(folder_id_drive)

    dir_path = os.path.dirname(path)

    

    dir_path = os.path.join(dir_path, "upload")

    generate_log(dir_path, name=name)

    upload_version = 1
    higher = 0

    for i in folder_contents:
        name = i['name']
        if name.startswith("upload_"):
            try:
                # Pega somente a parte numérica logo após "upload_"
                version_str = name.split('_')[1]
                version_num = ''.join(c for c in version_str if c.isdigit())
                
                if version_num:  # só se achou dígitos
                    upload_version = int(version_num)
                    if upload_version > higher:
                        higher = upload_version
            except (IndexError, ValueError):
               pass

    new_folder_id = create_folder(f"upload_{higher + 1}", folder_id_drive)

    

    upload_by_type(dir_path, new_folder_id)



    return f'https://drive.google.com/drive/u/4/folders/{new_folder_id}', f'version: {higher + 1}'


print(upload())
input("Aperte enter para encerrar")