import flask
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

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
            if profile_image and allowed_file(profile_image.filename):
                filename = secure_filename(profile_image.filename)

                # Create the user object without image information first
                new_user = User(email=email, first_name=first_name, last_name=last_name,
                                password=generate_password_hash(password1, method='pbkdf2:sha256'))
                db.session.add(new_user)
                db.session.commit()

                filename = f"{new_user.id}"
                image_data = profile_image.read()

                new_user.image_filename = filename
                new_user.image_data = image_data
                db.session.commit()

                flash('Account created', category='success')
                login_user(new_user, remember=True)
                return redirect(url_for('views.index'))
            else:
                flash('Invalid file type or no file selected', category='error')

    return render_template("signup.html", user=current_user)


