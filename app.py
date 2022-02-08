from flask import Flask, redirect, render_template, flash, request, url_for

from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms.widgets import TextArea

from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

# Create a Flask Instance

app = Flask(__name__)

# Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# Secret Key
app.config['SECRET_KEY'] = 'mysecretkey'
# Initialize Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Return some JSON
@app.route('/date')
def get_current_date():
    favorite_pizza = {'John': 'Pepperoni', 'Mary': 'Cheese', 'Bob': 'Hawaiian'}
    return favorite_pizza


# Create a Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    favorite_color = db.Column(db.String(50))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create a string

    def __repr__(self):
        return f'User {self.name}'


# Create a Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)


# Create a form class
class UserForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    email = StringField('What is your email?',
                        validators=[Email(), DataRequired()])
    favorite_color = StringField('What is your favorite color?')
    password_hash = PasswordField('What is your password?',
                                  validators=[
                                      DataRequired(),
                                      EqualTo('password_hash2',
                                              message='Passwords must match')
                                  ])
    password_hash2 = PasswordField('Confirm your password',
                                   validators=[DataRequired()])
    submit = SubmitField('Submit')


# Create Post Form
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    content = StringField('Content',
                          validators=[DataRequired()],
                          widget=TextArea())
    author = StringField('Author', validators=[DataRequired()])
    submit = SubmitField('Submit')


# Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        slug = form.slug.data
        content = form.content.data
        author = form.author.data
        post = Posts(title=title, slug=slug, content=content, author=author)
        form.title.data = ''
        form.content.data = ''
        form.slug.data = ''
        form.author.data = ''

        db.session.add(post)
        db.session.commit()
        flash('Your post has been added!', 'success')
    return render_template('add_post.html', form=form)


# Show All Posts Page
@app.route('/all-posts')
def all_posts():
    posts = Posts.query.all()
    return render_template('all_posts.html', posts=posts)


# Show Post Page
@app.route('/show-post/<int:id>')
def show_post(id):
    post = Posts.query.get_or_404(id)
    return render_template('show_post.html', post=post)


# Edit Post Page
@app.route('/edit-post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.slug = form.slug.data
        post.content = form.content.data
        post.author = form.author.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('show_post', id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.slug.data = post.slug
        form.content.data = post.content
        form.author.data = post.author
    return render_template('edit_post.html', form=form, post=post)


# Delete Post Page
@app.route('/delete-post/<int:id>', methods=['POST'])
@login_required
def delete_post(id):
    post = Posts.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('all_posts'))


# Confirmation Delete Post Page
@app.route('/confirm-delete-post/<int:id>')
@login_required
def confirmation_delete_post(id):
    post = Posts.query.get_or_404(id)
    return render_template('confirm_delete_post.html', post=post)


# Create a route decorator


@app.route('/')
def index():
    return render_template('index.html')


# Create custom error pages


#Invalid Url
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Server Error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# Create User Page
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pwd = generate_password_hash(form.password_hash.data,
                                                method='sha256')
            user = Users(name=form.name.data,
                         email=form.email.data,
                         favorite_color=form.favorite_color.data,
                         password_hash=hashed_pwd)
            db.session.add(user)
            db.session.commit()
        else:
            flash('User already exists', 'danger')
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash.data = ''
        flash('User added successfully!', 'success')
    all_users = Users.query.order_by(Users.date_added.desc()).all()
    return render_template('add_user.html',
                           name=name,
                           form=form,
                           all_users=all_users)


# Update User Page
@app.route('/user/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_user(id):
    user = Users.query.get_or_404(id)
    form = UserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user.name = form.name.data
            user.email = form.email.data
            user.favorite_color = form.favorite_color.data
            user.password_hash = form.password_hash.data
            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('add_user'))
        else:
            flash('Error updating user!', 'danger')
    elif request.method == 'GET':
        return render_template('update_user.html', form=form, user=user)


# Delete Confirmation Page
@app.route('/user/confirmation_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def confirmation_delete(id):
    user = Users.query.get_or_404(id)
    return render_template('delete_user.html', user=user)


# Delete User Page
@app.route('/user/delete/<int:id>')
@login_required
def delete_user(id):
    user = Users.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
        return redirect(url_for('add_user'))
    except:
        flash('Error deleting user!', 'danger')
        return redirect(url_for('add_user'))


# Login Form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password_hash = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


# Create Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.email.data:
        if form.validate_on_submit():
            user = Users.query.filter_by(email=form.email.data).first()
            if user:
                # Check the hash
                if check_password_hash(user.password_hash,
                                       form.password_hash.data):
                    login_user(user)
                    flash('You have successfully logged in!', 'success')
                    return redirect(url_for('index'))
                else:
                    flash(
                        'Login unsuccessful. Please check email and password',
                        'danger')
            else:
                flash('This user does not exist', 'danger')
        else:
            flash('Please, put a valid email', 'danger')
    return render_template('login.html', form=form)


# Logout Page
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have successfully logged out!', 'success')
    return redirect(url_for('index'))
