// ==========================================
// Chess Learning - Stage 2
// Standalone dashboard
// ==========================================


// -------------------------------
// Elements
// -------------------------------

const startProblemButton =
    document.getElementById("startProblemButton");

const chessProblemsCard =
    document.getElementById("chessProblemsCard");

const assistantButton =
    document.getElementById("assistantButton");

const backButton =
    document.getElementById("backButton");

const notification =
    document.getElementById("notification");

const progressPercent =
    document.getElementById("progressPercent");

const progressFill =
    document.getElementById("progressFill");


// -------------------------------
// Temporary progress
// -------------------------------

let chessProgress = 0;


// Load saved progress
const savedProgress =
    localStorage.getItem("chessProgress");

if (savedProgress !== null) {
    chessProgress = Number(savedProgress);
}


// Update progress UI
function updateProgress() {

    progressPercent.textContent =
        `${chessProgress}%`;

    progressFill.style.width =
        `${chessProgress}%`;
}


// -------------------------------
// Notification
// -------------------------------

function showNotification(message) {

    notification.textContent = message;

    notification.classList.add("show");

    setTimeout(() => {

        notification.classList.remove("show");

    }, 3000);
}


// -------------------------------
// Start Chess Problem
// -------------------------------

function startChessProblem() {

    /*
        The actual chess board will be implemented
        in the next stage.

        For now we confirm that the dashboard
        interaction is working.
    */

    showNotification(
        "Chess Problems module is ready for the next stage."
    );
}


// -------------------------------
// Card click
// -------------------------------

chessProblemsCard.addEventListener(
    "click",
    (event) => {

        if (
            event.target.closest(".start-button")
        ) {
            return;
        }

        startChessProblem();
    }
);


// -------------------------------
// Start button
// -------------------------------

startProblemButton.addEventListener(
    "click",
    startChessProblem
);


// -------------------------------
// Assistant
// -------------------------------

assistantButton.addEventListener(
    "click",
    () => {

        showNotification(
            "Chess Assistant will be added later."
        );

    }
);


// -------------------------------
// Back button
// -------------------------------

backButton.addEventListener(
    "click",
    () => {

        showNotification(
            "Integration with the main website will be added later."
        );

    }
);


// -------------------------------
// Initialisation
// -------------------------------

updateProgress();