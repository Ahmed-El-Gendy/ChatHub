import flask
from flask import Blueprint, render_template, request, flash

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    data = request.form
    return render_template("login.html")


@auth.route('/logout')
def logout():
    return "<p>Logout</p>"


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        password1 = request.form['password1']
        password2 = request.form['password2']
        email = request.form['email']
        first_name = request.form['firstname']
        last_name = request.form['lastname']

        if len(email) < 5:
            flash('Email must be 4 characters long', category='error')
        elif len(first_name) == 0 or len(last_name) == 0:
            flash('Name can\'t be empty', category='error')
        elif password1 != password2:
            flash('Password should be the same', category='error')
        elif len(password1) < 7:
            flash('Password length should be longer than 7', category='error')
        else:
            flash('Account created', category='success')

    return render_template("signup.html")
