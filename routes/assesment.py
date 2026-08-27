from flask import Blueprint, render_template, request, redirect, url_for, session

assessment_bp = Blueprint("assessment", __name__)


@assessment_bp.route("/assessment", methods=["GET", "POST"])
def assessment():

    if request.method == "GET":
        return render_template("assessment.html")

    if request.method == "POST":

        statistics = int(request.form.get("statistics", 0))
        interpretation = int(request.form.get("interpretation", 0))
        survey = int(request.form.get("survey", 0))

        data_analysis = int(request.form.get("data_analysis", 0))
        excel = int(request.form.get("excel", 0))
        python = int(request.form.get("python", 0))

        visualization = int(request.form.get("visualization", 0))
        communication = int(request.form.get("communication", 0))
        sql = int(request.form.get("sql", 0))
        aiml = int(request.form.get("aiml", 0))

        learning_goal = request.form.get("learning_goal")
        learning_format = request.form.get("learning_format")

        scores = {
            "Statistics": statistics,
            "Data Interpretation": interpretation,
            "Survey & Data Collection": survey,
            "Data Analysis": data_analysis,
            "Excel": excel,
            "Python": python,
            "Data Visualization": visualization,
            "Communication": communication,
            "SQL": sql,
            "AI & ML": aiml
        }

        skill_gaps = []

        for skill, score in scores.items():

            if score <= 2:
                skill_gaps.append(skill)

        session["assessment_scores"] = scores
        session["skill_gaps"] = skill_gaps

        session["learning_goal"] = learning_goal
        session["learning_format"] = learning_format

        return redirect(url_for("dashboard.dashboard"))