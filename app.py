from flask import Flask, render_template

# Create a Flask Instance

app = Flask(__name__)

# Create a route decorator


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user/<name>')
def user(name):
    favorite_pizzas = ['Pepperoni', 'Barbacoa', 'Cheese']
    return render_template('user.html',
                           name=name,
                           favorite_pizzas=favorite_pizzas)


# Create custom error pages


#Invalid Url
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Server Error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run()