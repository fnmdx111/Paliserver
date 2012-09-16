from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = '''\x8f\xae\x94\xa2\x0b\xcb\x95\xfe\xf9&5\xa4\x9a6\x14\xea5\x84D\xe7'\xcc\x90G'''

app.debug = True

db = SQLAlchemy(app)


@app.teardown_request
def shutdown_session(exception=None):
    db.session.remove()


Bootstrap(app)

