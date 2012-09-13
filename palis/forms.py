from flask.ext.wtf import Form
from wtforms import TextField, validators, PasswordField

class LoginForm(Form, object):
    username = TextField(u'Username', validators=[validators.Required()])
    password = PasswordField(u'Password', validators=[validators.Required()])

    def __init__(self, **kwargs):
        super(LoginForm, self).__init__(**kwargs)

