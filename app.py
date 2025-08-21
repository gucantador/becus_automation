# from flask_app import app


# if __name__ == "__main__":
#     # Rodando na rede local, porta 5000
#     app.run(host="0.0.0.0", port=5000, debug=True)

from waitress import serve
from flask_app import app  # seu app Flask

serve(app, host="0.0.0.0", port=5000)