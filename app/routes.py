# app/routes.py

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.models import db, NeedleChange
from datetime import datetime

main = Blueprint("main", __name__)

@main.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "admin":
        return redirect(url_for("admin.manage_machines"))
    else:
        return redirect(url_for("main.user_home"))

@main.route("/user/home")
@login_required
def user_home():
    if current_user.role != "user":
        return redirect(url_for("main.dashboard"))

    machines = current_user.machines

    if len(machines) == 1:
        machine = machines[0]
        return render_template("user_dashboard.html", machine=machine)

    return "Multiple machine support coming soon."  # Optional: show a dropdown later

@main.route("/head/<int:machine_id>/<int:head_id>", methods=["GET", "POST"])
@login_required
def head_view(machine_id, head_id):
    if request.method == "POST":
        needle_number = int(request.form["needle_number"])
        needle_type = int(request.form["needle_type"])

        change = NeedleChange(
            head_id=head_id,
            needle_number=needle_number,
            needle_type=needle_type,
            timestamp=datetime.utcnow()
        )
        db.session.add(change)
        db.session.commit()

        return redirect(url_for("main.head_view", machine_id=machine_id, head_id=head_id))

    logs = (
        NeedleChange.query
        .filter_by(head_id=head_id)  # ✅ FIXED
        .order_by(NeedleChange.timestamp.desc())
        .all()
    )

    last_change_dict = {}
    for log in logs:
        key = log.needle_number
        if key not in last_change_dict:
            last_change_dict[key] = log

    return render_template("head_view.html",
                           machine_id=machine_id,
                           head_id=head_id,
                           last_change_dict=last_change_dict,
                           now=datetime.utcnow())
