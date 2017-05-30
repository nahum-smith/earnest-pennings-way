from flask import Flask, g
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.login import LoginManager, current_user
from flask.ext.bcrypt import Bcrypt
from flask.ext.script import Manager
from flask.ext.sqlalchemy import SQLAlchemy

from config import Configuration # import our configuration file

app = Flask(__name__)
app.config.from_object(Configuration) # use values from our Configuration object
db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

bcrypt = Bcrypt(app)

@app.before_request
def _before_request():
    g.user = current_user
