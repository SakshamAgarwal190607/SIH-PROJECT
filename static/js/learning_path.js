document.addEventListener("DOMContentLoaded", function () {

    // =====================================================
    // 1. TRAINING BUTTONS
    // =====================================================

    const trainingButtons =
        document.querySelectorAll(".training-btn");

    trainingButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            // Prevent double clicks
            if (button.dataset.clicked === "true") {
                return;
            }

            button.dataset.clicked = "true";

            // Change button text briefly
            const originalText = button.innerHTML;

            button.innerHTML = "Opening Training ↗";

            // Restore text after a short delay
            setTimeout(function () {

                button.innerHTML = originalText;

                button.dataset.clicked = "false";

            }, 1500);

        });

    });


    // =====================================================
    // 2. SMOOTH SCROLL TO TRAINING
    // =====================================================

    const trainingSection =
        document.getElementById("training");

    if (
        trainingSection &&
        window.location.hash === "#training"
    ) {

        setTimeout(function () {

            trainingSection.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        }, 200);

    }


    // =====================================================
    // 3. REASSESSMENT BUTTON
    // =====================================================

    const reassessmentButton =
        document.querySelector(
            'a[href*="assessment"]'
        );

    if (reassessmentButton) {

        reassessmentButton.addEventListener(
            "click",
            function (event) {

                const confirmed = confirm(
                    "Have you completed your recommended training?\n\nClick OK to continue to reassessment."
                );

                if (!confirmed) {

                    event.preventDefault();

                }

            }
        );

    }


    // =====================================================
    // 4. BACK TO DASHBOARD
    // =====================================================

    const backButton =
        document.querySelector(".back-btn");

    if (backButton) {

        backButton.addEventListener(
            "click",
            function () {

                backButton.innerHTML =
                    "Opening Dashboard...";

            }
        );

    }


    // =====================================================
    // 5. TRAINING CARD ANIMATION
    // =====================================================

    const trainingCards =
        document.querySelectorAll(".training-card");

    trainingCards.forEach(function (card, index) {

        card.style.opacity = "0";
        card.style.transform = "translateY(15px)";

        setTimeout(function () {

            card.style.transition =
                "opacity 0.4s ease, transform 0.4s ease";

            card.style.opacity = "1";
            card.style.transform = "translateY(0)";

        }, 100 + (index * 100));

    });


    // =====================================================
    // 6. ROADMAP CARD ANIMATION
    // =====================================================

    const roadmapCards =
        document.querySelectorAll(".roadmap-card");

    roadmapCards.forEach(function (card, index) {

        card.style.opacity = "0";
        card.style.transform = "translateY(15px)";

        setTimeout(function () {

            card.style.transition =
                "opacity 0.4s ease, transform 0.4s ease";

            card.style.opacity = "1";
            card.style.transform = "translateY(0)";

        }, 150 + (index * 100));

    });


    // =====================================================
    // 7. SCROLL TO TOP ON PAGE LOAD
    // =====================================================

    if (window.location.hash !== "#training") {

        window.scrollTo({
            top: 0,
            behavior: "instant"
        });

    }

});