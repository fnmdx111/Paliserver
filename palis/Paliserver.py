# encoding: utf-8

# Pars Ain't Robust Server
# Parc Ain't Robust Client
from flask import session, request, redirect, url_for, flash
from flask.templating import render_template
import wtforms
from palis import app, db
from palis.forms import LoginForm
from palis.models import User, PaperDispatchEntity


state = {'agent': ''}

@app.route('/')
def index():
    if 'username' in session:
        app.logger.info('user %s logged in' % session['username'])

        return render_template('index.html', name=session['username'], username=session['username'])
        # return 'Logged in as %s%s' % (escape(session['username']), (' by %s' % state['agent']) if state['agent'] else '')
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if 'username' in session and request.method != 'POST':
        return render_template('login.html',
                               banner_message='%s has already logged in' % session['username'],
                               form=form,
                               username=session['username'])

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
            if 'Palient/0.0.a' in request.user_agent.string:
                state['agent'] = 'palient'
            else:
                state['agent'] = request.user_agent.browser

            flash('you were successfully logged in')
            return redirect(url_for('show_list'))

    return render_template('login.html', form=form)


@app.route('/user')
def show_list():
    user = User.query.filter_by(username=session['username']).first()
    for entity in user.papers + user.dispatches:
        entity.force_status_str()

    return render_template('papers.html',
                           pd_entities_to=sorted(user.papers,
                                                 cmp=lambda x, y: cmp(x.dispatch_date, y.dispatch_date),
                                                 reverse=True),
                           pd_entities_from=user.dispatches,
                           username=session['username'])


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
    pass


@app.route('/download', methods=['POST'])
def download_paper():
    pass


@app.route('/withdraw', methods=['POST'])
def withdraw_dispatch():
    pde_id = request.form['pde_id']
    db.session.delete(PaperDispatchEntity.query.filter_by(_id=pde_id).first())

    db.session.commit()

    return redirect(url_for('show_list'))


@app.route('/hasten', methods=['POST'])
def hasten_dispatch():
    pass


@app.route('/logout')
def logout():
    if not session.get('username', None):
        return redirect(url_for('index'))

    app.logger.info('user %s logged out' % session['username'])

    session.pop('username', None)

    return redirect(url_for('index'))


app.secret_key = '''\x8f\xae\x94\xa2\x0b\xcb\x95\xfe\xf9&5\xa4\x9a6\x14\xea5\x84D\xe7'\xcc\x90G'''


if __name__ == '__main__':
    app.run()

