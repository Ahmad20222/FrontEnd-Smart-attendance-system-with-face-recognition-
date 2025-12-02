
// BACKEND URL (change later if needed)
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

    // Placeholder until backend is added
    alert("Login successful");
    window.location.href = "/dashboard";
}


/* =======================================================
   LOGOUT FUNCTION
   ======================================================= */
function logout() {
    window.location.href = "/";
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

    // Placeholder
    alert(`Enrolled: ${fname} ${lname}`);
    window.location.href = "/dashboard";
}


/* =======================================================
   LOAD ATTENDANCE TABLE
   ======================================================= */
function loadAttendance() {
    const tableBody = document.getElementById("attendance-body");

    if (!tableBody) return; // Only run on attendance page

    const sampleData = [
        { name: "John Doe", date: "2025-11-22", status: "present" },
        { name: "Raghda Ali", date: "2025-11-22", status: "present" },
    ];

    sampleData.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${row.name}</td>
            <td>${row.date}</td>
            <td>${row.status}</td>
        `;
        tableBody.appendChild(tr);
    });
}


/* =======================================================
   START ATTENDANCE
   ======================================================= */
function startAttendance() {
    alert("Attendance started. (Face recognition will run here later.)");
}


/* =======================================================
   AUTO LOAD DATA
   ======================================================= */
document.addEventListener("DOMContentLoaded", () => {
    loadAttendance();
});
