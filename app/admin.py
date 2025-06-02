from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.models import db, User, Machine, Head, NeedleChange

admin = Blueprint("admin", __name__)

def admin_required(f):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return login_required(wrapper)

# ------------------------
# MACHINE MANAGEMENT
# ------------------------

@admin.route("/admin/machines", methods=["GET", "POST"])
@admin_required
def manage_machines():
    if request.method == "POST":
        name = request.form["machine_name"]
        owner_id = request.form["assigned_user"]
        head_count = int(request.form["head_count"])

        new_machine = Machine(name=name, owner_id=owner_id)
        db.session.add(new_machine)
        db.session.commit()

        for i in range(1, head_count + 1):
            head = Head(number=i, machine_id=new_machine.id)
            db.session.add(head)
        db.session.commit()

        return redirect(url_for("admin.manage_machines"))

    machines = Machine.query.all()
    users = User.query.all()

    # Count needle changes per machine
    needle_counts = {}
    for machine in machines:
        head_ids = [head.id for head in machine.heads]
        count = NeedleChange.query.filter(NeedleChange.head_id.in_(head_ids)).count()
        needle_counts[machine.id] = count

    return render_template("admin_machines.html", machines=machines, users=users, needle_counts=needle_counts)


@admin.route("/admin/delete_machine/<int:machine_id>")
@admin_required
def delete_machine(machine_id):
    machine = Machine.query.get_or_404(machine_id)

    for head in machine.heads:
        NeedleChange.query.filter_by(head_id=head.id).delete()
        db.session.delete(head)

    db.session.delete(machine)
    db.session.commit()
    return redirect(url_for("admin.manage_machines"))


@admin.route("/admin/edit_machine/<int:machine_id>", methods=["GET", "POST"])
@admin_required
def edit_machine(machine_id):
    machine = Machine.query.get_or_404(machine_id)
    users = User.query.all()

    if request.method == "POST":
        machine.name = request.form["machine_name"]
        machine.owner_id = request.form["assigned_user"]
        db.session.commit()
        return redirect(url_for("admin.manage_machines"))

    return render_template("edit_machine.html", machine=machine, users=users)


# ------------------------
# USER MANAGEMENT
# ------------------------

@admin.route("/admin/users", methods=["GET", "POST"])
@admin_required
def manage_users():
    if request.method == "POST":
        email = request.form["email"]
        role = request.form["role"]

        if User.query.filter_by(email=email).first():
            return "User already exists."

        new_user = User(
            email=email,
            password=generate_password_hash("default123"),  # Default password
            role=role
        )
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("admin.manage_users"))

    users = User.query.all()
    return render_template("admin_users.html", users=users)


@admin.route("/admin/edit_user/<int:user_id>", methods=["GET", "POST"])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        user.email = request.form["email"]
        user.role = request.form["role"]

        password = request.form.get("password")
        if password:
            user.password = generate_password_hash(password)

        db.session.commit()
        return redirect(url_for("admin.manage_users"))

    return render_template("edit_user.html", user=user)


@admin.route("/admin/delete_user/<int:user_id>")
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.email == current_user.email:
        return "You cannot delete your own account."

    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("admin.manage_users"))
