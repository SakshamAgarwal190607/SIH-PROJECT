from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session
)

from ai.igot_recommendation import (
    get_training_recommendations
)


# =========================================================
# BLUEPRINT
# =========================================================

igot_bp = Blueprint(
    "igot_training",
    __name__
)


# =========================================================
# IGOT TRAINING PAGE
# =========================================================

@igot_bp.route(
    "/igot-training",
    methods=["GET"]
)
def igot_training():

    # =====================================================
    # 1. CHECK LOGIN
    # =====================================================

    if "username" not in session:

        return redirect(
            url_for("login.login")
        )


    # =====================================================
    # 2. GET AI ANALYSIS
    # =====================================================
    #
    # Dashboard ke AI analysis me:
    #
    # skill_gaps
    # personalized_roadmap
    #
    # already available hain.
    # =====================================================

    analysis = session.get(
        "ai_analysis",
        {}
    )


    # =====================================================
    # 3. GET SKILL GAPS
    # =====================================================

    skill_gaps = analysis.get(
        "skill_gaps",
        []
    )


    # =====================================================
    # 4. GET PERSONALIZED ROADMAP
    # =====================================================

    roadmap = analysis.get(
        "personalized_roadmap",
        []
    )


    # =====================================================
    # 5. GET USER PROFILE
    # =====================================================

    profile = session.get(
        "user_profile",
        {}
    )


    # =====================================================
    # 6. GENERATE TRAINING RECOMMENDATIONS
    # =====================================================

    recommendations = (
        get_training_recommendations(
            skill_gaps
        )
    )


    # =====================================================
    # 7. SAVE SKILL GAPS
    # =====================================================
    #
    # Future routes ke liye useful.
    # =====================================================

    session["skill_gaps"] = skill_gaps

    session.modified = True


    # =====================================================
    # 8. RENDER LEARNING PATH
    # =====================================================

    return render_template(

        "learning_path.html",

        # User
        profile=profile,

        # Skill gaps
        skill_gaps=skill_gaps,

        # AI roadmap
        roadmap=roadmap,

        # Training
        recommendations=recommendations,

        # Also provide same data with
        # dashboard-friendly name
        training_recommendations=recommendations
    )