from flask import Blueprint, render_template, request, redirect, url_for
from app.db import db, NeedleChange
from datetime import datetime

main = Blueprint("main", __name__)

@main.route("/head/<int:machine_id>/<int:head_id>", methods=["GET", "POST"])
def head_view(machine_id, head_id):
    last_change = None

    if request.method == "POST":
        needle_number = int(request.form["needle_number"])
        needle_type = int(request.form["needle_type"])

        # Save to DB
        change = NeedleChange(
            machine_id=machine_id,
            head_id=head_id,
            needle_number=needle_number,
            needle_type=needle_type,
            timestamp=datetime.utcnow()
        )
        db.session.add(change)
        db.session.commit()

        return redirect(url_for("main.head_view", machine_id=machine_id, head_id=head_id))

    # Get the last change per needle
    logs = (
        NeedleChange.query
        .filter_by(machine_id=machine_id, head_id=head_id)
        .order_by(NeedleChange.timestamp.desc())
        .all()
    )

    last_change_dict = {}
    for log in logs:
        key = log.needle_number
        if key not in last_change_dict:
            last_change_dict[key] = log  # take the latest one

    return render_template("head_view.html",
                           machine_id=machine_id,
                           head_id=head_id,
                           last_change_dict=last_change_dict)
