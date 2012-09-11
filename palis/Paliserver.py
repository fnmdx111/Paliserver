# encoding: utf-8

# Pars Ain't Robust Server
# Parc Ain't Robust Client
from flask import session, escape, request, redirect, url_for
from palis import app


state = {'agent': ''}

@app.route('/')
def index():
    if 'username' in session:
        app.logger.info('user %s logged in' % session['username'])

        return 'Logged in as %s%s' % (escape(session['username']), (' by %s' % state['agent']) if state['agent'] else '')
    # abort(401)
    return 'You are not logged in'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        if 'Palient/0.0.a' in request.user_agent.string:
            state['agent'] = 'palient'
            return redirect(url_for('index'))
        else:
            state['agent'] = request.user_agent.browser
            return redirect(url_for('index'))
    return '''
        <form action="" method="post">
            <p><input type="text" name="username" /></p>
            <p><input type="submit" value="Login" /></p>
        </form>
    '''

@app.route('/logout')
def logout():
    app.logger.info('user %s logged out' % session['username'])

    session.pop('username', None)

    return redirect(url_for('index'))


app.secret_key = '''\x8f\xae\x94\xa2\x0b\xcb\x95\xfe\xf9&5\xa4\x9a6\x14\xea5\x84D\xe7'\xcc\x90G'''


if __name__ == '__main__':
    app.run()

