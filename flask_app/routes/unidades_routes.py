from flask import jsonify, request
from ..models import db, Unidades

from ..utils import  Status


def get_app():
    from flask_app import app
    return app

app = get_app()

# -------------------------------
# POST - Cadastrar Unidade
# -------------------------------
@app.route("/unidades", methods=["POST"])
def create_unidade():
    data = request.get_json()
    try:
        unidade = Unidades(
            name=data["name"]
        )
        db.session.add(unidade)
        db.session.commit()
        return jsonify({"message": "Unidade criada com sucesso", "unidade": unidade.to_dict()}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# -------------------------------
# PUT - Atualizar Unidade
# -------------------------------
@app.route("/unidades/<int:unidade_id>", methods=["PUT"])
def update_unidade(unidade_id):
    unidade = Unidades.query.get_or_404(unidade_id)
    data = request.get_json()
    unidade.name = data.get("name", unidade.name)
    db.session.commit()
    return jsonify({"message": "Unidade atualizada com sucesso", "unidade": unidade.to_dict()})


# -------------------------------
# GET - Unidade por ID
# -------------------------------
@app.route("/unidades/<int:unidade_id>", methods=["GET"])
def get_unidade_by_id(unidade_id):
    unidade = Unidades.query.get_or_404(unidade_id)
    return jsonify(unidade.to_dict())


# -------------------------------
# GET - Unidades por nome (texto parcial)
# -------------------------------
@app.route("/unidades/name/<string:name>", methods=["GET"])
def get_unidades_by_name(name):
    unidades = Unidades.query.filter(Unidades.name.ilike(f"%{name}%")).all()
    return jsonify([u.to_dict() for u in unidades])


# -------------------------------
# POST - Criar Unidades Padrão
# -------------------------------
@app.route("/unidades/populate", methods=["POST"])
def populate_unidades():
    try:
        siglas = [
            "CBR", "CCP", "CPL", "CSJ", "CJD",
            "CES", "CCS", "CBS", "SES", "SLD",
            "SPL", "SMA"
        ]

        created = []
        for sigla in siglas:
            # Verifica se já existe para não duplicar
            if not Unidades.query.filter_by(name=sigla).first():
                unidade = Unidades(name=sigla)
                db.session.add(unidade)
                created.append(sigla)

        db.session.commit()
        return jsonify({
            "message": "Unidades padrão criadas com sucesso",
            "created": created
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

# -------------------------------
# GET - Listar todas as Unidades
# -------------------------------
@app.route("/unidades", methods=["GET"])
def get_all_unidades():
    unidades = Unidades.query.all()
    return jsonify([u.to_dict() for u in unidades])



@app.route("/get_all_status", methods=["GET"])
def get_all_status():
    status_list = [status.value for status in Status]
    return jsonify(status_list)