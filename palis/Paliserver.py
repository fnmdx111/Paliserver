# encoding: utf-8

# Pars Ain't Robust Server
# Parc Ain't Robust Client
from datetime import date
from flask import session, request, redirect, url_for, flash
from flask.templating import render_template
import wtforms
from palis import app, db
from palis.forms import LoginForm, ForwardForm
from palis.models import User, PaperDispatchEntity


state = {'agent': ''}


@app.before_first_request
def init_db(exception=None):
    db.create_all()

    app.jinja_env.globals.update(user_list=User.query.all())


@app.before_request
def init_current_user(exception=None):
    username = session.get('username', None)
    if username:
        user = User.query.filter_by(username=username).first()

        app.jinja_env.globals.update(cur_uid=user._id, cur_username=username)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if 'username' in session and request.method != 'POST':
        return render_template('login.html',
                               banner_message='User %s has already logged in.' % session['username'],
                               form=form)

    if request.method == 'POST' and form.validate_on_submit():
        logout()

        username, password = form.username.data, form.password.data

        user = User.query.filter_by(username=username).first()
        if not user:
            form.username.errors = [wtforms.ValidationError(u'user %s not found' % username)]
        elif not user.password == password:
            form.password.errors = [wtforms.ValidationError(u'password does not match')]
        else:
            session['username'] = username
            app.logger.info('user %s logged in' % session['username'])

            if 'Palient/0.0.a' in request.user_agent.string:
                state['agent'] = 'palient'
            else:
                state['agent'] = request.user_agent.browser

            flash('you were successfully logged in')
            return redirect(url_for('show_list'))

    return render_template('login.html',
                           banner_message='Login for simple paper list service.',
                           form=form)


@app.route('/user')
def show_list():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()
    for entity in user.papers + user.dispatches:
        entity.force_status_str()

    forward_form = ForwardForm()
    forward_form.users_selected.choices = [(u._id, u.username) for u in User.query.all()
                                           if u._id not in (user._id,
                                                            User.query.filter_by(username='admin').first()._id)]

    return render_template('papers.html',
                           pd_entities_to=sorted(user.papers,
                                                 cmp=lambda x, y: cmp(x.dispatch_date, y.dispatch_date),
                                                 reverse=True),
                           pd_entities_from=user.dispatches,
                           forward_form=forward_form)


@app.route('/read', methods=['POST'])
def read_paper():
    pde_id = request.form['pde_id']
    pde = PaperDispatchEntity.query.filter_by(_id=pde_id).first()

    if pde.status == 0x1:
        pde.status = 0x2
    elif pde.status == 0x2:
        pde.status = 0x3

    db.session.commit()

    return redirect(url_for('show_list'))


@app.route('/forward', methods=['POST'])
def forward_paper():
    pde = PaperDispatchEntity.query.filter_by(_id=request.form['pde_id']).first()

    for _, user_id in filter(lambda (x, _): x == 'users_selected',
                             request.form.items()):
        new_pde = PaperDispatchEntity(request.form['from_uid'],
                                      user_id,
                                      pde.paper._id,
                                      0x1,
                                      date.today())
        db.session.add(new_pde)

    db.session.commit()

    return redirect(url_for('show_list'))


@app.route('/download', methods=['POST'])
def download_paper():
    pass


@app.route('/withdraw', methods=['POST'])
def withdraw_dispatch():
    pde_id = request.form['pde_id']
    pde = PaperDispatchEntity.query.filter_by(_id=pde_id).first()

    status = request.form['status']
    if status == 'refuse':
        pde.forward_status = 0x1
    else:
        db.session.delete(PaperDispatchEntity.query.filter_by(_id=pde_id).first())

    db.session.commit()

    return redirect(url_for('show_list'))


@app.route('/hasten', methods=['POST'])
def hasten_dispatch():
    pass


@app.route('/redispatch', methods=['POST'])
def redispatch():
    pde = PaperDispatchEntity.query.filter_by(_id=request.form['pde_id']).first()
    pde.status = 0x1
    pde.forward_status = 0x0
    pde.dispatch_date = date.today()

    db.session.commit()

    return redirect(url_for('show_list'))


@app.route('/logout')
def logout():
    if not session.get('username', None):
        return redirect(url_for('index'))

    app.logger.info('user %s logged out' % session['username'])

    session.pop('username', None)

    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run()

