from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import re

auth = Blueprint('auth', __name__)

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def validate_signup_form(email, first_name, password1, password2):
    if User.query.filter_by(email=email).first():
        return 'Email already exists.'
    if not is_valid_email(email):
        return 'Invalid email format.'
    if len(email) < 4:
        return 'Email must be greater than 4 characters.'
    if len(first_name) < 2:
        return 'First name must be greater than 1 character.'
    if password1 != password2:
        return 'Passwords don\'t match.'
    if len(password1) < 7:
        return 'Password is too short.'
    return None

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            flash('Logged in successfully!', category='success')
            login_user(user, remember=True)
            return redirect(url_for('views.home'))
        else:
            flash('Invalid email or password.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You\'ve successfully logged out', category='success')
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email', '')
        first_name = request.form.get('first_name', '')
        password1 = request.form.get('password1', '')
        password2 = request.form.get('password2', '')

        error = validate_signup_form(email, first_name, password1, password2)
        if error:
            flash(error, category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)