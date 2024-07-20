import flask
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify, send_file
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .models import User, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import io
from io import BytesIO

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.index'))
            else:
                flash('Invalid', category='error')
        else:
            flash('Account not found', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        password1 = request.form['password1']
        password2 = request.form['password2']
        email = request.form['email']
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        profile_image = request.files['profile_image']

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already used', category='error')
        elif len(email) < 5:
            flash('Email must be at least 5 characters long', category='error')
        elif len(first_name) == 0 or len(last_name) == 0:
            flash('Name can\'t be empty', category='error')
        elif password1 != password2:
            flash('Passwords do not match', category='error')
        elif len(password1) < 7:
            flash('Password length should be longer than 7 characters', category='error')
        else:
            new_user = User(email=email, first_name=first_name, last_name=last_name,
                            password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()

            if profile_image and allowed_file(profile_image.filename):
                filename = f"{new_user.id}"
                image_data = profile_image.read()
                new_user.image_filename = filename
                new_user.image_data = image_data
                db.session.commit()

            flash('Account created', category='success')
            login_user(new_user, remember=True)
            return redirect(url_for('views.index'))

    return render_template("signup.html", user=current_user)


@auth.route('/api/chats', methods=['POST'])
def send_message():
    data = request.json
    receiver_id = data.get('receiver_id')
    message_text = data.get('message')

    if receiver_id and message_text:
        new_message = Message(sender_id=current_user.id, receiver_id=receiver_id, content=message_text)
        db.session.add(new_message)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': {
                'sender_id': current_user.id,
                'receiver_id': receiver_id,
                'content': message_text,
                'timestamp': new_message.timestamp
            }
        }), 200
    else:
        return jsonify({'error': 'Invalid data'}), 400


@auth.route('/api/chats/<int:user_id>', methods=['GET'])
def get_chats(user_id):
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp).all()

    # Format messages to send as JSON
    formatted_messages = [{
        'sender_id': message.sender_id,
        'receiver_id': message.receiver_id,
        'content': message.content,
        'timestamp': message.timestamp
    } for message in messages]

    return jsonify(formatted_messages), 200


@auth.route('/api/user_images', methods=['GET'])
def get_user_images():
    users = User.query.all()
    user_images = {user.first_name: user.image_data.decode('utf-8') if user.image_data else None for user in users}
    return jsonify(user_images)


@auth.route('/user_images/<int:user_id>')
def user_image(user_id):
    user = User.query.get(user_id)
    if user and user.image_data:
        return send_file(
            BytesIO(user.image_data),
            mimetype='image/jpeg',
            as_attachment=False,
            download_name=user.image_filename
        )
    return redirect(url_for('static', filename='saged.jpg'))


@auth.route('/add_friend_by_email', methods=['POST'])
@login_required
def add_friend_by_email():
    friend_email = request.form.get('friend_email')
    if not friend_email:
        flash('Please provide an email address.', 'error')
        return redirect(url_for('views.friends'))

    friend = User.query.filter_by(email=friend_email).first()
    if friend is None:
        flash('User not found.', 'error')
        return redirect(url_for('views.friends'))

    if friend == current_user:
        flash('You cannot add yourself as a friend.', 'error')
        return redirect(url_for('views.friends'))

    current_user.send_friend_request(friend)
    db.session.commit()
    flash(f'Friend request sent to {friend.first_name} {friend.last_name}.', 'success')
    return redirect(url_for('views.friends'))


@auth.route('/remove_friend_by_email', methods=['POST'])
@login_required
def remove_friend_by_email():
    remove_friend_email = request.form.get('remove_friend_email')
    if not remove_friend_email:
        flash('Please provide an email address.', 'error')
        return redirect(url_for('views.friends'))

    friend = User.query.filter_by(email=remove_friend_email).first()
    if friend is None:
        flash('User not found.', 'error')
        return redirect(url_for('views.friends'))

    if not current_user.is_friend(friend):
        flash(f'{friend.first_name} {friend.last_name} is not your friend.', 'error')
        return redirect(url_for('views.friends'))

    current_user.remove_friend(friend)
    db.session.commit()
    flash(f'You are no longer friends with {friend.first_name} {friend.last_name}.', 'success')
    return redirect(url_for('views.friends'))


@auth.route('/accept_friend/<int:user_id>', methods=['POST'])
@login_required
def accept_friend(user_id):
    sender = User.query.get_or_404(user_id)
    current_user.accept_friend_request(sender)
    db.session.commit()
    flash(f'You are now friends with {sender.first_name} {sender.last_name}.', 'success')
    return redirect(url_for('views.friends'))

