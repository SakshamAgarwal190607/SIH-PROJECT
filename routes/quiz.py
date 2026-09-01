import os
import json
import uuid

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader

from ai.quiz_generator import generate_quiz


quiz_bp = Blueprint("quiz", __name__)


# =========================================================
# CONFIGURATION
# =========================================================

UPLOAD_FOLDER = "uploads"
QUIZ_STORAGE_FOLDER = os.path.join(
    "instance",
    "quizzes"
)

ALLOWED_EXTENSION = ".pdf"

PASS_PERCENTAGE = 60


# =========================================================
# CREATE REQUIRED FOLDERS
# =========================================================

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    QUIZ_STORAGE_FOLDER,
    exist_ok=True
)


# =========================================================
# HELPER: ALLOWED PDF
# =========================================================

def allowed_file(filename):

    return (
        filename
        and filename.lower().endswith(
            ALLOWED_EXTENSION
        )
    )


# =========================================================
# HELPER: SAVE QUIZ SERVER-SIDE
# =========================================================

def save_quiz(quiz_data):

    quiz_id = str(
        uuid.uuid4()
    )

    filepath = os.path.join(
        QUIZ_STORAGE_FOLDER,
        f"{quiz_id}.json"
    )

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            quiz_data,
            file,
            ensure_ascii=False,
            indent=2
        )

    return quiz_id


# =========================================================
# HELPER: LOAD QUIZ SERVER-SIDE
# =========================================================

def load_quiz(quiz_id):

    if not quiz_id:
        return None

    # Security: only allow UUID-like filename
    safe_id = secure_filename(
        str(quiz_id)
    )

    filepath = os.path.join(
        QUIZ_STORAGE_FOLDER,
        f"{safe_id}.json"
    )

    if not os.path.exists(filepath):
        return None

    try:

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as e:

        print(
            "QUIZ LOAD ERROR:",
            e
        )

        return None


# =========================================================
# HELPER: DELETE QUIZ
# =========================================================

def delete_quiz(quiz_id):

    if not quiz_id:
        return

    safe_id = secure_filename(
        str(quiz_id)
    )

    filepath = os.path.join(
        QUIZ_STORAGE_FOLDER,
        f"{safe_id}.json"
    )

    try:

        if os.path.exists(filepath):

            os.remove(filepath)

    except Exception as e:

        print(
            "QUIZ DELETE ERROR:",
            e
        )


# =========================================================
# QUIZ PAGE
# =========================================================

@quiz_bp.route(
    "/quiz",
    methods=["GET", "POST"]
)
def quiz():

    # -----------------------------------------------------
    # LOGIN
    # -----------------------------------------------------

    if "username" not in session:

        return redirect(
            url_for("login.login")
        )


    # -----------------------------------------------------
    # PROFILE
    # -----------------------------------------------------

    if "user_profile" not in session:

        return redirect(
            url_for("profile.profile")
        )


    # =====================================================
    # GET
    # =====================================================

    if request.method == "GET":

        quiz_id = session.get(
            "quiz_id"
        )

        quiz_data = load_quiz(
            quiz_id
        )

        quiz_result = session.get(
            "quiz_result"
        )

        return render_template(
            "quiz.html",
            quiz=quiz_data,
            result=quiz_result,
            completed=bool(quiz_result)
        )


    # =====================================================
    # POST → GENERATE QUIZ
    # =====================================================

    pdf_file = request.files.get(
        "learning_material"
    )


    topic = request.form.get(
        "topic",
        ""
    ).strip()


    # -----------------------------------------------------
    # NUMBER OF QUESTIONS
    # -----------------------------------------------------

    try:

        number_of_questions = int(
            request.form.get(
                "num_questions",
                5
            )
        )

    except (
        ValueError,
        TypeError
    ):

        number_of_questions = 5


    if number_of_questions not in [
        5,
        10,
        15
    ]:

        number_of_questions = 5


    # =====================================================
    # PDF VALIDATION
    # =====================================================

    if not pdf_file:

        return render_template(
            "quiz.html",
            error="Please upload a PDF."
        )


    if not pdf_file.filename:

        return render_template(
            "quiz.html",
            error="Please select a PDF."
        )


    if not allowed_file(
        pdf_file.filename
    ):

        return render_template(
            "quiz.html",
            error="Only PDF files are allowed."
        )


    # =====================================================
    # SAVE PDF
    # =====================================================

    try:

        filename = secure_filename(
            pdf_file.filename
        )

        filepath = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        pdf_file.save(
            filepath
        )

    except Exception as e:

        print(
            "FILE SAVE ERROR:",
            e
        )

        return render_template(
            "quiz.html",
            error="Could not save the PDF."
        )


    # =====================================================
    # EXTRACT PDF TEXT
    # =====================================================

    try:

        reader = PdfReader(
            filepath
        )

        text_parts = []

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:

                text_parts.append(
                    page_text
                )

        text = "\n".join(
            text_parts
        )

    except Exception as e:

        print(
            "PDF ERROR:",
            e
        )

        return render_template(
            "quiz.html",
            error="Could not read this PDF."
        )


    # =====================================================
    # EMPTY PDF
    # =====================================================

    if not text.strip():

        return render_template(
            "quiz.html",
            error=(
                "No readable text was found in this PDF. "
                "Please upload a text-based PDF."
            )
        )


    # =====================================================
    # GENERATE QUIZ
    # =====================================================

    print()
    print("=" * 65)
    print("GENERATING QUIZ")
    print("=" * 65)
    print(
        "Questions:",
        number_of_questions
    )
    print(
        "Topic:",
        topic or "General"
    )
    print("=" * 65)


    try:

        quiz_data = generate_quiz(

            text=text,

            topic=topic,

            number_of_questions=
                number_of_questions

        )

    except Exception as e:

        print(
            "GENERATION ERROR:",
            e
        )

        return render_template(
            "quiz.html",
            error=(
                "Quiz generation failed. "
                "Please try again."
            )
        )


    # =====================================================
    # AI ERROR
    # =====================================================

    if not quiz_data:

        return render_template(
            "quiz.html",
            error="AI could not generate the quiz."
        )


    if quiz_data.get("error"):

        print(
            "AI ERROR:",
            quiz_data["error"]
        )

        return render_template(
            "quiz.html",
            error=(
                "Quiz generation failed: "
                + str(
                    quiz_data["error"]
                )
            )
        )


    # =====================================================
    # GET QUESTIONS
    # =====================================================

    questions = quiz_data.get(
        "questions",
        []
    )


    if not questions:

        return render_template(
            "quiz.html",
            error="No valid questions generated."
        )


    # =====================================================
    # CLEAN QUIZ
    # =====================================================

    clean_quiz = {

        "topic":
            quiz_data.get(
                "topic",
                topic
            ),

        "questions":
            questions

    }


    # =====================================================
    # DELETE OLD QUIZ
    # =====================================================

    old_quiz_id = session.get(
        "quiz_id"
    )

    if old_quiz_id:

        delete_quiz(
            old_quiz_id
        )


    # =====================================================
    # SAVE NEW QUIZ SERVER-SIDE
    # =====================================================

    try:

        quiz_id = save_quiz(
            clean_quiz
        )

    except Exception as e:

        print(
            "QUIZ SAVE ERROR:",
            e
        )

        return render_template(
            "quiz.html",
            error="Could not save generated quiz."
        )


    # =====================================================
    # STORE ONLY ID IN SESSION
    # =====================================================

    session["quiz_id"] = quiz_id

    session.pop(
        "quiz_result",
        None
    )

    session.modified = True


    # =====================================================
    # DEBUG
    # =====================================================

    print(
        "QUIZ ID:",
        quiz_id
    )

    print(
        "QUESTIONS GENERATED:",
        len(questions)
    )

    print("=" * 65)


    # =====================================================
    # SHOW QUIZ
    # =====================================================

    return render_template(
        "quiz.html",
        quiz=clean_quiz
    )


# =========================================================
# SUBMIT QUIZ
# =========================================================

@quiz_bp.route(
    "/quiz/submit",
    methods=["POST"]
)
def submit_quiz():

    # -----------------------------------------------------
    # LOGIN
    # -----------------------------------------------------

    if "username" not in session:

        return redirect(
            url_for("login.login")
        )


    # =====================================================
    # LOAD QUIZ ID
    # =====================================================

    quiz_id = session.get(
        "quiz_id"
    )


    if not quiz_id:

        print(
            "SUBMIT ERROR: No quiz_id in session."
        )

        return redirect(
            url_for("quiz.quiz")
        )


    # =====================================================
    # LOAD QUIZ
    # =====================================================

    quiz_data = load_quiz(
        quiz_id
    )


    if not quiz_data:

        print(
            "SUBMIT ERROR: Quiz file not found."
        )

        session.pop(
            "quiz_id",
            None
        )

        return redirect(
            url_for("quiz.quiz")
        )


    # =====================================================
    # QUESTIONS
    # =====================================================

    questions = quiz_data.get(
        "questions",
        []
    )


    if not questions:

        return redirect(
            url_for("quiz.quiz")
        )


    # =====================================================
    # SCORE
    # =====================================================

    score = 0

    total = len(
        questions
    )

    results = []


    for index, question in enumerate(
        questions
    ):

        # -------------------------------------------------
        # IMPORTANT
        # Must match HTML:
        #
        # name="question_0"
        # name="question_1"
        # etc.
        # -------------------------------------------------

        user_answer = request.form.get(
            f"question_{index}",
            ""
        ).strip()


        correct_answer = str(
            question.get(
                "correct_answer",
                ""
            )
        ).strip()


        is_correct = (
            bool(user_answer)
            and
            user_answer == correct_answer
        )


        if is_correct:

            score += 1


        results.append({

            "question":
                question.get(
                    "question",
                    ""
                ),

            "selected_answer":
                user_answer
                if user_answer
                else "Not answered",

            "correct_answer":
                correct_answer,

            "is_correct":
                is_correct,

            "explanation":
                question.get(
                    "explanation",
                    ""
                )

        })


    # =====================================================
    # PERCENTAGE
    # =====================================================

    percentage = (

        round(
            (score / total) * 100
        )

        if total

        else 0

    )


    # =====================================================
    # PASS
    # =====================================================

    passed = (
        percentage >= PASS_PERCENTAGE
    )


    # =====================================================
    # FEEDBACK
    # =====================================================

    if percentage >= 80:

        feedback = (
            "Excellent performance! "
            "You have demonstrated strong understanding."
        )

    elif percentage >= 60:

        feedback = (
            "Good performance! "
            "Review the questions you missed "
            "and strengthen those concepts."
        )

    else:

        feedback = (
            "You need more practice. "
            "Review the learning material "
            "and try again."
        )


    # =====================================================
    # RESULT
    # =====================================================

    quiz_result = {

        "score":
            score,

        "total":
            total,

        "percentage":
            percentage,

        "passed":
            passed,

        "feedback":
            feedback,

        "results":
            results

    }


    # =====================================================
    # SAVE RESULT
    # =====================================================

    session["quiz_result"] = quiz_result

    session.modified = True


    # =====================================================
    # DEBUG
    # =====================================================

    print()
    print("=" * 65)
    print("QUIZ SUBMITTED")
    print("=" * 65)
    print(
        "Quiz ID:",
        quiz_id
    )
    print(
        "Score:",
        score,
        "/",
        total
    )
    print(
        "Percentage:",
        percentage,
        "%"
    )
    print(
        "Passed:",
        passed
    )
    print("=" * 65)


    # =====================================================
    # RESULT PAGE
    # =====================================================

    return render_template(
        "quiz.html",
        quiz=quiz_data,
        result=quiz_result,
        completed=True
    )


# =========================================================
# RETAKE QUIZ
# =========================================================

@quiz_bp.route(
    "/quiz/retake"
)
def retake_quiz():

    if "username" not in session:

        return redirect(
            url_for("login.login")
        )


    # -----------------------------------------------------
    # Remove result only.
    #
    # Keep quiz itself so user can retake
    # the same questions.
    # -----------------------------------------------------

    session.pop(
        "quiz_result",
        None
    )

    session.modified = True


    return redirect(
        url_for("quiz.quiz")
    )