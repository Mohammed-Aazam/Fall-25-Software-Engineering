import sys
from flask import Flask
from flask_cors import CORS
from moj.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__, template_folder='../templates')
app.config.from_object(Config)

# Enable CORS for all routes and all origins (*)
CORS(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'  # Tell flask-login which route to redirect to

from moj import routes, models, commands
