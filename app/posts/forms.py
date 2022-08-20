from wtforms import Form, StringField, TextAreaField
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired


# форма поста и содержимого
class PostForm(Form):
    title = StringField('Title')
    body = TextAreaField('Body')


# форма входа на сайт
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


# форма регестрации на сайте
class RegisterForm(FlaskForm):
    username = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')


# форма сортировки постов
class SortForm(FlaskForm):
    class_ = SelectField('Sort by:',
                         choices=[
                             ('time', 'date of change'), ('alph', 'alphabet')],
                         validators=[DataRequired()])
    submit = SubmitField('Show')


# форма удаления
class DeletePostForm(Form):
    submit = SubmitField('Delete')
