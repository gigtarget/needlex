from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.models import db, User, Machine, Head, NeedleChange

admin = Blueprint("admin", __name__)

def admin_required(f):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return login_required(wrapper)

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

    # Delete associated heads and changes
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
