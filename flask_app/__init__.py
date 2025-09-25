from flask import Flask
import os

from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__) # creates a flask app with the name of the file as a parameter
CORS(app)
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.secret_key = "secret_key" 
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from flask_app import routes, views