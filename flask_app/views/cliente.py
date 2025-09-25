from flask import redirect, render_template, request, session, url_for, flash



def get_app():
    from flask_app import app
    return app

app = get_app()


@app.route('/system')
def system():
    
    return render_template('base.html')


@app.route('/system/novo_cliente')
def novo_cliente():
    if "user_id" not in session: 
        
        return redirect(url_for("login"))
    
    # inserir logica para verificar se é adm
    
    return render_template('novo_cliente.html')


@app.route('/system/get_clientes')
def get_clientes_view():
    if "user_id" not in session: 
        
        return redirect(url_for("login"))
    
    # inserir logica para verificar se é adm

    return render_template('filter_clients.html')


@app.route('/system/cliente/<int:cliente_id>')
def get_cliente(cliente_id):
    if "user_id" not in session: 
        
        return redirect(url_for("login"))
    return render_template('cliente.html', cliente_id=cliente_id)


