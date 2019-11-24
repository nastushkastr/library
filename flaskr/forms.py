from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField
from wtforms.fields.html5 import DateTimeField
from wtforms.validators import DataRequired, NumberRange


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class BookForm(FlaskForm):
    title = StringField('Название книги', validators=[DataRequired()])
    genre = StringField('Жанр', validators=[DataRequired()])
    author = StringField('Автор', validators=[DataRequired()])
    count_copies = IntegerField('Количество копий', validators=[DataRequired(), NumberRange(1)])
    price = IntegerField('Цена', validators=[DataRequired(), NumberRange(1)])
    submit = SubmitField('Подтвердить')
