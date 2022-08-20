from flask import Blueprint
from flask import render_template
from models import *
from flask import *
from .forms import PostForm, SortForm, DeletePostForm
from flask import render_template, session, redirect

posts = Blueprint('posts', __name__, template_folder='templates')
db = DB()
UsersModel(db.get_connection()).init_table()
NewsModel(db.get_connection()).init_table()


# создание нового поста
@posts.route('/create', methods=['POST', 'GET'])
def create_post():
    if 'username' not in session:
        return redirect('/start_menu')
    form = PostForm()
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        try:
            NewsModel(db.get_connection()).insert(
                title, body, int(session['user_id']))
        except:
            print('Something wrong')
        return redirect(url_for('posts.index'))
    return render_template('posts/create_post.html', form=form)


# домашня страница
@posts.route('/', methods=['GET', 'POST'])
def index(pages=1):
    if 'username' not in session:
        return redirect('/start_menu')
    form = SortForm()
    q = request.args.get('q')
    posts = []
    page = request.args.get('page')
    if page and page.isdigit():
        page = init(page)
    else:
        page = 1
    if q:
        for i in NewsModel(db.get_connection()).get_all():
            if q.lower() in i[1].lower() or q.lower() in i[2].lower():
                if int(session['user_id']) == int(i[3]):
                    posts.append(i)
    else:
        for i in NewsModel(db.get_connection()).get_all():
            if int(session['user_id']) == int(i[3]):
                posts.append(i)
    if form.validate_on_submit():
        if form.class_.data == 'alph':
            post2 = sorted(posts, key=lambda item: item[1])
            return render_template(
                'posts/index.html', form=form, posts=post2, pages=pages)
    return render_template(
        'posts/index.html', form=form, posts=posts, pages=pages)


# просмотр содержимого поста
@posts.route('/<slug>', methods=['GET', 'POST'])
def post_detail(slug):
    form = DeletePostForm()
    if 'username' not in session:
        return redirect('/start_menu')
    if slug and slug.isdigit():
        post = NewsModel(db.get_connection()).get(int(slug))
        return render_template('posts/post_detail.html', post=post,
                               slug=slug, form=form)
    else:
        return render_template('404.html'), 404


# удаление поста
@posts.route('/delete_post/<slug>', methods=['GET', 'POST'])
def delete_post(slug):
    nm = NewsModel(db.get_connection())
    nm.delete(int(slug))
    return redirect("/blog")
