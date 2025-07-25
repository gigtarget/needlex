from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.models import db, Machine, NeedleChange
from datetime import datetime
import qrcode
import os

main = Blueprint("main", __name__)

@main.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))

@main.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "admin":
        return redirect(url_for("admin.admin_dashboard"))
    else:
        return redirect(url_for("main.user_dashboard"))

@main.route("/user/dashboard")
@login_required
def user_dashboard():
    if current_user.role != "user":
        return redirect(url_for("main.dashboard"))

    machines = current_user.machines
    return render_template("user_dashboard.html", machines=machines)

@main.route("/machine/<int:machine_id>")
@login_required
def view_machine_heads(machine_id):
    machine = Machine.query.get_or_404(machine_id)

    # Security check: users can only view their own machines
    if current_user.role != "admin" and machine.owner_id != current_user.id:
        return "Unauthorized"

    qr_folder = os.path.join("app", "static", "qr_codes")
    os.makedirs(qr_folder, exist_ok=True)

    qr_map = {}

    for head in machine.heads:
        qr_filename = f"qr_machine_{machine.id}_head_{head.id}.png"
        qr_path = os.path.join(qr_folder, qr_filename)

        if not os.path.exists(qr_path):
            qr_url = url_for('main.head_view', machine_id=machine.id, head_id=head.id, _external=True)
            qr = qrcode.QRCode(box_size=4, border=1)
            qr.add_data(qr_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(qr_path)

        qr_map[head.id] = qr_filename

    return render_template("machine_view.html", machine=machine, qr_map=qr_map)

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
        .filter_by(head_id=head_id)
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
