document.addEventListener("DOMContentLoaded", function () {

    // =====================================================
    // ELEMENTS
    // =====================================================

    const quizForm = document.getElementById("answerForm");
    const submitButton = document.getElementById("submitQuizBtn");

    const generatorForm = document.getElementById("quizForm");
    const generateButton = document.getElementById("generateBtn");

    const pdfFile = document.getElementById("pdfFile");
    const fileName = document.getElementById("fileName");
    const fileText = document.getElementById("fileText");


    // =====================================================
    // PDF FILE DISPLAY
    // =====================================================

    if (pdfFile) {

        pdfFile.addEventListener("change", function () {

            if (pdfFile.files && pdfFile.files.length > 0) {

                const file = pdfFile.files[0];

                // Show selected filename
                if (fileName) {
                    fileName.textContent = file.name;
                }

                // Change upload text
                if (fileText) {
                    fileText.textContent = "📄 PDF Selected";
                }

            } else {

                if (fileName) {
                    fileName.textContent = "No file selected";
                }

                if (fileText) {
                    fileText.textContent = "📄 Choose PDF";
                }

            }

        });

    }


    // =====================================================
    // GENERATE QUIZ
    // =====================================================

    if (generatorForm) {

        generatorForm.addEventListener("submit", function (event) {

            // Check PDF
            if (!pdfFile || !pdfFile.files || pdfFile.files.length === 0) {

                event.preventDefault();

                alert("Please select a PDF first.");

                return;
            }


            // Check file type
            const file = pdfFile.files[0];

            if (!file.name.toLowerCase().endsWith(".pdf")) {

                event.preventDefault();

                alert("Only PDF files are allowed.");

                return;
            }


            // Prevent multiple clicks
            if (generateButton) {

                generateButton.disabled = true;

                generateButton.textContent =
                    "⏳ Generating Quiz...";

            }

        });

    }


    // =====================================================
    // OPTION SELECTION
    // =====================================================

    const radioButtons = document.querySelectorAll(
        ".option input[type='radio']"
    );


    radioButtons.forEach(function (radio) {

        radio.addEventListener("change", function () {

            // Find current question
            const question =
                radio.closest(".question");

            if (!question) {
                return;
            }


            // Remove selected class
            // ONLY from options of this question
            const questionOptions =
                question.querySelectorAll(".option");


            questionOptions.forEach(function (option) {

                option.classList.remove("selected");

            });


            // Add selected class
            // to clicked option
            const selectedOption =
                radio.closest(".option");


            if (selectedOption) {

                selectedOption.classList.add("selected");

            }

        });

    });


    // =====================================================
    // SUBMIT QUIZ
    // =====================================================

    if (quizForm) {

        quizForm.addEventListener("submit", function (event) {

            const questions =
                quizForm.querySelectorAll(".question");


            let unanswered = [];


            // ---------------------------------------------
            // CHECK EVERY QUESTION
            // ---------------------------------------------

            questions.forEach(function (question) {

                const selected =
                    question.querySelector(
                        "input[type='radio']:checked"
                    );


                if (!selected) {

                    const questionNumber =
                        question.dataset.question;


                    unanswered.push(
                        questionNumber
                    );

                }

            });


            // =================================================
            // UNANSWERED QUESTIONS
            // =================================================

            if (unanswered.length > 0) {

                event.preventDefault();


                // Find first unanswered question
                const firstQuestion =
                    quizForm.querySelector(
                        `.question[data-question="${unanswered[0]}"]`
                    );


                // Scroll to it
                if (firstQuestion) {

                    firstQuestion.scrollIntoView({
                        behavior: "smooth",
                        block: "center"
                    });


                    // Highlight unanswered question
                    firstQuestion.classList.add(
                        "unanswered"
                    );


                    // Remove highlight after 2 seconds
                    setTimeout(function () {

                        firstQuestion.classList.remove(
                            "unanswered"
                        );

                    }, 2000);

                }


                alert(
                    "Please answer all questions before submitting the quiz."
                );


                return;

            }


            // =================================================
            // ALL QUESTIONS ANSWERED
            // =================================================

            if (submitButton) {

                submitButton.disabled = true;

                submitButton.textContent =
                    "⏳ Calculating Score...";

            }


            // IMPORTANT:
            // Do NOT calculate score here.
            //
            // Flask quiz.py will receive the answers
            // and calculate the official score.
            //
            // Therefore we allow normal form submission.

        });

    }


    // =====================================================
    // PREVENT ACCIDENTAL DOUBLE CLICK
    // =====================================================

    if (quizForm && submitButton) {

        submitButton.addEventListener("click", function () {

            if (submitButton.disabled) {

                return;

            }

        });

    }


    // =====================================================
    // DEBUG
    // =====================================================

    console.log(
        "Quiz JavaScript loaded successfully."
    );

});