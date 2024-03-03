from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from datetime import timedelta

app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SECRET_KEY'] = 'gffgugbhrnejrj'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(hours=4)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=4)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# set login
login_manager = LoginManager(app)
login_manager.login_view = "login_view"
login_manager.login_message_category = "primary"

from web_app import routes, auth
