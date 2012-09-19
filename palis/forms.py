from flask.ext.wtf import Form, FileField
from wtforms import TextField, validators, PasswordField, SelectMultipleField, widgets
from palis import app
from palis.models import User, Paper

class LoginForm(Form, object):
    username = TextField(u'Username', validators=[validators.Required()])
    password = PasswordField(u'Password', validators=[validators.Required()])

    def __init__(self, form, **kwargs):
        super(LoginForm, self).__init__(form, **kwargs)
        self.user = None


    def validate(self):
        request_valid = Form.validate(self)
        if not request_valid:
            return False

        user = User.query.filter_by(username=self.username.data).first()
        if not user:
            self.username.errors.append(u'user %s not found' % self.username.data)
            return False
        if user.password != self.password.data:
            self.password.errors.append(u'password does not match')
            return False

        self.user = user
        return True



class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ForwardForm(Form, object):
    users_selected = MultiCheckboxField()

    def __init__(self, **kwargs):
        super(ForwardForm, self).__init__(**kwargs)



class UploadForm(Form, object):
    title = TextField(u'Title', validators=[validators.Required()])
    author = TextField(u'Author', validators=[validators.Required()])
    paper = FileField(u'Paper')

    def __init__(self, **kwargs):
        super(UploadForm, self).__init__(**kwargs)


    def validate(self):
        request_valid = Form.validate(self)
        if not request_valid:
            return False

        if not self.title.data:
            self.title.errors.append(u'please fill in this field')
            return False
        if not self.author.data:
            self.author.errors.append(u'please fill in this field')
            return False

        paper = Paper.query.filter_by(author=self.author.data,
                                      title=self.title.data).first()
        if paper:
            return False

        return True


