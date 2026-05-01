function showLoader() {
    const loader = document.getElementById("loader");
    if (loader) loader.classList.remove("hidden");
}

function hideLoader() {
    const loader = document.getElementById("loader");
    if (loader) loader.classList.add("hidden");
}

function showClientError(message) {
    alert(message);
}

function validateLogin() {
    const username = document.getElementById("loginUsername").value.trim();
    const password = document.getElementById("loginPassword").value;

    if (!username || !password) {
        showClientError("Please enter username/email and password.");
        return false;
    }

    showLoader();
    return true;
}

function validateRegister() {
    const username = document.getElementById("regUsername").value.trim();
    const email = document.getElementById("regEmail").value.trim();
    const password = document.getElementById("regPassword").value;

    if (!username || !email || !password) {
        showClientError("All fields are required.");
        return false;
    }

    if (password.length < 6) {
        showClientError("Password must be at least 6 characters.");
        return false;
    }

    showLoader();
    return true;
}

function validateReset() {
    const email = document.getElementById("resetEmail").value.trim();
    const password = document.getElementById("resetPassword").value;

    if (!email || !password) {
        showClientError("Email and new password are required.");
        return false;
    }

    if (password.length < 6) {
        showClientError("Password must be at least 6 characters.");
        return false;
    }

    showLoader();
    return true;
}

setTimeout(() => {
    document.querySelectorAll(".flash").forEach(item => {
        item.style.opacity = "0";
        item.style.transform = "translateY(-8px)";
    });
}, 3500);
