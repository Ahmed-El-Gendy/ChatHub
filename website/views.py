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

from flask import Blueprint, render_template, jsonify, send_file, request
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Chat
import io
from . import db

views = Blueprint('views', __name__)


@views.route('/home')
@login_required
def index():
    users = User.query.all()
    user_data = {
        user.id: {'first_name': user.first_name, 'last_name': user.last_name, 'image_filename': user.image_filename} for
        user in users}
    return render_template('home.html', user=current_user, user_data=user_data)


@views.route('/')
def home():
    users = User.query.all()
    user_data = {
        user.id: {'first_name': user.first_name, 'last_name': user.last_name, 'image_filename': user.image_filename} for
        user in users}
    return render_template('saged.html', user=current_user, user_data=user_data)


@views.route('/api/user_images', methods=['GET'])
def get_user_images():
    users = User.query.all()
    user_images = {f"{user.first_name} {user.last_name}": user.id for user in users}
    return jsonify(user_images)


@views.route('/api/chats/<int:user_id>', methods=['GET'])
def get_user_chats(user_id):
    chats = Chat.query.filter(
        (Chat.sender_id == current_user.id) & (Chat.receiver_id == user_id) |
        (Chat.sender_id == user_id) & (Chat.receiver_id == current_user.id)
    ).all()
    chat_data = [{'message': chat.message, 'sender_id': chat.sender_id, 'receiver_id': chat.receiver_id} for chat in
                 chats]
    return jsonify(chat_data)


@views.route('/user_image/<int:user_id>')
def user_image(user_id):
    user = User.query.get(user_id)
    if user and user.image_data:
        return send_file(io.BytesIO(user.image_data), mimetype='image/jpeg')
    else:
        return send_file('static/default.jpg', mimetype='image/jpeg')


@views.route('/api/chats', methods=['POST'])
@login_required
def send_chat():
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    message = data.get('message')

    if receiver_id and message:
        new_chat = Chat(sender_id=current_user.id, receiver_id=receiver_id, message=message)
        db.session.add(new_chat)
        db.session.commit()
        return jsonify({'success': True}), 200
    return jsonify({'success': False}), 400
