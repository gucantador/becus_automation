from flask import jsonify, request
from ..models import db, Projeto, Observacao, Correcao, Cliente
from ..utils import prazo, Status, Actions


def get_app():
    from flask_app import app
    return app

app = get_app()


# -------------------------------
# POST - Cadastrar Projeto
# -------------------------------
@app.route("/projetos", methods=["POST"])
def create_projeto():
    data = request.get_json()
    prazo_entrega = prazo(data.get('solicitacao'), 4).strftime("%d/%m/%Y")
    if data.get("status") is None:
        data["status"] = Status.AGENDAR.value
        


    try:
        projeto = Projeto(
            solicitacao=data["solicitacao"],
            prazo=prazo_entrega,
            visita=data.get("visita"),
            desenhista=data.get("desenhista"),
            revisor=data.get("revisor"),
            data_entrega=data.get("data_entrega"),
            art=data.get("art"),
            status=data.get("status"),
            cliente_id=data["cliente_id"]
        )
        db.session.add(projeto)
        db.session.commit()

        Actions.log_action(user_id=data.get("user_id"), project_id=projeto.id, action=Actions.CRIAR_PROJETO)
        
        return jsonify({
            "message": "Projeto criado com sucesso",
            "projeto": projeto.to_dict(include_cliente=True)
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# -------------------------------
# PUT - Atualizar Projeto
# -------------------------------
@app.route("/projetos/<int:projeto_id>", methods=["PUT"])
def update_projeto(projeto_id):
    projeto = Projeto.query.get_or_404(projeto_id)
    data = request.get_json()

    # Guarda o status antigo ANTES de atualizar
    status_anterior = projeto.status  

    # Atualiza os campos
    projeto.solicitacao = data.get("solicitacao", projeto.solicitacao)
    projeto.prazo = data.get("prazo", projeto.prazo)
    projeto.visita = data.get("visita", projeto.visita)
    projeto.desenhista = data.get("desenhista", projeto.desenhista)
    projeto.revisor = data.get("revisor", projeto.revisor)
    projeto.data_entrega = data.get("data_entrega", projeto.data_entrega)
    projeto.art = data.get("art", projeto.art)
    projeto.status = data.get("status", projeto.status)
    projeto.cliente_id = data.get("cliente_id", projeto.cliente_id)

    db.session.commit()

    # Sempre registra atualização
    Actions.log_action(
        user_id=data.get("user_id"),
        project_id=projeto.id,
        action=Actions.ATUALIZAR_PROJETO
    )

    # Se mudou só o status
    if status_anterior != projeto.status:
        Actions.log_action(
            user_id=data.get("user_id"),
            project_id=projeto.id,
            action=Actions.update_status(status_anterior, projeto.status)
        )

    return jsonify({
        "message": "Projeto atualizado com sucesso",
        "projeto": projeto.to_dict(include_cliente=True)
    })


# -------------------------------
# GET - Projetos de um Cliente
# -------------------------------
@app.route("/clientes/<int:cliente_id>/projetos", methods=["GET"])
def get_projetos_by_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)

    # pega todos os projetos do cliente
    projetos = Projeto.query.filter_by(cliente_id=cliente.id).all()

    return jsonify({
        "cliente": cliente.to_dict(),
        "projetos": [p.to_dict(include_cliente=False) for p in projetos]
    })


# -------------------------------
# GET - Projeto por ID
# -------------------------------
@app.route("/projetos/<int:projeto_id>", methods=["GET"])
def get_projeto_by_id(projeto_id):
    projeto = Projeto.query.get_or_404(projeto_id)
    return jsonify(projeto.to_dict(include_cliente=True, include_history=True))


# -------------------------------
# GET - Projetos por status
# -------------------------------
@app.route("/projetos/status/<string:status>", methods=["GET"])
def get_projetos_by_status(status):
    projetos = Projeto.query.filter(Projeto.status.ilike(f"%{status}%")).all()
    return jsonify([p.to_dict(include_cliente=True) for p in projetos])


# -------------------------------
# GET - Listar todos os Projetos
# -------------------------------
@app.route("/projetos", methods=["GET"])
def get_all_projetos():
    projetos = Projeto.query.all()
    return jsonify([p.to_dict(include_cliente=True) for p in projetos])


# -------------------------------
# DELETE - Remover Projeto
# -------------------------------
@app.route("/projetos/<int:projeto_id>", methods=["DELETE"])
def delete_projeto(projeto_id):
    projeto = Projeto.query.get_or_404(projeto_id)
    db.session.delete(projeto)
    db.session.commit()
    return jsonify({"message": f"Projeto {projeto_id} deletado com sucesso"})



# -------------------------------
# POST - Adicionar Correção
# -------------------------------
@app.route("/projetos/<int:projeto_id>/correcoes", methods=["POST"])
def add_correcao(projeto_id):
    projeto = Projeto.query.get_or_404(projeto_id)
    data = request.get_json()
    try:
        correcao = Correcao(
            descricao=data["descricao"],
            status=data.get("corrigida", False),
            projeto_id=projeto.id
        )
        db.session.add(correcao)
        db.session.commit()
        return jsonify({
            "message": "Correção adicionada com sucesso",
            "correcao": correcao.to_dict()
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# -------------------------------
# PUT - Atualizar Correção
# -------------------------------
@app.route("/projetos/<int:projeto_id>/correcoes/<int:correcao_id>", methods=["PUT"])
def update_correcao(projeto_id, correcao_id):
    correcao = Correcao.query.filter_by(id=correcao_id, projeto_id=projeto_id).first_or_404()
    data = request.get_json()

    correcao.descricao = data.get("descricao", correcao.descricao)
    correcao.status = data.get("corrigida", correcao.status)

    db.session.commit()
    return jsonify({
        "message": "Correção atualizada com sucesso",
        "correcao": correcao.to_dict()
    })


# -------------------------------
# GET - Listar Correções de um Projeto
# -------------------------------
@app.route("/projetos/<int:projeto_id>/correcoes", methods=["GET"])
def get_correcoes(projeto_id):
    projeto = Projeto.query.get_or_404(projeto_id)
    return jsonify([c.to_dict() for c in projeto.correcoes])


# -------------------------------
# DELETE - Remover Correção
# -------------------------------
@app.route("/projetos/<int:projeto_id>/correcoes/<int:correcao_id>", methods=["DELETE"])
def delete_correcao(projeto_id, correcao_id):
    correcao = Correcao.query.filter_by(id=correcao_id, projeto_id=projeto_id).first_or_404()
    db.session.delete(correcao)
    db.session.commit()
    return jsonify({"message": f"Correção {correcao_id} removida com sucesso"})


# -------------------------------
# POST - Adicionar Observação
# -------------------------------
@app.route("/projetos/<int:projeto_id>/observacoes", methods=["POST"])
def add_observacao(projeto_id):
    projeto = Projeto.query.get_or_404(projeto_id)
    data = request.get_json()
    try:
        observacao = Observacao(
            comentario=data["comentario"],
            user_id=data["user_id"],
            projeto_id=projeto.id
        )
        db.session.add(observacao)
        db.session.commit()
        return jsonify({
            "message": "Observação adicionada com sucesso",
            "observacao": observacao.to_dict(include_user=True)
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# -------------------------------
# PUT - Atualizar Observação
# -------------------------------
@app.route("/projetos/<int:projeto_id>/observacoes/<int:observacao_id>", methods=["PUT"])
def update_observacao(projeto_id, observacao_id):
    observacao = Observacao.query.filter_by(id=observacao_id, projeto_id=projeto_id).first_or_404()
    data = request.get_json()

    observacao.comentario = data.get("comentario", observacao.comentario)
    db.session.commit()

    return jsonify({
        "message": "Observação atualizada com sucesso",
        "observacao": observacao.to_dict(include_user=True)
    })


# -------------------------------
# GET - Listar Observações de um Projeto
# -------------------------------
@app.route("/projetos/<int:projeto_id>/observacoes", methods=["GET"])
def get_observacoes(projeto_id):
    projeto = Projeto.query.get_or_404(projeto_id)
    return jsonify([o.to_dict(include_user=True) for o in projeto.observacoes])


# -------------------------------
# DELETE - Remover Observação
# -------------------------------
@app.route("/projetos/<int:projeto_id>/observacoes/<int:observacao_id>", methods=["DELETE"])
def delete_observacao(projeto_id, observacao_id):
    observacao = Observacao.query.filter_by(id=observacao_id, projeto_id=projeto_id).first_or_404()
    db.session.delete(observacao)
    db.session.commit()
    return jsonify({"message": f"Observação {observacao_id} removida com sucesso"})


@app.route("/api/projetos", methods=["GET"])
def get_projetos():
    filters = request.args
    query = Projeto.query

    # --- trata unidade separadamente ---
    unidades = request.args.getlist("unidade")

    print(unidades)
    if unidades:
        query = query.join(Cliente).filter(Cliente.unidade.in_(unidades))

    # --- demais filtros genéricos ---
    for key, value in filters.items():
        if key == "unidade":
            continue  # já tratamos acima

        if hasattr(Projeto, key) and value.strip():
            column_attr = getattr(Projeto, key)
            if isinstance(column_attr.type, db.String):
                query = query.filter(column_attr.ilike(f"%{value}%"))
            else:
                query = query.filter(column_attr == value)

    projetos = query.all()
    return jsonify([p.to_dict() for p in projetos])
