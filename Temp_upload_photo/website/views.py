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

from flask import Blueprint, render_template, jsonify, send_file
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
import io

views = Blueprint('views', __name__)

user_images = {
    'Ramy Rashad': 'ramy.jpg',
    'Ahmed Elgendy': 'gendy.jpg',
    'Abdelrahman Atef': 'atef.jpg',
    'Youssef Khaled': 'youssef.jpg',
    'Ziad Hany': 'ziad.jpg',
}

chats = {
    'Ramy Rashad': [],
    'Ahmed Elgendy': [],
    'Abdelrahman Atef': [],
    'Youssef Khaled': [],
    'Ziad Hany': [],
}


@views.route('/')
@login_required
def index():
    return render_template('home.html', user_images=user_images, chats=chats, user=current_user)


@views.route('/api/user_images', methods=['GET'])
def get_user_images():
    return jsonify(user_images)


@views.route('/api/chats/<user>', methods=['GET'])
def get_user_chats(user):
    return jsonify(chats.get(user, []))


@views.route('/user_image/<int:user_id>')
def user_image(user_id):
    user = User.query.get(user_id)
    if user and user.image_data:
        return send_file(io.BytesIO(user.image_data), mimetype='image/jpeg')
    else:
        return send_file('static/default.jpg', mimetype='image/jpeg')
