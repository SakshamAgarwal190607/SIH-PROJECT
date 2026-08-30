from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session
)

from ai.ai_engine import analyze_user
from ai.igot_recommendation import (
    get_training_recommendations
)


dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


# =========================================================
# DASHBOARD
# =========================================================

@dashboard_bp.route(
    "/dashboard",
    methods=["GET"]
)
def dashboard():

    # =====================================================
    # 1. CHECK LOGIN
    # =====================================================

    if "username" not in session:

        return redirect(
            url_for("login.login")
        )


    # =====================================================
    # 2. GET USER PROFILE
    # =====================================================

    profile = session.get(
        "user_profile"
    )

    if not profile:

        return redirect(
            url_for("profile.profile")
        )


    # =====================================================
    # 3. GET LATEST ASSESSMENT
    # =====================================================

    scores = session.get(
        "assessment_scores"
    )

    if not scores:

        return redirect(
            url_for("assessment.assessment")
        )


    # =====================================================
    # 4. LEARNING PREFERENCES
    # =====================================================

    learning_goal = session.get(
        "learning_goal",
        ""
    )

    learning_format = session.get(
        "learning_format",
        ""
    )


    # =====================================================
    # 5. GET AI ANALYSIS
    # =====================================================

    analysis = session.get(
        "ai_analysis"
    )


    # =====================================================
    # 6. GENERATE AI ANALYSIS
    # =====================================================
    #
    # First assessment:
    #       no ai_analysis → generate
    #
    # Reassessment:
    #       assessment.py deletes ai_analysis
    #       → generate again with new scores
    #
    # =====================================================

    if not analysis:

        print()
        print("=" * 60)
        print("AI COMPETENCY ANALYSIS")
        print("=" * 60)

        print("User:")
        print(
            profile.get(
                "name",
                "User"
            )
        )

        print()
        print("Assessment Scores:")
        print(scores)

        print()
        print("Generating AI analysis...")

        try:

            analysis = analyze_user(
                profile=profile,
                scores=scores
            )

        except Exception as e:

            print(
                "AI analysis failed:",
                e
            )

            analysis = {
                "career_goal":
                    "Statistical Data Analyst",

                "career_reason":
                    "Your profile and assessment indicate "
                    "alignment with data and statistical work.",

                "competencies": [],

                "overall_competency_score":
                    0,

                "skill_gaps": [],

                "personalized_roadmap": [],

                "ready_for_quiz":
                    False,

                "overall_feedback":
                    "AI analysis could not be generated. "
                    "Please try refreshing the dashboard."
            }


        # -------------------------------------------------
        # SAVE NEW ANALYSIS
        # -------------------------------------------------

        session["ai_analysis"] = analysis

        session.modified = True

        print()
        print("AI analysis saved.")


    # =====================================================
    # 7. EXTRACT AI DATA
    # =====================================================

    career_goal = analysis.get(
        "career_goal",
        "Career goal not available"
    )


    career_reason = analysis.get(
        "career_reason",
        "No career explanation available."
    )


    competencies = analysis.get(
        "competencies",
        []
    )


    overall_score = analysis.get(
        "overall_competency_score",
        0
    )


    skill_gaps = analysis.get(
        "skill_gaps",
        []
    )


    roadmap = analysis.get(
        "personalized_roadmap",
        []
    )


    ready_for_quiz = analysis.get(
        "ready_for_quiz",
        False
    )


    overall_feedback = analysis.get(
        "overall_feedback",
        ""
    )


    # =====================================================
    # 8. SAFETY CHECK
    # =====================================================
    #
    # Quiz should ONLY be available when there are
    # actually no competency gaps.
    #
    # This prevents AI accidentally returning
    # ready_for_quiz=True while gaps still exist.
    #
    # =====================================================

    if skill_gaps:

        ready_for_quiz = False

    else:

        ready_for_quiz = True


    # =====================================================
    # 9. PERSONALIZED TRAINING
    # =====================================================
    #
    # Send ONLY user's skill gaps to recommendation engine.
    #
    # Example:
    #
    # ["Python", "SQL"]
    #
    # → Python training
    # → SQL training
    #
    # =====================================================

    try:

        training_recommendations = (
            get_training_recommendations(
                skill_gaps
            )
        )

    except Exception as e:

        print(
            "Training recommendation error:",
            e
        )

        training_recommendations = []


    # =====================================================
    # 10. TRAINING REQUIRED
    # =====================================================

    training_required = (
        len(skill_gaps) > 0
    )


    # =====================================================
    # 11. DASHBOARD DATA
    # =====================================================

    dashboard_data = {

        "career_goal":
            career_goal,

        "career_reason":
            career_reason,

        "overall_score":
            overall_score,

        "competencies":
            competencies,

        "skill_gaps":
            skill_gaps,

        "roadmap":
            roadmap,

        "training_recommendations":
            training_recommendations,

        "ready_for_quiz":
            ready_for_quiz,

        "training_required":
            training_required,

        "overall_feedback":
            overall_feedback
    }


    # =====================================================
    # 12. DEBUG INFORMATION
    # =====================================================

    print()
    print("=" * 60)
    print("DASHBOARD RESULT")
    print("=" * 60)

    print(
        "Career Goal:",
        career_goal
    )

    print(
        "Overall Score:",
        overall_score
    )

    print(
        "Skill Gaps:",
        skill_gaps
    )

    print(
        "Training:",
        training_recommendations
    )

    print(
        "Ready For Quiz:",
        ready_for_quiz
    )

    print("=" * 60)
    print()


    # =====================================================
    # 13. RENDER DASHBOARD
    # =====================================================

    return render_template(

        "dashboard.html",

        # -----------------------------------------------
        # USER
        # -----------------------------------------------

        profile=profile,


        # -----------------------------------------------
        # ASSESSMENT
        # -----------------------------------------------

        scores=scores,

        learning_goal=learning_goal,

        learning_format=learning_format,


        # -----------------------------------------------
        # COMPLETE AI ANALYSIS
        # -----------------------------------------------

        analysis=analysis,

        dashboard_data=dashboard_data,


        # -----------------------------------------------
        # CAREER
        # -----------------------------------------------

        career_goal=career_goal,

        career_reason=career_reason,


        # -----------------------------------------------
        # COMPETENCIES
        # -----------------------------------------------

        competencies=competencies,

        overall_score=overall_score,


        # -----------------------------------------------
        # SKILL GAPS
        # -----------------------------------------------

        skill_gaps=skill_gaps,


        # -----------------------------------------------
        # ROADMAP
        # -----------------------------------------------

        roadmap=roadmap,


        # -----------------------------------------------
        # TRAINING
        # -----------------------------------------------

        training_recommendations=(
            training_recommendations
        ),

        training_required=(
            training_required
        ),


        # -----------------------------------------------
        # QUIZ
        # -----------------------------------------------

        ready_for_quiz=(
            ready_for_quiz
        ),


        # -----------------------------------------------
        # FEEDBACK
        # -----------------------------------------------

        overall_feedback=(
            overall_feedback
        )
    )


# =========================================================
# REFRESH DASHBOARD
# =========================================================

@dashboard_bp.route(
    "/dashboard/refresh",
    methods=["GET"]
)
def refresh_dashboard():

    # =====================================================
    # CHECK LOGIN
    # =====================================================

    if "username" not in session:

        return redirect(
            url_for("login.login")
        )


    # =====================================================
    # REMOVE OLD AI ANALYSIS
    # =====================================================

    session.pop(
        "ai_analysis",
        None
    )


    # =====================================================
    # REMOVE OLD QUIZ
    # =====================================================

    session.pop(
        "quiz_data",
        None
    )


    session.modified = True


    print()
    print("=" * 60)
    print("DASHBOARD REFRESHED")
    print("Old AI analysis removed.")
    print("New analysis will be generated.")
    print("=" * 60)
    print()


    # =====================================================
    # REDIRECT TO DASHBOARD
    # =====================================================

    return redirect(
        url_for("dashboard.dashboard")
    )