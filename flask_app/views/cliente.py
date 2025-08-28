from flask import render_template, request



def get_app():
    from flask_app import app
    return app

app = get_app()


@app.route('/system')
def system():
    return render_template('base.html')


@app.route('/system/novo_cliente')
def novo_cliente():
    return render_template('novo_cliente.html')