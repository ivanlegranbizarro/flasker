from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField, PasswordField, FileField
from wtforms.validators import DataRequired, Email, EqualTo

from flask_ckeditor import CKEditorField


# Create a form class
class UserForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    email = StringField('What is your email?',
                        validators=[Email(), DataRequired()])
    favorite_color = StringField('What is your favorite color?')
    about_author = CKEditorField('Tell us about yourself.')
    password_hash = PasswordField('What is your password?',
                                  validators=[
                                      DataRequired(),
                                      EqualTo('password_hash2',
                                              message='Passwords must match')
                                  ])
    password_hash2 = PasswordField('Confirm your password',
                                   validators=[DataRequired()])
    profile_picture = FileField('Upload a profile picture')
    submit = SubmitField('Submit')


# Create Post Form
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    content = CKEditorField('Content', validators=[DataRequired()])
    author = StringField('Author')
    submit = SubmitField('Submit')


# Login Form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password_hash = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


# Search Form
class SearchForm(FlaskForm):
    searched = StringField('Searched', validators=[DataRequired()])
    submit = SubmitField('Search')