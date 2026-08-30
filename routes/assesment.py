from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session
)

assessment_bp = Blueprint(
    "assessment",
    __name__
)


@assessment_bp.route(
    "/assessment",
    methods=["GET", "POST"]
)
def assessment():

    # =====================================================
    # CHECK LOGIN
    # =====================================================

    if "username" not in session:
        return redirect(
            url_for("login.login")
        )


    # =====================================================
    # CHECK PROFILE
    # =====================================================

    if "user_profile" not in session:
        return redirect(
            url_for("profile.profile")
        )


    # =====================================================
    # GET
    # =====================================================

    if request.method == "GET":

        return render_template(
            "assessment.html"
        )


    # =====================================================
    # POST
    # =====================================================

    try:

        statistics = int(
            request.form.get("statistics", 0)
        )

        interpretation = int(
            request.form.get("interpretation", 0)
        )

        survey = int(
            request.form.get("survey", 0)
        )

        data_analysis = int(
            request.form.get("data_analysis", 0)
        )

        excel = int(
            request.form.get("excel", 0)
        )

        python = int(
            request.form.get("python", 0)
        )

        visualization = int(
            request.form.get("visualization", 0)
        )

        communication = int(
            request.form.get("communication", 0)
        )

        sql = int(
            request.form.get("sql", 0)
        )

        aiml = int(
            request.form.get("aiml", 0)
        )

    except (ValueError, TypeError):

        return render_template(
            "assessment.html",
            error="Please provide valid assessment scores."
        )


    # =====================================================
    # VALIDATE SCORES
    # =====================================================

    scores = {

        "Statistics":
            statistics,

        "Data Interpretation":
            interpretation,

        "Survey & Data Collection":
            survey,

        "Data Analysis":
            data_analysis,

        "Excel":
            excel,

        "Python":
            python,

        "Data Visualization":
            visualization,

        "Communication":
            communication,

        "SQL":
            sql,

        "AI & ML":
            aiml
    }


    # Every score must be between 1 and 5

    for skill, score in scores.items():

        if score < 1 or score > 5:

            return render_template(
                "assessment.html",
                error=f"Invalid score for {skill}."
            )


    # =====================================================
    # LEARNING PREFERENCES
    # =====================================================

    learning_goal = request.form.get(
        "learning_goal",
        ""
    )

    learning_format = request.form.get(
        "learning_format",
        ""
    )


    if not learning_goal:

        return render_template(
            "assessment.html",
            error="Please select your learning goal."
        )


    if not learning_format:

        return render_template(
            "assessment.html",
            error="Please select your learning format."
        )


    # =====================================================
    # SAVE NEW ASSESSMENT
    # =====================================================

    session["assessment_scores"] = scores

    session["learning_goal"] = learning_goal

    session["learning_format"] = learning_format


    # =====================================================
    # VERY IMPORTANT FOR REASSESSMENT
    # =====================================================
    #
    # Remove old AI analysis.
    #
    # Dashboard will therefore analyze the NEW scores.
    #

    session.pop(
        "ai_analysis",
        None
    )


    # Old quiz should also be removed

    session.pop(
        "quiz_data",
        None
    )


    session.modified = True


    print("\n")
    print("=" * 60)
    print("NEW ASSESSMENT SAVED")
    print("=" * 60)

    print("Scores:")
    print(scores)

    print("Learning Goal:")
    print(learning_goal)

    print("Learning Format:")
    print(learning_format)

    print("Old AI analysis cleared.")

    print("=" * 60)


    # =====================================================
    # GO TO DASHBOARD
    # =====================================================

    return redirect(
        url_for("dashboard.dashboard")
    )