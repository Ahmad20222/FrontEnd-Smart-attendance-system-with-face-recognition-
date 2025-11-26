/* =======================================================
   Smart Attendance System - main.js
   ======================================================= */

const BACKEND_URL = "http://localhost:8000";   

/* =======================================================
   LOGIN FUNCTION
   ======================================================= */
function login() {
    const user = document.getElementById("username").value.trim();
    const pass = document.getElementById("password").value.trim();

    if (user === "" || pass === "") {
        alert("Please enter username and password");
        return;
    }

    // Placeholder (connect to backend later)
    alert("Login successful");
    window.location.href = "dashboard.html";
}

/* =======================================================
   LOGOUT FUNCTION
   ======================================================= */
function logout() {
    window.location.href = "login.html";
}

/* =======================================================
   ENROLL FUNCTION
   ======================================================= */
function enrollStudent() {
    const fname = document.getElementById("firstName").value.trim();
    const lname = document.getElementById("lastName").value.trim();

    if (fname === "" || lname === "") {
        alert("Please enter first name and last name");
        return;
    }

    // Placeholder (connect to backend later)
    alert(`Enrolled: ${fname} ${lname}`);
    window.location.href = "dashboard.html";
}

/* =======================================================
   LOAD ATTENDANCE TABLE
   ======================================================= */
function loadAttendance() {
    const tableBody = document.getElementById("attendance-body");

    if (!tableBody) return; // Not on attendance page

    // Example placeholder data
    const demoData = [
        { name: "John Doe", email: "john@example.com", date: "2025-11-22", time: "09:41", status: "present" },
        { name: "Raghda Ali", email: "raghda@example.com", date: "2025-11-22", time: "09:43", status: "present" },
    ];

    demoData.forEach(row => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${row.name}</td>
            <td>${row.email}</td>
            <td>${row.date}</td>
            <td>${row.time}</td>
            <td>${row.status}</td>
        `;

        tableBody.appendChild(tr);
    });
}

/* =======================================================
   START ATTENDANCE
   ======================================================= */
function startAttendance() {
    alert("Attendance started (camera would open here)");
}

/* =======================================================
   AUTO RUN ON PAGE LOAD
   ======================================================= */
document.addEventListener("DOMContentLoaded", () => {
    loadAttendance();
});
