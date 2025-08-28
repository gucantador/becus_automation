from flask import jsonify, request, Blueprint, request, jsonify, redirect, url_for

from gdrive_auto.drive_auto import upload_file, create_folder, create_next_folder


def get_app():
    from flask_app import app
    return app

app = get_app()



from ..models import db, Cliente

# -------------------------------
# POST - Cadastrar Cliente
# -------------------------------
@app.route("/clientes", methods=["POST"])
def create_cliente():
    data = request.get_json()
    print(data)
    next_folder = create_next_folder(data.get("unidade"), data.get('tanque'), int(data.get("quantidade")), data.get("name"))
    becus_id = next_folder["becus_id"] if data.get("criar-pasta") else data.get("criar-pasta") 
    google_drive_link = data.get("link_google_drive") or next_folder["link_google_drive"]
    try:
        cliente = Cliente(
            tanque=data.get("tanque"),
            quantidade=data.get("quantidade"),
            unidade=data["unidade"],
            capex=data.get("capex"),
            cidade=data.get("cidade"),
            observacoes=data.get("observacoes"),
            link_google_drive=google_drive_link,
            becus_id = becus_id,
            estado=data.get("estado"),
            cep=data.get("CEP"),
            numero=data.get("numero"),
            logradouro=data.get("logradouro"),
            bairro=data.get("bairro"),
            cnpj=data.get("cnpj"),
            name=data.get("name")
        )
        db.session.add(cliente)
        db.session.commit()
        return jsonify({
                "success": True,
                "redirect_url": url_for('index', drive_id=next_folder["folder_id"])
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# PUT - Atualizar Cliente
@app.route("/clientes/<int:cliente_id>", methods=["PUT"])
def update_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    data = request.get_json()

    cliente.tanque = data.get("tanque", cliente.tanque)
    cliente.unidade = data.get("unidade", cliente.unidade)
    cliente.capex = data.get("capex", cliente.capex)
    cliente.cidade = data.get("cidade", cliente.cidade)
    cliente.observacoes = data.get("observacoes", cliente.observacoes)
    cliente.link_google_drive = data.get("link_google_drive", cliente.link_google_drive)
    cliente.becus_id = data.get("becus_id", cliente.becus_id)
    cliente.estado = data.get("estado", cliente.estado)
    cliente.cep = data.get("CEP", cliente.cep)
    cliente.numero = data.get("numero", cliente.numero)
    cliente.logradouro = data.get("logradouro", cliente.logradouro)

    db.session.commit()
    return jsonify({"message": "Cliente atualizado com sucesso", "cliente": cliente.to_dict()})


# -------------------------------
# GET - Cliente por ID
# -------------------------------
@app.route("/clientes/<int:cliente_id>", methods=["GET"])
def get_cliente_by_id(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    return jsonify(cliente.to_dict(include_projetos=True))


# -------------------------------
# GET - Clientes por nome (texto parcial)
# -------------------------------
@app.route("/clientes/name/<string:name>", methods=["GET"])
def get_clientes_by_name(name):
    clientes = Cliente.query.filter(Cliente.unidade.ilike(f"%{name}%")).all()
    return jsonify([c.to_dict() for c in clientes])


# -------------------------------
# GET - Cliente por becus_id
# -------------------------------
@app.route("/clientes/becus/<string:becus_id>", methods=["GET"])
def get_cliente_by_becus(becus_id):
    cliente = Cliente.query.filter_by(becus_id=becus_id).first_or_404()
    return jsonify(cliente.to_dict(include_projetos=True))
