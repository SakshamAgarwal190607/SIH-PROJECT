document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("copilotForm");
    const textarea = document.getElementById("question");
    const sendButton = document.getElementById("sendButton");
    const messagesContainer = document.getElementById("messages");

    if (!form || !textarea || !sendButton || !messagesContainer) {
        console.error("Copilot elements not found.");
        return;
    }


    // =====================================================
    // ADD MESSAGE TO CHAT
    // =====================================================

    function addMessage(role, content) {

        const messageDiv = document.createElement("div");

        messageDiv.className =
            "message " +
            (role === "user"
                ? "user-message"
                : "assistant-message");


        // Avatar

        const avatar = document.createElement("div");

        avatar.className =
            role === "user"
                ? "message-avatar user-avatar"
                : "message-avatar";

        avatar.textContent =
            role === "user"
                ? "U"
                : "🤖";


        // Content

        const contentDiv =
            document.createElement("div");

        contentDiv.className =
            "message-content";


        // Convert new lines safely

        contentDiv.textContent = content;


        if (role === "assistant") {

            messageDiv.appendChild(avatar);

            messageDiv.appendChild(contentDiv);

        } else {

            messageDiv.appendChild(contentDiv);

            messageDiv.appendChild(avatar);

        }


        messagesContainer.appendChild(
            messageDiv
        );


        // Scroll to bottom

        messagesContainer.scrollTop =
            messagesContainer.scrollHeight;
    }


    // =====================================================
    // SHOW LOADING MESSAGE
    // =====================================================

    function showLoading() {

        const loadingDiv =
            document.createElement("div");

        loadingDiv.id =
            "copilot-loading";

        loadingDiv.className =
            "message assistant-message";


        loadingDiv.innerHTML = `
            <div class="message-avatar">
                🤖
            </div>

            <div class="message-content">
                Thinking...
            </div>
        `;


        messagesContainer.appendChild(
            loadingDiv
        );


        messagesContainer.scrollTop =
            messagesContainer.scrollHeight;
    }


    // =====================================================
    // REMOVE LOADING
    // =====================================================

    function removeLoading() {

        const loading =
            document.getElementById(
                "copilot-loading"
            );

        if (loading) {
            loading.remove();
        }
    }


    // =====================================================
    // SUBMIT MESSAGE
    // =====================================================

    form.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const question =
                textarea.value.trim();


            if (!question) {
                return;
            }


            // Disable input

            textarea.disabled = true;

            sendButton.disabled = true;

            sendButton.textContent =
                "Thinking...";


            // Immediately show user message

            addMessage(
                "user",
                question
            );


            // Clear input

            textarea.value = "";


            // Show loading

            showLoading();


            try {

                const response =
                    await fetch(
                        "/copilot",
                        {

                            method: "POST",

                            headers: {

                                "Content-Type":
                                    "application/json",

                                "Accept":
                                    "application/json"

                            },

                            body: JSON.stringify({

                                question:
                                    question

                            })

                        }
                    );


                // Get JSON

                const data =
                    await response.json();


                console.log(
                    "Copilot response:",
                    data
                );


                removeLoading();


                // Check response

                if (!response.ok ||
                    !data.success) {

                    throw new Error(
                        data.error ||
                        "Something went wrong."
                    );
                }


                // Add AI response

                addMessage(
                    "assistant",
                    data.answer
                );


            } catch (error) {

                console.error(
                    "Copilot error:",
                    error
                );


                removeLoading();


                addMessage(

                    "assistant",

                    "Sorry, I couldn't process your request. " +
                    "Please try again."

                );

            }


            // Enable input

            textarea.disabled = false;

            sendButton.disabled = false;

            sendButton.textContent =
                "Send ↑";


            textarea.focus();

        }
    );


    // =====================================================
    // ENTER TO SEND
    // SHIFT + ENTER = NEW LINE
    // =====================================================

    textarea.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                form.requestSubmit();

            }

        }
    );


    // =====================================================
    // AUTO RESIZE TEXTAREA
    // =====================================================

    textarea.addEventListener(
        "input",
        function () {

            this.style.height = "auto";

            this.style.height =
                this.scrollHeight + "px";

        }
    );


    // =====================================================
    // SUGGESTION BUTTONS
    // =====================================================

    const suggestions =
        document.querySelectorAll(
            ".suggestion"
        );


    suggestions.forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    textarea.value =
                        this.textContent.trim();

                    textarea.focus();

                    form.requestSubmit();

                }
            );

        }
    );

});