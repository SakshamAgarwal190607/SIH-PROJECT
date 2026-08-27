const loginForm = document.getElementById("loginForm");

const continueBtn = document.getElementById("continueBtn");

const buttonText = document.getElementById("buttonText");


loginForm.addEventListener("submit", function () {

    continueBtn.disabled = true;

    buttonText.textContent = "Saving...";

});