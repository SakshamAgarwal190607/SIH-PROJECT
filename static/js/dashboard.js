// =====================================================
// DASHBOARD JAVASCRIPT
// =====================================================


// Scroll to personalized training
function scrollToTraining() {

    const trainingSection =
        document.getElementById("training");

    if (trainingSection) {

        trainingSection.scrollIntoView({
            behavior: "smooth"
        });

    }
}


// =====================================================
// TRAINING BUTTON TRACKING
// =====================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const trainingButtons =
            document.querySelectorAll(
                ".training-btn"
            );


        trainingButtons.forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        console.log(
                            "User opened personalized training:",
                            button.href
                        );

                    }
                );

            }
        );

    }
);