let questions = [];
let currentIndex = 0;
let answers = {};
let totalSeconds = 300;
let timerInterval = null;
let submitted = false;

const questionBox = document.getElementById("questionBox");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const submitBtn = document.getElementById("submitBtn");
const timerEl = document.getElementById("timer");
const progressEl = document.getElementById("quizProgress");

document.addEventListener("DOMContentLoaded", () => {
    loadQuestions();
    startTimer();

    prevBtn.addEventListener("click", prevQuestion);
    nextBtn.addEventListener("click", nextQuestion);
    submitBtn.addEventListener("click", submitQuiz);
});

// Basic reload/back warning to reduce accidental cheating.
window.addEventListener("beforeunload", (event) => {
    if (!submitted) {
        event.preventDefault();
        event.returnValue = "";
    }
});

history.pushState(null, "", location.href);
window.addEventListener("popstate", () => {
    history.pushState(null, "", location.href);
    alert("Back navigation is disabled during quiz.");
});

async function loadQuestions() {
    try {
        const response = await fetch(`/api/questions/${encodeURIComponent(window.QUIZ_CATEGORY)}`);
        questions = await response.json();

        if (!questions.length) {
            questionBox.innerHTML = "<p>No questions available for this category.</p>";
            return;
        }

        renderQuestion();
    } catch (error) {
        questionBox.innerHTML = "<p>Unable to load questions. Please try again.</p>";
    }
}

function renderQuestion() {
    const q = questions[currentIndex];
    const selected = answers[q.id] || "";

    const optionsHtml = Object.entries(q.options).map(([key, value]) => {
        const active = selected === key ? "selected" : "";
        return `
            <label class="option ${active}" onclick="selectAnswer(${q.id}, '${key}')">
                <input type="radio" name="answer" value="${key}" ${selected === key ? "checked" : ""}>
                <strong>${key}.</strong> ${value}
            </label>
        `;
    }).join("");

    questionBox.innerHTML = `
        <p class="question-meta">Question ${currentIndex + 1} of ${questions.length}</p>
        <h2 class="question-title">${q.question}</h2>
        <div class="options">${optionsHtml}</div>
    `;

    updateButtons();
    updateProgress();
}

function selectAnswer(questionId, option) {
    answers[questionId] = option;
    renderQuestion();
}

function nextQuestion() {
    if (currentIndex < questions.length - 1) {
        currentIndex++;
        renderQuestion();
    }
}

function prevQuestion() {
    if (currentIndex > 0) {
        currentIndex--;
        renderQuestion();
    }
}

function updateButtons() {
    prevBtn.disabled = currentIndex === 0;
    nextBtn.disabled = currentIndex === questions.length - 1;
}

function updateProgress() {
    const percent = ((currentIndex + 1) / questions.length) * 100;
    progressEl.style.width = `${percent}%`;
}

function startTimer() {
    timerInterval = setInterval(() => {
        totalSeconds--;

        const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, "0");
        const seconds = (totalSeconds % 60).toString().padStart(2, "0");
        timerEl.textContent = `${minutes}:${seconds}`;

        if (totalSeconds <= 0) {
            clearInterval(timerInterval);
            submitQuiz();
        }
    }, 1000);
}

async function submitQuiz() {
    if (submitted) return;

    const confirmSubmit = totalSeconds <= 0 || confirm("Submit quiz now?");
    if (!confirmSubmit) return;

    submitted = true;
    clearInterval(timerInterval);
    showLoader();

    const response = await fetch("/submit-quiz", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            category: window.QUIZ_CATEGORY,
            answers: answers
        })
    });

    const data = await response.json();
    window.location.href = data.redirect;
}
