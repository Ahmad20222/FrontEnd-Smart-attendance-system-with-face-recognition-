const BACKEND_URL = "http://127.0.0.1:8000"; // Change if backend hosted elsewhere

// === LOGIN FUNCTIONALITY ===

async function login(email, password) {
  const url = `${BACKEND_URL}/admin/login`;
  const body = new URLSearchParams();
  body.append("username", email); // OAuth2PasswordRequestForm expects "username"
  body.append("password", password);

  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });

  if (!res.ok) {
    const errText = await res.text().catch(()=>null);
    throw new Error("Login failed: " + (errText || res.status));
  }
  const data = await res.json(); // { access_token, token_type, admin }
  // store token (localStorage/sessionStorage or memory)
  localStorage.setItem("token", data.access_token);
  localStorage.setItem("admin", JSON.stringify(data.admin));
  return data;
}

// === LOGOUT FUNCTIONALITY ===
function logout() {
  localStorage.removeItem("admin");
  localStorage.removeItem("token");
  window.location.href = "index.html";
}

// === CHECK AUTH STATE ===
function checkAuth() {
  const admin = localStorage.getItem("admin");
  if (!admin) {
    window.location.href = "index.html";
  }
  const nameElement = document.getElementById("admin-name");
  if (nameElement) {
    nameElement.textContent = admin;
  }
}

// === FETCH ATTENDANCE DATA ===
async function loadAttendance() {
  const tableRoot = document.getElementById("attendance-table");
  const errorElement = document.getElementById("error-message");
  const token = localStorage.getItem("token");

  if (!token) {
    window.location.href = "index.html";
    return;
  }

  try {
    const response = await fetch(`${BACKEND_URL}/attendance`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.status === 200) {
      const data = await response.json();
      if (data.length === 0) {
        tableRoot.innerHTML = "<tr><td colspan='4'>No attendance data found.</td></tr>";
        return;
      }

      let html = "";
      data.forEach((record, index) => {
        html += `
          <tr>
            <td>${index + 1}</td>
            <td>${record.name || record.user || "—"}</td>
            <td>${record.time || record.timestamp || "—"}</td>
            <td>${record.status || "Present"}</td>
          </tr>`;
      });
      tableRoot.innerHTML = html;
    } else if (response.status === 401) {
      errorElement.textContent = "Unauthorized. Please log in again.";
      logout();
    } else {
      errorElement.textContent = "Failed to load attendance data.";
    }
  } catch (error) {
    console.error("Attendance fetch error:", error);
    errorElement.textContent = "Server unreachable.";
  }
}

// === FILTER ATTENDANCE (CLIENT-SIDE) ===
function filterAttendance() {
  const query = document.getElementById("filter-input").value.toLowerCase();
  const rows = document.querySelectorAll("#attendance-table tr");

  rows.forEach((row) => {
    const name = row.cells[1]?.textContent.toLowerCase() || "";
    row.style.display = name.includes(query) ? "" : "none";
  });
}

// === DOWNLOAD REPORT ===
async function downloadReport() {
  const token = localStorage.getItem("token");
  if (!token) {
    alert("Please log in first.");
    return;
  }

  try {
    const response = await fetch(`${BACKEND_URL}/attendance`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (response.status === 200) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "attendance_report.csv";
      document.body.appendChild(a);
      a.click();
      a.remove();
    } else {
      alert("Failed to download report.");
    }
  } catch (error) {
    alert("Server unreachable.");
  }
}

// === AUTO INITIALIZATION ===
// Call checkAuth() and loadAttendance() automatically if available
document.addEventListener("DOMContentLoaded", () => {
  if (document.body.classList.contains("dashboard-page")) {
    checkAuth();
    loadAttendance();
  }
  if (document.body.classList.contains("attendance-page")) {
    checkAuth();
    loadAttendance();
  }
});

