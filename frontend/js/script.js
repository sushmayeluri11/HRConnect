document.addEventListener("DOMContentLoaded", function () {

    const hrLoginForm = document.getElementById("hrLoginForm");

    if (hrLoginForm) {

        hrLoginForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const hrId = document.getElementById("hrId").value.trim();
            const password = document.getElementById("password").value.trim();
            const loginMessage = document.getElementById("loginMessage");

            if (!hrId || !password) {
                loginMessage.textContent = "Please enter HR ID and password.";
                return;
            }

            loginMessage.textContent = "Logging in...";

            try {

                const response = await fetch(
                    "http://127.0.0.1:5000/api/login",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            role: "hr",
                            email: "hr@hrconnect.com",
                            password: password
                        })
                    }
                );

                const data = await response.json();

                if (data.success) {

                    loginMessage.textContent = "Login successful!";

                    // Save logged-in user details
                    localStorage.setItem(
                        "hrUser",
                        JSON.stringify(data.user)
                    );

                    // Redirect to HR dashboard
                    window.location.href = "hr-dashboard.html";

                } else {

                    loginMessage.textContent =
                        data.message || "Invalid HR ID or password.";
                }

            } catch (error) {

                console.error("Login Error:", error);

                loginMessage.textContent =
                    "Python backend is not connected.";
            }
        });
    }

});