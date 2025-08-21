from flask import Flask

from flask_cors import CORS

app = Flask(__name__) # creates a flask app with the name of the file as a parameter
CORS(app)


from flask_app import routes