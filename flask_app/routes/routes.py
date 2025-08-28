from flask import jsonify, request, render_template_string, render_template
import os
from gdrive_auto.drive_auto import upload_file, create_folder
import re
import uuid

def get_app():
    from flask_app import app
    return app

app = get_app()

# Pasta temporária para salvar arquivos antes do upload
UPLOAD_TEMP_DIR = "temp_uploads"
os.makedirs(UPLOAD_TEMP_DIR, exist_ok=True)

# ID da pasta pai no Google Drive (pode ser dinâmico)
PARENT_FOLDER_ID = None

# HTML_TEMPLATE = """
#     <!DOCTYPE html>
#     <html lang="pt-BR">
#     <head>
#         <meta charset="UTF-8">
#         <title>Uploader Google Drive</title>
#         <style>
#             body {
#                 display: flex;
#                 flex-direction: column;
#                 align-items: center;
#                 justify-content: center;
#                 height: 100vh;
#                 background: #f0f8ff;
#                 font-family: Arial, sans-serif;
#             }
#             .container {
#                 background: #ffffff;
#                 padding: 30px;
#                 border-radius: 12px;
#                 box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15);
#                 text-align: center;
#                 width: 400px;
#             }
#             input, button {
#                 margin-top: 10px;
#                 padding: 10px;
#                 border-radius: 8px;
#                 border: 1px solid #aaa;
#                 width: 100%;
#             }
#             button {
#                 background-color: #007BFF;
#                 color: white;
#                 font-weight: bold;
#                 cursor: pointer;
#             }
#             button:hover {
#                 background-color: #0056b3;
#             }
#             #status {
#                 margin-top: 15px;
#                 font-size: 14px;
#                 color: #333;
#                 text-align: left;
#             }
#         </style>
#     </head>
#     <body>
#         <div class="container">
#             <h2>Uploader Google Drive</h2>
#             <form id="uploadForm">
#                 <input type="file" name="file" multiple required><br>
#                 <input type="text" name="parent_folder_id" placeholder="Cole o link/ID da pasta"><br>
#                 <button type="submit">Enviar</button>
#             </form>
#             <div id="status"></div>
#         </div>

#         <script>
#             document.getElementById("uploadForm").addEventListener("submit", async function(e) {
#                 e.preventDefault();

#                 const files = e.target.file.files;
#                 const parentFolder = e.target.parent_folder_id.value.trim();
#                 const statusDiv = document.getElementById("status");

#                 statusDiv.innerHTML = "⏳ Enviando arquivos...<br>";

#                 for (let i = 0; i < files.length; i++) {
#                     const formData = new FormData();
#                     formData.append("file", files[i]);
#                     formData.append("parent_folder_id", parentFolder);

#                     try {
#                         const res = await fetch("/upload-file", {
#                             method: "POST",
#                             body: formData
#                         });
#                         const data = await res.json();

#                         if (data.success) {
#                             statusDiv.innerHTML += `✅ ${files[i].name} enviado com sucesso<br>`;
#                         } else {
#                             statusDiv.innerHTML += `❌ Erro ao enviar ${files[i].name}: ${data.error}<br>`;
#                         }
#                     } catch (err) {
#                         statusDiv.innerHTML += `⚠️ Falha de rede ao enviar ${files[i].name}<br>`;
#                     }
#                 }

#                 statusDiv.innerHTML += "<br><b>📂 Upload concluído!</b>";
#             });
#         </script>
#     </body>
#     </html>
#     """

@app.route("/")
def index():
    drive_id = request.args.get("drive_id")  # pega da query string
    drive_link = f'https://drive.google.com/drive/u/4/folders/{drive_id}'
    return render_template("upload_google_drive.html", param=drive_link)

@app.route("/upload-file", methods=["POST"])
def upload_file_endpoint():
    file = request.files.get("file")
    parent_folder_id = request.form.get("parent_folder_id", PARENT_FOLDER_ID)
    parent_folder_id = parse_drive_id(parent_folder_id) if parent_folder_id else None

    if not file:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400


    uuid_name = f"{uuid.uuid4()}_{file.filename}"
    temp_path = os.path.join(UPLOAD_TEMP_DIR, uuid_name)
    file.save(temp_path)
    try:
        file_id = upload_file(temp_path, file_name=file.filename, parent_folder_id=parent_folder_id)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return jsonify({"success": True, "files": file_id})


def parse_drive_id(drive_url_or_id: str) -> str:
    """
    Extrai o ID da pasta/arquivo do Google Drive a partir de um link ou ID direto.
    Exemplos de links:
        https://drive.google.com/drive/folders/1_lDZn5GW0wXBJ9uuiX8Isck1fsdfnurG
        https://drive.google.com/open?id=1_lDZn5GW0wXBJ9uuiX8Isck1fsdfnurG
    Ou apenas o ID:
        1_lDZn5GW0wXBJ9uuiX8Isck1fsdfnurG
    """
    if not drive_url_or_id:
        return None

    # Tenta extrair do link
    match = re.search(r"/folders/([a-zA-Z0-9_-]+)", drive_url_or_id)
    if not match:
        match = re.search(r"id=([a-zA-Z0-9_-]+)", drive_url_or_id)

    if match:
        return match.group(1)

    # Caso já seja só o ID
    return drive_url_or_id if re.match(r"^[a-zA-Z0-9_-]+$", drive_url_or_id) else None