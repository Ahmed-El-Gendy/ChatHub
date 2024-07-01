"""from flask import Blueprint, render_template, request, jsonify, redirect, url_for

views = Blueprint('views', __name__)


@views.route('/')
def hello_world():  # put application's code here
    return render_template('index.html', name='Saged Rayan', ch=['ahmed', 'ramez', 'sir'])


@views.route('/profile/<username>')
def profile(username):
    return render_template('index.html', name=username)


@views.route('/profiles/')
def profile1():
    args = request.args
    name = args.get('name')
    return render_template('index.html', name=name)


@views.route('/json')
def get_json():
    return jsonify({'message': 'Hello World!'})


@views.route('/data')
def get_data():
    data = request.json
    return jsonify(data)


@views.route('/go-to-home')
def go_to_home():
    return redirect(url_for('views.get_json'))"""

from flask import Blueprint, render_template

views = Blueprint('views', __name__)


@views.route('/')
def home():
    return render_template("home.html")
