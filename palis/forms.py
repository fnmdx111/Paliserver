from flask.ext.wtf import Form
from wtforms import TextField, validators, PasswordField, SelectMultipleField, widgets
from palis import app
from palis.models import User

class LoginForm(Form, object):
    username = TextField(u'Username', validators=[validators.Required()])
    password = PasswordField(u'Password', validators=[validators.Required()])

    def __init__(self, form, **kwargs):
        super(LoginForm, self).__init__(form, **kwargs)



class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ForwardForm(Form, object):
    users_selected = MultiCheckboxField()

    def __init__(self, **kwargs):
        super(ForwardForm, self).__init__(**kwargs)



