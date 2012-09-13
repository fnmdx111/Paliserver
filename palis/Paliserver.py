# encoding: utf-8

# Pars Ain't Robust Server
# Parc Ain't Robust Client
from flask import session, escape, request, redirect, url_for, flash
from flask.templating import render_template
from palis import app
from palis.forms import LoginForm
from palis.models import User


state = {'agent': ''}

@app.route('/')
def index():
    if 'username' in session:
        app.logger.info('user %s logged in' % session['username'])

        return render_template('index.html', name=session['username'])
        # return 'Logged in as %s%s' % (escape(session['username']), (' by %s' % state['agent']) if state['agent'] else '')
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        logout()

        username, password = request.form['username'], request.form['password']

        if not username in map(lambda user: user.username, User.query.all()):
            return render_template('login.html', username_side_msg='user %s not found' % username, form=LoginForm())
        if not password == User.query.filter_by(username=username).first().password:
            return render_template('login.html', password_side_msg='password does not match', form=LoginForm())

        session['username'] = username
        if 'Palient/0.0.a' in request.user_agent.string:
            state['agent'] = 'palient'
        else:
            state['agent'] = request.user_agent.browser

        flash('you were successfully logged in')
        return redirect(url_for('index'))

    return render_template('login.html', form=LoginForm())


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

