from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

app.debug = True

db = SQLAlchemy(app)

db.create_all()


@app.teardown_request
def shutdown_session(exception=None):
    db.session.remove()


Bootstrap(app)

