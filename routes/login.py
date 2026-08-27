from flask import Blueprint, render_template, request, redirect, url_for, session

login_bp = Blueprint("login", __name__)


@login_bp.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        email_id = request.form.get("email")

        # Basic validation
        if not username or not email_id:
            return render_template(
                "login.html",
                error="Please enter username and email."
            )

        # Later:
        # Save username and email to database

        # Temporary session storage
        session["username"] = username
        session["email_id"] = email_id

        # Go to profile page
        return redirect(url_for("profile.profile"))

    return render_template("login.html")