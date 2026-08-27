const form = document.getElementById("assessmentForm");

const progressFill = document.getElementById("progressFill");

const progressText = document.getElementById("progressText");

const submitBtn = document.getElementById("submitBtn");

const submitText = document.getElementById("submitText");


// ==================================
// TOTAL QUESTIONS
// ==================================

const totalQuestions = 12;


// ==================================
// UPDATE PROGRESS
// ==================================

function updateProgress() {

    let completed = 0;


    // Questions which use radio buttons

    const radioGroups = [

        "statistics",
        "interpretation",
        "survey",

        "data_analysis",
        "excel",
        "python",

        "visualization",
        "communication",
        "sql",
        "aiml",

        "learning_format"

    ];


    // Check every radio question

    radioGroups.forEach(function (groupName) {

        const selected = document.querySelector(
            `input[name="${groupName}"]:checked`
        );


        if (selected) {
            completed++;
        }

    });


    // Check learning goal

    const learningGoal =
        document.querySelector(
            'select[name="learning_goal"]'
        );


    if (learningGoal.value !== "") {
        completed++;
    }


    // Calculate percentage

    const percentage =
        Math.round(
            (completed / totalQuestions) * 100
        );


    // Update progress bar

    progressFill.style.width =
        percentage + "%";


    // Update percentage text

    progressText.textContent =
        percentage + "%";

}


// ==================================
// LISTEN FOR ANSWER CHANGES
// ==================================

form.addEventListener(
    "change",
    updateProgress
);


// Run once when page loads

updateProgress();


// ==================================
// FORM SUBMISSION
// ==================================

form.addEventListener(
    "submit",
    function () {

        submitBtn.disabled = true;

        submitText.textContent =
            "Analyzing your competencies...";

    }
);