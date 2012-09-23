from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.uploads import UploadSet, DOCUMENTS, TEXT, configure_uploads, os
from flask_bootstrap import Bootstrap

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///palis.db'
app.config['SECRET_KEY'] = '''\x8f\xae\x94\xa2\x0b\xcb\x95\xfe\xf9&5\xa4\x9a6\x14\xea5\x84D\xe7'\xcc\x90G'''


db = SQLAlchemy(app)

Bootstrap(app)

paper_uploader = UploadSet('papers', TEXT + DOCUMENTS + (u'pdf',),
                           default_dest=lambda app: os.path.join(app.instance_path, 'papers'))
configure_uploads(app, (paper_uploader,))


@app.teardown_request
def shutdown_session(exception=None):
    db.session.remove()


