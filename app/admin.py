# app/admin.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.models import db, Machine, Head, User

admin = Blueprint("admin", __name__)

# Decorator to restrict access to admins
def admin_only(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role != 'admin':
            flash("Admins only!")
            return redirect(url_for("main.dashboard"))
        return func(*args, **kwargs)
    return wrapper

# ----------------- MACHINE MANAGEMENT -----------------

@admin.route("/admin/machines", methods=["GET", "POST"])
@login_required
@admin_only
def manage_machines():
    if request.method == "POST":
        machine_name = request.form["machine_name"]
        user_id = int(request.form["user_id"])
        num_heads = int(request.form["num_heads"])

        machine = Machine(name=machine_name, owner_id=user_id)
        db.session.add(machine)
        db.session.commit()

        # Create heads
        for i in range(1, num_heads + 1):
            head = Head(number=i, machine_id=machine.id)
            db.session.add(head)
        db.session.commit()

        flash("✅ Machine added with heads.")
        return redirect(url_for("admin.manage_machines"))

    machines = Machine.query.all()
    users = User.query.filter_by(role='user').all()
    return render_template("admin_machines.html", machines=machines, users=users)

# ----------------- USER MANAGEMENT -----------------

@admin.route("/admin/users", methods=["GET", "POST"])
@login_required
@admin_only
def manage_users():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        if User.query.filter_by(email=email).first():
            flash("⚠️ User already exists.")
        else:
            hashed_pw = generate_password_hash(password)
            new_user = User(email=email, password=hashed_pw, role=role)
            db.session.add(new_user)
            db.session.commit()
            flash("✅ New user created.")

        return redirect(url_for("admin.manage_users"))

    users = User.query.all()
    return render_template("admin_users.html", users=users)
