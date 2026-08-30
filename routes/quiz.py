import os

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from PyPDF2 import PdfReader

from ai.quiz_generator import generate_quiz


quiz_bp = Blueprint("quiz", __name__)

UPLOAD_FOLDER = "uploads"


# =========================================
# QUIZ PAGE + GENERATE QUIZ
# =========================================

@quiz_bp.route("/quiz", methods=["GET", "POST"])
def quiz():

    # -----------------------------
    # Check login
    # -----------------------------

    if "username" not in session:
        return redirect(
            url_for("login.login")
        )


    # -----------------------------
    # Check profile
    # -----------------------------

    if "user_profile" not in session:
        return redirect(
            url_for("profile.profile")
        )


    # -----------------------------
    # GET → Show quiz page
    # -----------------------------

    if request.method == "GET":

        return render_template(
            "quiz.html"
        )


    # =================================
    # POST → Generate Quiz
    # =================================

    pdf_file = request.files.get(
        "learning_material"
    )

    topic = request.form.get(
        "topic",
        ""
    )


    # -----------------------------
    # Check PDF
    # -----------------------------

    if not pdf_file:

        return render_template(
            "quiz.html",
            error="Please upload a PDF."
        )


    if pdf_file.filename == "":

        return render_template(
            "quiz.html",
            error="Please select a PDF."
        )


    if not pdf_file.filename.lower().endswith(".pdf"):

        return render_template(
            "quiz.html",
            error="Only PDF files are allowed."
        )


    # =================================
    # Save PDF
    # =================================

    os.makedirs(
        UPLOAD_FOLDER,
        exist_ok=True
    )


    filepath = os.path.join(
        UPLOAD_FOLDER,
        pdf_file.filename
    )


    pdf_file.save(filepath)


    # =================================
    # Extract PDF Text
    # =================================

    try:

        reader = PdfReader(filepath)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:

                text += page_text + "\n"


    except Exception as e:

        print("PDF ERROR:", e)

        return render_template(
            "quiz.html",
            error="Could not read this PDF."
        )


    # -----------------------------
    # Check extracted text
    # -----------------------------

    if not text.strip():

        return render_template(
            "quiz.html",
            error=(
                "No readable text found in this PDF. "
                "Please upload a text-based PDF."
            )
        )


    print(
        "PDF TEXT LENGTH:",
        len(text)
    )


    # =================================
    # Generate AI Quiz
    # =================================

    quiz_data = generate_quiz(
        text=text,
        topic=topic,
        number_of_questions=10
    )


    # -----------------------------
    # Check AI result
    # -----------------------------

    if not quiz_data:

        return render_template(
            "quiz.html",
            error="AI could not generate the quiz."
        )


    if quiz_data.get("error"):

        print(
            "AI ERROR:",
            quiz_data.get("error")
        )

        return render_template(
            "quiz.html",
            error=(
                "Quiz generation failed. "
                "Please try again."
            )
        )


    questions = quiz_data.get(
        "questions",
        []
    )


    if not questions:

        return render_template(
            "quiz.html",
            error=(
                "AI did not generate any questions. "
                "Please try another PDF."
            )
        )


    # =================================
    # Save quiz temporarily
    # =================================

    session["quiz_data"] = quiz_data


    print(
        "QUESTIONS GENERATED:",
        len(questions)
    )


    # =================================
    # Show Quiz
    # =================================

    return render_template(
        "quiz.html",
        quiz=quiz_data
    )


# =========================================
# SUBMIT QUIZ
# =========================================

@quiz_bp.route(
    "/quiz/submit",
    methods=["POST"]
)
def submit_quiz():

    # -----------------------------
    # Login check
    # -----------------------------

    if "username" not in session:

        return redirect(
            url_for("login.login")
        )


    # -----------------------------
    # Get generated quiz
    # -----------------------------

    quiz_data = session.get(
        "quiz_data"
    )


    if not quiz_data:

        return redirect(
            url_for("quiz.quiz")
        )


    questions = quiz_data.get(
        "questions",
        []
    )


    score = 0


    # =================================
    # Check answers
    # =================================

    for index, question in enumerate(questions):

        user_answer = request.form.get(
            f"question_{index}"
        )


        correct_answer = question.get(
            "correct_answer"
        )


        if user_answer == correct_answer:

            score += 1


    # =================================
    # Calculate Result
    # =================================

    total = len(questions)


    percentage = 0


    if total > 0:

        percentage = round(
            (score / total) * 100
        )


    print(
        "QUIZ RESULT:",
        score,
        "/",
        total
    )


    # =================================
    # Show Result
    # =================================

    return render_template(
        "quiz.html",
        quiz=quiz_data,
        completed=True,
        score=score,
        total=total,
        percentage=percentage
    )