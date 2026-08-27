const form = document.getElementById("profileForm");
const button = document.getElementById("saveButton");

form.addEventListener("submit", function () {

    button.disabled = true;

    button.querySelector("span:first-child").textContent =
        "Saving profile...";

});