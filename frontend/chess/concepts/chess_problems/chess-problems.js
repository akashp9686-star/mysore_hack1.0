```javascript
// ========================================
// CHESS.JS
// ========================================
import { Chess } from "https://cdn.jsdelivr.net/npm/chess.js@1.4.0/+esm";

// ========================================
// GLOBAL VARIABLES
// ========================================
let allProblems = [];
let currentProblemIndex = 0;
let currentProblem = null;
let chess = null;
let selectedSquare = null;
let selectedMove = null;

// Progress Tracking Variables
let sessionStats = {
    attempted: 0,
    correctFirstTry: 0,
    streak: 0
};

let currentProblemMistakeMade = false;
let currentProblemSolved = false;

// ========================================
// LOAD PROBLEMS (UPDATED TO USE FASTAPI)
// ========================================
async function loadProblems() {
    try {
        // Load the bundled 75-level problem set so Chess works inside the main website.
        const response = await fetch("../../data/problems.json");

        if (!response.ok) {
            throw new Error(
                `Could not load problems from API. Status: ${response.status}`
            );
        }

        const problems = await response.json();

        // Check if the backend returned an error message
        if (problems.error) {
            throw new Error(problems.error);
        }

        if (!problems || problems.length === 0) {
            throw new Error("No chess problems found.");
        }

        allProblems = problems;
        currentProblemIndex = 0;

        loadProblem(currentProblemIndex);
        updateStatsUI();

    } catch (error) {
        console.error("Chess API loading error:", error);

        document.getElementById("problemTitle").textContent =
            "API Connection Failed";

        document.getElementById("problemDescription").textContent =
            error.message + " (Is the FastAPI backend running?)";
    }
}

// ========================================
// LOAD A PROBLEM
// ========================================
function loadProblem(index) {
    currentProblem = allProblems[index];

    try {
        chess = new Chess(currentProblem.fen);
    } catch (error) {
        console.error("Invalid FEN:", error);

        document.getElementById("problemTitle").textContent =
            "Invalid chess position";

        document.getElementById("problemDescription").textContent =
            error.message;

        return;
    }

    selectedSquare = null;
    selectedMove = null;
    currentProblemMistakeMade = false;
    currentProblemSolved = false;

    // Counter
    document.getElementById("problemCounter").textContent =
        `PROBLEM ${index + 1} OF ${allProblems.length}`;

    // Title
    document.getElementById("problemTitle").textContent =
        currentProblem.title;

    // Difficulty
    document.getElementById("difficulty").textContent =
        currentProblem.difficulty.toUpperCase();

    document.getElementById("difficulty").classList.remove("hidden");

    // Description
    document.getElementById("problemDescription").textContent =
        "Find the best move for White.";

    // Task
    document.getElementById("taskTitle").textContent =
        chess.turn() === "w" ? "White to move" : "Black to move";

    // Show submit button, hide next button
    document.getElementById("submitButton").classList.remove("hidden");
    document.getElementById("nextButton").classList.add("hidden");

    resetUI();
    renderBoard();
}

// ========================================
// RENDER BOARD
// ========================================
function renderBoard() {
    const boardElement = document.getElementById("chessBoard");
    boardElement.innerHTML = "";

    const board = chess.board();

    const pieces = {
        w: {
            k: "♔",
            q: "♕",
            r: "♖",
            b: "♗",
            n: "♘",
            p: "♙"
        },
        b: {
            k: "♚",
            q: "♛",
            r: "♜",
            b: "♝",
            n: "♞",
            p: "♟"
        }
    };

    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {

            const squareData = board[row][col];

            const square = document.createElement("div");
            square.classList.add("chess-square");

            const isDark = (row + col) % 2 === 1;

            square.classList.add(
                isDark ? "dark-square" : "light-square"
            );

            const file = String.fromCharCode(97 + col);
            const rank = 8 - row;

            const squareName = file + rank;

            square.dataset.square = squareName;

            if (squareData) {
                const pieceElement = document.createElement("div");

                pieceElement.classList.add("chess-piece");

                pieceElement.classList.add(
                    squareData.color === "w"
                        ? "white-piece"
                        : "black-piece"
                );

                pieceElement.textContent =
                    pieces[squareData.color][squareData.type];

                square.appendChild(pieceElement);
            }

            square.addEventListener(
                "click",
                () => handleSquareClick(squareName)
            );

            boardElement.appendChild(square);
        }
    }

    if (selectedSquare) {
        highlightLegalMoves(selectedSquare);
    }
}

// ========================================
// HANDLE SQUARE CLICK
// ========================================
function handleSquareClick(square) {

    if (selectedSquare) {

        if (square === selectedSquare) {
            selectedSquare = null;
            selectedMove = null;

            renderBoard();
            updateSelectedMove();

            return;
        }

        const move = {
            from: selectedSquare,
            to: square,
            promotion: "q"
        };

        const legalMoves = chess.moves({
            square: selectedSquare,
            verbose: true
        });

        const legalMove = legalMoves.find(
            m => m.to === square
        );

        if (!legalMove) {
            showFeedback(
                "✗ Illegal move. That piece cannot move there.",
                "error"
            );

            selectedSquare = null;
            selectedMove = null;

            renderBoard();
            updateSelectedMove();

            return;
        }

        selectedMove = move;

        updateSelectedMove();

        selectedSquare = null;

        renderBoard();

        return;
    }

    const piece = chess.get(square);

    if (!piece) {
        showFeedback(
            "Select a chess piece first.",
            "error"
        );

        return;
    }

    if (piece.color !== chess.turn()) {
        showFeedback(
            "It is not that side's turn.",
            "error"
        );

        return;
    }

    const legalMoves = chess.moves({
        square: square
    });

    if (legalMoves.length === 0) {
        showFeedback(
            "That piece has no legal moves.",
            "error"
        );

        return;
    }

    selectedSquare = square;
    selectedMove = null;

    updateSelectedMove();

    renderBoard();
}

// ========================================
// HIGHLIGHT LEGAL MOVES
// ========================================
function highlightLegalMoves(square) {

    const legalMoves = chess.moves({
        square: square,
        verbose: true
    });

    legalMoves.forEach(move => {

        const element = document.querySelector(
            `[data-square="${move.to}"]`
        );

        if (element) {
            element.classList.add("legal-move");
        }
    });

    const selectedElement = document.querySelector(
        `[data-square="${square}"]`
    );

    if (selectedElement) {
        selectedElement.classList.add("selected");
    }
}

// ========================================
// UPDATE SELECTED MOVE
// ========================================
function updateSelectedMove() {

    const element =
        document.getElementById("selectedMove");

    if (!selectedMove) {

        if (selectedSquare) {
            element.textContent =
                `Selected: ${selectedSquare}`;
        } else {
            element.textContent =
                "No move selected";
        }

        return;
    }

    element.textContent =
        `Move: ${selectedMove.from}${selectedMove.to}`;
}

// ========================================
// PROGRESS STATS UI
// ========================================
function updateStatsUI() {

    const accuracy =
        sessionStats.attempted === 0
            ? 0
            : Math.round(
                (sessionStats.correctFirstTry /
                    sessionStats.attempted) *
                100
            );

    document.getElementById("statAccuracy").textContent =
        accuracy + "%";

    document.getElementById("statCorrect").textContent =
        sessionStats.correctFirstTry;

    document.getElementById("statAttempted").textContent =
        sessionStats.attempted;

    document.getElementById("statStreak").textContent =
        sessionStats.streak;
}

// ========================================
// SUBMIT MOVE
// ========================================
function submitMove() {

    if (!currentProblem) return;

    if (!selectedMove) {
        showFeedback(
            "Please select a move first.",
            "error"
        );

        return;
    }

    let moveResult = null;

    try {
        moveResult = chess.move(selectedMove);
    } catch (error) {

        showFeedback(
            "✗ Illegal chess move.",
            "error"
        );

        return;
    }

    if (!moveResult) {

        showFeedback(
            "✗ Illegal chess move.",
            "error"
        );

        return;
    }

    const moveNotation =
        moveResult.from + moveResult.to;

    const correctMoves =
        currentProblem.correct_moves;

    if (correctMoves.includes(moveNotation)) {

        renderBoard();

        showFeedback(
            "✓ Correct! Excellent move.",
            "success"
        );

        if (!currentProblemSolved) {

            sessionStats.attempted++;

            if (!currentProblemMistakeMade) {
                sessionStats.correctFirstTry++;
                sessionStats.streak++;
            }

            currentProblemSolved = true;

            updateStatsUI();
        }

        document
            .getElementById("explanation")
            .classList.remove("hidden");

        document.getElementById("explanationText").textContent =
            currentProblem.explanation;

        document.getElementById("learningTip").textContent =
            currentProblem.learning_tip;

        if (chess.isCheckmate()) {

            document.getElementById("taskDescription").textContent =
                "Checkmate! You solved the puzzle.";

        } else if (chess.isCheck()) {

            document.getElementById("taskDescription").textContent =
                "Correct! The move gives check.";

        } else {

            document.getElementById("taskDescription").textContent =
                "Correct! You found the expected move.";
        }

        selectedMove = null;

        updateSelectedMove();

        document
            .getElementById("submitButton")
            .classList.add("hidden");

        const nextBtn =
            document.getElementById("nextButton");

        nextBtn.classList.remove("hidden");

        if (currentProblemIndex < allProblems.length - 1) {
            nextBtn.textContent = "Next Problem";
        } else {
            nextBtn.textContent = "Finish Module";
        }

        return;
    }

    chess.undo();

    renderBoard();

    showFeedback(
        "✗ Legal move, but not the best move. Try again.",
        "error"
    );

    if (
        !currentProblemSolved &&
        !currentProblemMistakeMade
    ) {
        currentProblemMistakeMade = true;

        sessionStats.streak = 0;

        updateStatsUI();
    }

    selectedMove = null;

    updateSelectedMove();
}

// ========================================
// NEXT PROBLEM
// ========================================
function nextProblem() {

    if (currentProblemIndex < allProblems.length - 1) {

        currentProblemIndex++;

        loadProblem(currentProblemIndex);

    } else {

        alert(
            `Module Complete!\nYou solved ${sessionStats.correctFirstTry} out of ${sessionStats.attempted} problems on the first try.`
        );

        currentProblemIndex = 0;

        sessionStats = {
            attempted: 0,
            correctFirstTry: 0,
            streak: 0
        };

        updateStatsUI();

        loadProblem(currentProblemIndex);
    }
}

// ========================================
// FEEDBACK
// ========================================
function showFeedback(message, type) {

    const feedback =
        document.getElementById("feedback");

    feedback.textContent = message;

    feedback.className =
        `feedback ${type}`;

    feedback.classList.remove("hidden");
}

// ========================================
// RESET UI
// ========================================
function resetUI() {

    selectedSquare = null;
    selectedMove = null;

    document.getElementById("selectedMove").textContent =
        "No move selected";

    document.getElementById("feedback").textContent =
        "";

    document.getElementById("feedback").className =
        "feedback hidden";

    document
        .getElementById("explanation")
        .classList.add("hidden");

    document.getElementById("explanationText").textContent =
        "";

    document.getElementById("taskDescription").textContent =
        "Select a piece and then select its destination square.";
}

// ========================================
// RESET PROBLEM
// ========================================
function resetProblem() {

    if (!currentProblem) return;

    loadProblem(currentProblemIndex);
}

// ========================================
// BUTTON EVENTS
// ========================================
document
    .getElementById("submitButton")
    .addEventListener("click", submitMove);

document
    .getElementById("resetButton")
    .addEventListener("click", resetProblem);

document
    .getElementById("nextButton")
    .addEventListener("click", nextProblem);

// ========================================
// START
// ========================================
loadProblems();
```

The important change is:

```javascript
const response = await fetch("../../data/problems.json");
```

So your FastAPI backend should be running at:

`http://127.0.0.1:8000`
