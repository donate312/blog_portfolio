from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from uuid import uuid4
from .forms import LoginForm
from .models import User, Visitor
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
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            flash('Logged in successfully!', category='success')
            login_user(user, remember=True)
            return redirect(url_for('views.home'))
        else:
            flash('Invalid email or password.', category='error')

    return render_template("login.html", user=current_user, form=form)

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
            is_first_user = User.query.count() == 0
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='pbkdf2:sha256'), is_admin=is_first_user)
            
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

@auth.route('/guest', methods=['GET'])
def guest_login():
    # Create a new guest user
    guest_user = User(
        email=guest_email,
        first_name='Guest',
        password=generate_password_hash('guest_password', method='pbkdf2:sha256'),  # Use a default password for guest users
       # session_id=str(uuid4()),  # Generate a unique session ID
       # ip_address=request.remote_addr,
        is_guest=True
    )
    db.session.add(guest_user)
    db.session.commit()

    # Log in the guest user
    login_user(guest_user, remember=True)
    flash('You are now logged in as a guest.', category='success')
    return redirect(url_for('views.home'))