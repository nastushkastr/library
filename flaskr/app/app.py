from flask import Flask
from flask_login import LoginManager
from flaskr.config import Config

app = Flask(__name__)
app.config.from_object(Config)
login_manager = LoginManager()
login_manager.init_app(app)
