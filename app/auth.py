from flask import Blueprint, render_template, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    success = None

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'user')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            error = '⚠️ Email already registered.'
        else:
            new_user = User(
                email=email,
                password=generate_password_hash(password),
                role=role
            )
            db.session.add(new_user)
            db.session.commit()
            success = '✅ Signup successful. You can now log in.'
            return render_template('login.html', success=success)

    return render_template('signup.html', error=error)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    success = request.args.get("success")

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('main.dashboard'))
            else:
                error = "❌ Incorrect password."
        else:
            error = "⚠️ Email does not exist."

    return render_template('login.html', error=error, success=success)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login', success='✅ You have been logged out.'))
