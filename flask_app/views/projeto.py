from typing import List
from flask import redirect, render_template, request, session, url_for, flash
from ..utils import Status

from ..models import db, User, Projeto, Cliente


def get_app():
    from flask_app import app
    return app

app = get_app()




@app.route('/system/cliente/<int:client_id>/novo_projeto', methods=['GET'])
def novo_projeto_view(client_id):
    if "user_id" not in session: 
        return redirect(url_for("login"))
    return render_template('novo_projeto.html', client_id=client_id)


@app.route('/system/cliente/<int:client_id>/<int:projeto_id>', methods=['GET'])
def projeto_view(client_id, projeto_id):
    if "user_id" not in session: 
        return redirect(url_for("login"))
    
    users = User.query.all()
    user_list = []
    for user in users:
        name = f"{user.name} {user.last_name or ''}".strip()
        user_list.append(name)




    return render_template(
    'projeto.html', 
    client_id=client_id, 
    projeto_id=projeto_id, 
    status_list=[status.value for status in Status],
    user_list=user_list  # mudou de 'users' para 'user_list'
)



@app.route('/system/projetos', methods=['GET'])
def get_projetos_view():

    if "user_id" not in session: 
        return redirect(url_for("login"))
    
    

    return render_template('projetos.html', status_list=[status.value for status in Status])

@app.route("/table_component/projetos")
def table_component_projetos():

    projetos = get_projetos_result(request)

    print(projetos)

    return render_template("components/table_projeto.html", projetos=projetos)


# retorna um bloco de busca pronto
@app.route("/bloco_busca")
def bloco_busca():
    return render_template("components/modal_status.html", status_list=[status.value for status in Status])






def get_projetos_result(request):
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

    projetos: List[Projeto] = query.all()


    return [projeto for projeto in projetos]


