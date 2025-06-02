# app/admin.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Machine, Head

admin = Blueprint("admin", __name__)

def admin_only(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role != 'admin':
            flash("Admins only!")
            return redirect(url_for("main.dashboard"))
        return func(*args, **kwargs)
    return wrapper

@admin.route("/admin/machines", methods=["GET", "POST"])
@login_required
@admin_only
def manage_machines():
    if request.method == "POST":
        machine_name = request.form["machine_name"]
        machine = Machine(name=machine_name, owner_id=current_user.id)
        db.session.add(machine)
        db.session.commit()

        # Create 8 heads for the machine
        for i in range(1, 9):
            head = Head(number=i, machine_id=machine.id)
            db.session.add(head)
        db.session.commit()

        flash("✅ Machine and 8 heads added successfully.")
        return redirect(url_for("admin.manage_machines"))

    machines = Machine.query.filter_by(owner_id=current_user.id).all()
    return render_template("admin_machines.html", machines=machines)
