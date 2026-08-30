const pdfFile = document.getElementById("pdfFile");

const fileName = document.getElementById("fileName");

const generateBtn =
    document.getElementById("generateBtn");

const quizForm =
    document.getElementById("quizForm");


pdfFile.addEventListener("change", function () {

    if (pdfFile.files.length > 0) {

        const file = pdfFile.files[0];

        fileName.textContent =
            "Selected: " + file.name;

    } else {

        fileName.textContent =
            "No file selected";
    }

});


quizForm.addEventListener("submit", function () {

    generateBtn.disabled = true;

    generateBtn.textContent =
        "Generating Quiz...";

});