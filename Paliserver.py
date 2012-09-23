# encoding: utf-8

# Pars Ain't Robust Server
# Parc Ain't Robust Client
from datetime import date
from flask import session, request, redirect, url_for, flash, jsonify, send_from_directory
from flask.ext.uploads import UploadNotAllowed, extension, os
from flask.templating import render_template
from sqlalchemy.exc import IntegrityError
from palis import app, db, paper_uploader
from palis.forms import LoginForm, ForwardForm, UploadForm, RegistrationForm
from palis.misc import gen_filename
from palis.models import User, PaperDispatchEntity, Paper

state = {'agent': ''}


@app.before_first_request
def init_db(_=None):
    db.create_all()

    app.jinja_env.globals.update(user_list=User.query.all())


@app.before_request
def init_current_user(_=None):
    username = session.get('username', None)
    if username:
        user = User.query.filter_by(username=username).first()
        app.jinja_env.globals.update(cur_uid=user._id, cur_username=username)
    else:
        app.jinja_env.globals.update(cur_uid=None, cur_username=None)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin', defaults={'active': 'users'})
@app.route('/admin/active/<active>', methods=['GET', 'POST'])
def admin(active):
    if 'username' not in session or session['username'] != 'admin':
        flash('You are not authorized.')
        return redirect(url_for('login'))

    form = RegistrationForm(request.form)
    success, error = '', ''
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            user = User(form.username.data, form.password.data)
            success = 'User %s added successfully.' % user.username
        elif user.password == form.password.data:
            error = 'This ain\'t login form!'
        else:
            user.password = form.password.data
            success = 'Password modified successfully.'
        db.session.add(user)
        db.session.commit()

    users = filter(lambda user: user.username != 'admin', User.query.all())
    for user in users:
        user.force_statistics()

    return render_template('admin.html',
                           form=form,
                           success=success,
                           error=error,
                           users=users,
                           active=active)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if 'username' in session and request.method != 'POST':
        return render_template('login.html',
                               banner_message='User %s has already logged in.' % session['username'],
                               form=form,
                               login_active=True)

    if request.method == 'POST' and form.validate_on_submit():
        logout()
        session['username'] = form.user.username
        app.logger.info('user %s logged in' % session['username'])

        if 'Palient/0.0.a' in request.user_agent.string:
            state['agent'] = 'palient'
        else:
            state['agent'] = request.user_agent.browser

        flash('you were successfully logged in')
        return redirect(url_for('show_list'))

    return render_template('login.html',
                           banner_message='Login for simple paper list service.',
                           form=form,
                           login_active=True)


@app.route('/user', defaults={'active': 'from'})
@app.route('/user/active/<active>')
def show_list(active):
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
                           forward_form=forward_form,
                           show_list_active=True,
                           active=active)


@app.route('/papers')
def view_papers():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        my_papers = user.uploaded_papers

        forward_form = ForwardForm()
        forward_form.users_selected.choices = [(u._id, u.username) for u in User.query.all()
                                               if u._id not in (user._id,
                                                                User.query.filter_by(username='admin').first()._id)]
    else:
        my_papers = None
        forward_form = None

    all_papers = Paper.query.all()
    for paper in all_papers:
        paper.force_statistics_data()

    return render_template('view_papers.html',
                           paper_all=all_papers,
                           paper_my=my_papers,
                           forward_form=forward_form,
                           view_papers_active=True,
                           logged_in=forward_form) # if logged in, form is always True



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
    if 'username' not in session:
        return redirect(url_for('login'))

    for user_id in request.form['selected_uid'].split(',')[:-1]:
        new_pde = PaperDispatchEntity(request.form['from_uid'],
                                      user_id,
                                      request.form['paper_id'],
                                      0x1,
                                      date.today())
        app.logger.info(new_pde)
        db.session.add(new_pde)
        try:
            db.session.commit()
            app.logger.info('db committed')
        except IntegrityError:
            db.session.rollback()
            app.logger.error('%s already in db' % new_pde)

    return redirect(url_for('show_list'))


@app.route('/validate_paper', methods=['GET'])
def validate_paper():
    title = request.args.get('title', '', type=unicode)
    author = request.args.get('author', '', type=unicode)

    if not title or not author:
        return jsonify(result='incomplete')
    elif Paper.query.filter_by(title=title, author=author).first():
        return jsonify(result='exist')
    return jsonify(result='proceed')


@app.route('/upload', methods=['GET', 'POST'])
def upload_paper():
    if 'username' not in session:
        return redirect(url_for('login'))

    form = UploadForm(form=request.form)

    if request.method == 'POST' and 'paper' in request.files:
        try:
            filename = gen_filename(form.title.data, form.author.data) + '.' + extension(request.files['paper'].filename)
            paper_uploader.save(request.files['paper'], name=filename)
        except UploadNotAllowed:
            return render_template('upload.html',
                                   error='Please select file to upload.',
                                   form=form, upload_paper_active=True)

        paper = Paper(form.author.data, form.title.data, filename, date.today(),
                      User.query.filter_by(username=session['username']).first()._id)
        db.session.add(paper)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.delete(paper)
            return render_template('upload.html', error='Filename already exists.', form=form,
                                   upload_paper_active=True)

        flash('Paper uploaded successfully.')
        return render_template('upload.html', success='Paper uploaded successfully.', form=UploadForm(),
                               upload_paper_active=True)

    return render_template('upload.html', form=form, upload_paper_active=True)


@app.route('/download', methods=['GET'])
def download_paper():
    paper_id = request.args['paper_id']
    app.logger.info(Paper.query.filter_by(_id=paper_id).first().filename)

    return send_from_directory(os.path.join(app.instance_path, 'papers'), Paper.query.filter_by(_id=paper_id).first().filename)


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

    return redirect(url_for('show_list', active='to' if status != 'refuse' else 'from'))


@app.route('/delete', methods=['POST'])
def delete_paper():
    if 'username' not in session:
        flash('You are not authorized.')
        return redirect(url_for('login'))

    paper = Paper.query.filter_by(_id=request.form['paper_id']).first()
    for pde in paper.dispatched_entities:
        db.session.delete(pde)
    db.session.delete(Paper.query.filter_by(_id=request.form['paper_id']).first())
    # TODO add paper removing mechanism if needed
    db.session.commit()

    return redirect(url_for('view_papers'))


@app.route('/delete_user', methods=['POST'])
def delete_user():
    if 'username' not in session or session['username'] != 'admin':
        flash('You are not authorized.')
        return redirect(url_for('login'))

    user = User.query.filter_by(_id=request.form['user_id']).first()
    for pde in user.papers:
        db.session.delete(pde)
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('admin', active='users'))


@app.route('/redispatch', methods=['POST'])
def redispatch():
    pde = PaperDispatchEntity.query.filter_by(_id=request.form['pde_id']).first()
    pde.status = 0x1
    pde.forward_status = 0x0
    pde.dispatch_date = date.today()

    db.session.commit()

    return redirect(url_for('show_list', active='to'))


@app.route('/logout')
def logout():
    if not session.get('username', None):
        return redirect(url_for('index'))

    app.logger.info('user %s logged out' % session['username'])

    session.pop('username', None)

    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run()

