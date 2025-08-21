from flask import jsonify, request, render_template_string
import os
from gdrive_auto.drive_auto import upload_file, create_folder
import re

def get_app():
    from flask_app import app
    return app

app = get_app()

# Pasta temporária para salvar arquivos antes do upload
UPLOAD_TEMP_DIR = "temp_uploads"
os.makedirs(UPLOAD_TEMP_DIR, exist_ok=True)

# ID da pasta pai no Google Drive (pode ser dinâmico)
PARENT_FOLDER_ID = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>Upload para Google Drive</title>
<style>
body {
    height: 100vh;
    margin: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    background: linear-gradient(to right, #1E3C72, #2A5298);
    font-family: Arial, sans-serif;
    color: #fff;
}
.container {
    background-color: rgba(255,255,255,0.1);
    padding: 40px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    min-width: 350px;
}
input[type="file"], input[type="text"] {
    margin: 10px 0;
    padding: 8px;
    border-radius: 6px;
    border: none;
    font-size: 14px;
}
button {
    padding: 10px 30px;
    background-color: #4A90E2;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 16px;
    margin-top: 10px;
}
button:hover { background-color: #357ABD; }
.success {
    background-color: rgba(0,200,0,0.8);
    padding: 20px;
    border-radius: 10px;
    margin-top: 20px;
}
a { display: inline-block; margin-top: 15px; color: #fff; text-decoration: underline; }
</style>
</head>
<body>
<div class="container">
    <h1>Upload para Google Drive</h1>
    <form id="uploadForm" action="/upload-file" method="post" enctype="multipart/form-data">
        <input type="file" name="files" multiple required><br>
        <input type="text" name="parent_folder_id" placeholder="ID da pasta (opcional)"><br>
        <button type="submit">Enviar</button>
    </form>
    <div id="result"></div>
</div>

<script>
const form = document.getElementById("uploadForm");
const resultDiv = document.getElementById("result");

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(form);

    resultDiv.innerHTML = "⏳ Enviando...";
    try {
        const response = await fetch("/upload-file", {
            method: "POST",
            body: formData
        });
        const data = await response.json();

        if(data.success){
            resultDiv.innerHTML = `
                <div class="success">
                    ✅ Arquivos enviados com sucesso!<br>
                    IDs: ${data.files.map(f => f.file_id).join(", ")}<br>
                    <a href="/">Enviar mais arquivos</a>
                </div>
            `;
        } else {
            resultDiv.innerHTML = `<div class="success" style="background-color: rgba(200,0,0,0.8);">
                ❌ Erro: ${data.error}<br>
                <a href="/">Tentar novamente</a>
            </div>`;
        }
    } catch(err){
        resultDiv.innerHTML = `<div class="success" style="background-color: rgba(200,0,0,0.8);">
            ❌ Erro inesperado<br>
            <a href="/">Tentar novamente</a>
        </div>`;
    }
});
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/upload-file", methods=["POST"])
def upload_file_endpoint():
    files = request.files.getlist("files")
    parent_folder_id = request.form.get("parent_folder_id", PARENT_FOLDER_ID)
    parent_folder_id = parse_drive_id(parent_folder_id) if parent_folder_id else None

    if not files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    uploaded_files = []
    for file in files:
        temp_path = os.path.join(UPLOAD_TEMP_DIR, file.filename)
        file.save(temp_path)
        try:
            file_id = upload_file(temp_path, file_name=file.filename, parent_folder_id=parent_folder_id)
            uploaded_files.append({"file_id": file_id, "name": file.filename})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    return jsonify({"success": True, "files": uploaded_files})


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