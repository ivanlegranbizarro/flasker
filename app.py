from flask import Flask, redirect, render_template, flash, request, url_for

from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

from datetime import datetime

# Create a Flask Instance

app = Flask(__name__)

# Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# Secret Key
app.config['SECRET_KEY'] = 'mysecretkey'
# Initialize Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Create a Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    favorite_color = db.Column(db.String(50))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Create a string

    def __repr__(self):
        return f'User {self.name}'


# Create a form class
class UserForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    email = StringField('What is your email?',
                        validators=[Email(), DataRequired()])
    favorite_color = StringField('What is your favorite color?')
    submit = SubmitField('Submit')


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
            user = Users(name=form.name.data,
                         email=form.email.data,
                         favorite_color=form.favorite_color.data)
            db.session.add(user)
            db.session.commit()
        else:
            flash('User already exists', 'danger')
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        flash('User added successfully!', 'success')
    all_users = Users.query.order_by(Users.date_added.desc()).all()
    return render_template('add_user.html',
                           name=name,
                           form=form,
                           all_users=all_users)


# Update User Page
@app.route('/user/update/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    user = Users.query.get_or_404(id)
    form = UserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user.name = form.name.data
            user.email = form.email.data
            user.favorite_color = form.favorite_color.data
            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('add_user'))
        else:
            flash('Error updating user!', 'danger')
    elif request.method == 'GET':
        return render_template('update_user.html', form=form, user=user)


# Delete Confirmation Page
@app.route('/user/confirmation_delete/<int:id>', methods=['GET', 'POST'])
def confirmation_delete(id):
    user = Users.query.get_or_404(id)
    return render_template('delete_user.html', user=user)


# Delete User Page
@app.route('/user/delete/<int:id>')
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


if __name__ == '__main__':
    app.run()