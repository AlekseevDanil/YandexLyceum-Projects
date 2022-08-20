from app import app
from flask import render_template, session, redirect
from models import *
from posts.forms import *

db = DB()
UsersModel(db.get_connection()).init_table()
NewsModel(db.get_connection()).init_table()


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect('/start_menu')
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    session.pop('username', 0)
    session.pop('user_id', 0)
    session.pop('password', 0)
    form = LoginForm()
    if form.validate_on_submit():
        user = form.username.data
        password = form.password.data
        um = UsersModel(db.get_connection())
        exists = um.exists(user, password)
        if (exists[0]):
            session['username'] = user
            session['password'] = password
            session['user_id'] = exists[1]
        else:
            return render_template('log_is_error.html',
                                   title='Авторизация',
                                   form=form)
        return redirect("/")
    return render_template('login.html',
                           title='Авторизация',
                           form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    session.pop('username', 0)
    session.pop('user_id', 0)
    session.pop('password', 0)
    form = RegisterForm()
    if form.validate_on_submit():
        user = form.username.data
        pas = form.password.data
        um = UsersModel(db.get_connection())
        exists = um.exists(user, pas)
        if (exists[0]):
            return render_template('reg_is_error.html',
                                   title='Регистрация',
                                   form=form)
        else:
            um.insert(user, pas)
            exists = um.exists(user, pas)
            session['username'] = user
            session['password'] = pas
            session['user_id'] = exists[1]
        return render_template('reg_is_success.html',
                               title='Ура!',
                               form=form)
    return render_template('register.html',
                           title='Регистрация',
                           form=form)


@app.route('/start_menu')
def start_menu():
    session.pop('username', 0)
    session.pop('password', 0)
    session.pop('user_id', 0)
    return render_template('start_menu.html')


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('password', 0)
    session.pop('user_id', 0)
    return redirect('/start_menu')


@app.errorhandler(404)
def page_notfound(e):
    return render_template('404.html'), 404


@app.route('/admin')
def admin():
    um = UsersModel(db.get_connection()).get_all()
    nm = {}
    for i in NewsModel(db.get_connection()).get_all():
        if i[3] in nm:
            nm[i[3]] += 1
        else:
            nm[i[3]] = 1
    if session['username'] == 'admin' and session['password'] == 'admin':
        return render_template(
            'confidentially/users_admin.html', users=um, len_posts=nm)
    else:
        return render_template('confidentially/base_admin_error.html')


@app.route('/admin/posts')
def admin_posts():
    um = {}
    nm = NewsModel(db.get_connection()).get_all()
    for i in UsersModel(db.get_connection()).get_all():
        if i[0] not in um:
            um[i[0]] = i[1]
    if session['username'] == 'admin' and session['password'] == 'admin':
        return render_template(
            'confidentially/posts_admin.html', users=um, posts=nm)
    else:
        return render_template('confidentially/base_admin_error.html')
