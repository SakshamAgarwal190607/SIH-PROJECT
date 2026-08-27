from flask import Blueprint, render_template, request, redirect, url_for, session

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile", methods=["GET", "POST"])
def profile():

    if request.method == "POST":

        # Get data from form
        name = request.form.get("name")
        department = request.form.get("department")
        designation = request.form.get("designation")
        experience = request.form.get("experience")
        education = request.form.get("education")

        # Basic validation
        if not name or not department or not designation:
            return render_template(
                "profile.html",
                error="Please fill all required fields."
            )

        # Temporary storage
        # Later this will be replaced by database
        session["user_profile"] = {
            "name": name,
            "department": department,
            "designation": designation,
            "experience": experience,
            "education": education
        }

        # After saving → Assessment
        return redirect(url_for("assessment.assessment"))

    # GET request
    return render_template("profile.html")