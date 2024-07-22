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

from flask import Blueprint, render_template, jsonify, send_file, request, redirect, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Chat
import io
from . import db
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

views = Blueprint('views', __name__)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@views.route('/home')
@login_required
def index():
    users = User.query.all()
    user_data = {
        user.id: {'first_name': user.first_name, 'last_name': user.last_name, 'image_filename': user.image_filename} for
        user in users}
    return render_template('home.html', user=current_user, user_data=user_data)


@views.route('/friends')
@login_required
def friends():
    users = User.query.all()
    user_data = {
        user.id: {'first_name': user.first_name, 'last_name': user.last_name, 'image_filename': user.image_filename} for
        user in users}
    return render_template('friends.html', user=current_user, user_data=user_data)


@views.route('/')
def home():
    users = User.query.all()
    user_data = {
        user.id: {'first_name': user.first_name, 'last_name': user.last_name, 'image_filename': user.image_filename} for
        user in users}
    return render_template('saged.html', user=current_user, user_data=user_data)


@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        print('Form Data:', request.form)  # Print form data
        print('Files:', request.files)  # Print file data
        if 'update_name' in request.form:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            if first_name and last_name:
                current_user.first_name = first_name
                current_user.last_name = last_name
                db.session.commit()
                flash('Name updated successfully!', 'success')
            else:
                flash('Please provide both first name and last name', 'error')
        elif 'update_password' in request.form:
            password = request.form.get('password')
            if password:
                current_user.password = generate_password_hash(password)
                db.session.commit()
                flash('Password updated successfully!', 'success')
            else:
                flash('Please provide a new password.', 'error')
        elif 'update_photo' in request.form:
            print('Photo Update Requested')
            photo = request.files.get('photo')
            if photo and photo.filename:
                if allowed_file(photo.filename):
                    image_filename = secure_filename(photo.filename)
                    image_data = photo.read()
                    current_user.image_data = image_data
                    current_user.image_filename = image_filename
                    db.session.commit()
                    flash('Profile photo updated successfully!', 'success')
                else:
                    flash('Invalid file type. Please upload a jpg, jpeg, or png image.', 'error')
            else:
                flash('No file uploaded.', 'error')
    users = User.query.all()
    user_data = {
        user.id: {'first_name': user.first_name, 'last_name': user.last_name, 'image_filename': user.image_filename} for
        user in users}
    return render_template('setting.html', user=current_user, user_data=user_data)


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
