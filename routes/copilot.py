from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    request,
    jsonify
)

from ai.copilot_engine import ask_copilot


copilot_bp = Blueprint(
    "copilot",
    __name__
)


# =========================================================
# AI COPILOT
# =========================================================

@copilot_bp.route(
    "/copilot",
    methods=["GET", "POST"]
)
def copilot():

    # =====================================================
    # CHECK LOGIN
    # =====================================================

    if "username" not in session:

        return redirect(
            url_for("login.login")
        )


    # =====================================================
    # USER CONTEXT
    # =====================================================

    profile = session.get(
        "user_profile",
        {}
    )

    scores = session.get(
        "assessment_scores",
        {}
    )

    skill_gaps = session.get(
        "skill_gaps",
        []
    )

    learning_goal = session.get(
        "learning_goal",
        ""
    )


    # =====================================================
    # EXISTING CONVERSATION
    # =====================================================

    messages = session.get(
        "copilot_messages",
        []
    )


    # =====================================================
    # POST MESSAGE
    # =====================================================

    if request.method == "POST":

        # -------------------------------------------------
        # JSON REQUEST
        # -------------------------------------------------

        if request.is_json:

            data = request.get_json(
                silent=True
            ) or {}

            question = str(
                data.get(
                    "question",
                    ""
                )
            ).strip()


        # -------------------------------------------------
        # NORMAL FORM REQUEST
        # -------------------------------------------------

        else:

            question = str(
                request.form.get(
                    "question",
                    ""
                )
            ).strip()


        # =================================================
        # EMPTY QUESTION
        # =================================================

        if not question:

            if request.is_json:

                return jsonify({

                    "success": False,

                    "error":
                        "Please enter a question."

                }), 400


            return redirect(
                url_for(
                    "copilot.copilot"
                )
            )


        # =================================================
        # KEEP OLD CONVERSATION
        # =================================================
        #
        # IMPORTANT:
        #
        # Send previous messages to AI BEFORE adding
        # the current question.
        #

        previous_conversation = list(
            messages
        )


        # =================================================
        # CALL AI
        # =================================================

        try:

            print("\n")
            print("=" * 70)
            print("AI COPILOT REQUEST")
            print("=" * 70)

            print(
                "Question:",
                question
            )


            answer = ask_copilot(
    question=question,
    profile=profile,
    scores=scores,
    skill_gaps=skill_gaps,
    learning_goal=learning_goal,
    conversation=messages
)


            if answer is None:

                answer = (
                    "I could not generate a response. "
                    "Please try again."
                )


            answer = str(
                answer
            ).strip()


        except Exception as e:

            print("\n")
            print("=" * 70)
            print("COPILOT ROUTE ERROR")
            print("=" * 70)

            print(
                type(e).__name__,
                str(e)
            )

            print("=" * 70)


            answer = (
                "Sorry, I couldn't process your request "
                "right now. Please try again."
            )


        # =================================================
        # SAVE USER MESSAGE
        # =================================================

        messages.append({

            "role": "user",

            "content": question

        })


        # =================================================
        # SAVE AI RESPONSE
        # =================================================

        messages.append({

            "role": "assistant",

            "content": answer

        })


        # =================================================
        # SAVE CHAT
        # =================================================

        session[
            "copilot_messages"
        ] = messages

        session.modified = True


        # =================================================
        # JSON RESPONSE
        # =================================================

        if request.is_json:

            return jsonify({

                "success": True,

                "question":
                    question,

                "answer":
                    answer

            })


        # =================================================
        # NORMAL FORM
        # =================================================

        return redirect(
            url_for(
                "copilot.copilot"
            )
        )


    # =====================================================
    # GET → SHOW COPILOT
    # =====================================================

    return render_template(

        "copilot.html",

        messages=messages,

        profile=profile,

        scores=scores,

        skill_gaps=skill_gaps,

        learning_goal=learning_goal

    )


# =========================================================
# CLEAR CHAT
# =========================================================

@copilot_bp.route(
    "/copilot/clear",
    methods=["GET"]
)
def clear_copilot():

    session.pop(
        "copilot_messages",
        None
    )

    session.modified = True

    return redirect(
        url_for(
            "copilot.copilot"
        )
    )