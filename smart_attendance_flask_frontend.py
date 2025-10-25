# Project: Smart Attendance System - Flask Frontend
# Structure
# ├── app.py
# ├── requirements.txt
# ├── README.md
# ├── static/
# │   ├── css/style.css
# │   └── js/main.js
# └── templates/
#     ├── base.html
#     ├── login.html
#     ├── dashboard.html
#     └── attendance.html


### File: requirements.txt
```
Flask==2.3.2
python-dotenv==1.0.0
requests==2.31.0
```


### File: README.md
```
# Smart Attendance System - Flask Frontend

## Quick start
1. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Mac/Linux
   venv\Scripts\activate    # Windows
   ```
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variable for Flask (optional):
   ```bash
   export FLASK_APP=app.py
   export FLASK_ENV=development
   ```
4. Run the app:
   ```bash
   flask run --port 5000
   ```

This frontend expects the FastAPI backend to be running and reachable (default `http://localhost:8000`).

Endpoints used (examples):
- `GET /api/attendance` -> list of attendance records
- `GET /api/attendance/report` -> aggregated report (CSV/JSON)
- `POST /api/auth/login` -> admin login

Adjust `BACKEND_URL` in `app.py` if needed.
```


### File: app.py
```python
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
import requests
import os
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret-please-change')
app.permanent_session_lifetime = timedelta(hours=8)

# Point this to your FastAPI backend
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8000')


@app.route('/')
def index():
    if 'admin' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Forward login to backend auth endpoint (assumes token in response)
        try:
            resp = requests.post(f'{BACKEND_URL}/api/auth/login', json={'username': username, 'password': password}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                token = data.get('access_token') or data.get('token')
                session.permanent = True
                session['admin'] = username
                session['token'] = token
                return redirect(url_for('dashboard'))
            else:
                error = resp.json().get('detail', 'Login failed') if resp.headers.get('content-type','').startswith('application/json') else 'Login failed'
                return render_template('login.html', error=error)
        except requests.exceptions.RequestException:
            return render_template('login.html', error='Backend unreachable')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', admin=session.get('admin'))


@app.route('/api/attendance')
def attendance_api_proxy():
    # Proxy endpoint to call backend and return JSON (used by client JS)
    if 'admin' not in session:
        return jsonify({'detail': 'Unauthorized'}), 401
    headers = {}
    if session.get('token'):
        headers['Authorization'] = f"Bearer {session['token']}"
    try:
        resp = requests.get(f'{BACKEND_URL}/api/attendance', headers=headers, timeout=5)
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.RequestException:
        return jsonify({'detail': 'Backend unreachable'}), 503


@app.route('/attendance')
def attendance_page():
    if 'admin' not in session:
        return redirect(url_for('login'))
    return render_template('attendance.html')


@app.route('/report')
def download_report():
    if 'admin' not in session:
        return redirect(url_for('login'))
    headers = {}
    if session.get('token'):
        headers['Authorization'] = f"Bearer {session['token']}"
    try:
        # expect the backend to send back a CSV file or downloadable report
        resp = requests.get(f'{BACKEND_URL}/api/attendance/report', headers=headers, timeout=10, stream=True)
        if resp.status_code == 200:
            # save to temporary file and send
            tmp_path = 'attendance_report.csv'
            with open(tmp_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            return send_file(tmp_path, as_attachment=True, download_name='attendance_report.csv')
        else:
            return redirect(url_for('dashboard'))
    except requests.exceptions.RequestException:
        return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
```


### File: templates/base.html
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{% block title %}Attendance Dashboard{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
  </head>
  <body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container-fluid">
        <a class="navbar-brand" href="{{ url_for('dashboard') }}">Smart Attendance</a>
        <div class="collapse navbar-collapse">
          <ul class="navbar-nav ms-auto">
            {% if session.get('admin') %}
            <li class="nav-item"><a class="nav-link">{{ session.get('admin') }}</a></li>
            <li class="nav-item"><a class="nav-link" href="{{ url_for('attendance_page') }}">Attendance</a></li>
            <li class="nav-item"><a class="nav-link" href="{{ url_for('download_report') }}">Download Report</a></li>
            <li class="nav-item"><a class="nav-link" href="{{ url_for('logout') }}">Logout</a></li>
            {% endif %}
          </ul>
        </div>
      </div>
    </nav>

    <main class="container py-4">
      {% block content %}{% endblock %}
    </main>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block scripts %}{% endblock %}
  </body>
</html>
```


### File: templates/login.html
```html
{% extends 'base.html' %}
{% block title %}Login - Smart Attendance{% endblock %}
{% block content %}
<div class="row justify-content-center">
  <div class="col-md-5">
    <div class="card shadow-sm">
      <div class="card-body">
        <h4 class="card-title mb-4">Administrator Login</h4>
        {% if error %}
          <div class="alert alert-danger">{{ error }}</div>
        {% endif %}
        <form method="post">
          <div class="mb-3">
            <label for="username" class="form-label">Username</label>
            <input type="text" class="form-control" id="username" name="username" required>
          </div>
          <div class="mb-3">
            <label for="password" class="form-label">Password</label>
            <input type="password" class="form-control" id="password" name="password" required>
          </div>
          <button class="btn btn-primary w-100" type="submit">Log in</button>
        </form>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```


### File: templates/dashboard.html
```html
{% extends 'base.html' %}
{% block title %}Dashboard - Smart Attendance{% endblock %}
{% block content %}
<h1 class="mb-3">Dashboard</h1>
<p>Welcome, <strong>{{ admin }}</strong>.</p>
<div class="row">
  <div class="col-md-8">
    <div class="card">
      <div class="card-body">
        <h5 class="card-title">Recent Attendance</h5>
        <div id="attendance-table-root">Loading...</div>
      </div>
    </div>
  </div>
  <div class="col-md-4">
    <div class="card mb-3">
      <div class="card-body">
        <h6>Quick Actions</h6>
        <a class="btn btn-outline-primary w-100 mb-2" href="{{ url_for('attendance_page') }}">Open Attendance View</a>
        <a class="btn btn-outline-secondary w-100" href="{{ url_for('download_report') }}">Download CSV Report</a>
      </div>
    </div>
  </div>
</div>
{% endblock %}
{% block scripts %}
<script>
// Fetch recent attendance and render a simple table
async function loadRecentAttendance() {
  const root = document.getElementById('attendance-table-root');
  root.innerHTML = 'Loading...';
  try {
    const res = await fetch('/api/attendance');
    if (res.status === 200) {
      const data = await res.json();
      if (!Array.isArray(data)) {
        root.innerHTML = '<div class="text-muted">No attendance data available.</div>';
        return;
      }
      let html = '<div class="table-responsive"><table class="table table-sm"><thead><tr><th>#</th><th>Name</th><th>Time</th><th>Status</th></tr></thead><tbody>';
      data.slice(0,10).forEach((row, idx) => {
        html += `<tr><td>${idx+1}</td><td>${row.name || row.user || '—'}</td><td>${row.time || row.timestamp || '—'}</td><td>${row.status || 'Present'}</td></tr>`;
      });
      html += '</tbody></table></div>';
      root.innerHTML = html;
    } else if (res.status === 401) {
      window.location = '/login';
    } else {
      root.innerHTML = '<div class="text-danger">Failed to load attendance.</div>';
    }
  } catch (e) {
    root.innerHTML = '<div class="text-danger">Backend unreachable.</div>';
  }
}

loadRecentAttendance();
</script>
{% endblock %}
```


### File: templates/attendance.html
```html
{% extends 'base.html' %}
{% block title %}Attendance Records - Smart Attendance{% endblock %}
{% block content %}
<h1>Attendance Records</h1>
<div class="mb-3">
  <input id="filter-input" class="form-control" placeholder="Filter by name...">
</div>
<div id="attendance-list">Loading attendance...</div>
{% endblock %}
{% block scripts %}
<script>
async function loadAttendance() {
  const root = document.getElementById('attendance-list');
  root.innerHTML = 'Loading...';
  try {
    const res = await fetch('/api/attendance');
    if (res.status === 200) {
      const data = await res.json();
      if (!Array.isArray(data) || data.length === 0) {
        root.innerHTML = '<div class="text-muted">No attendance records found.</div>';
        return;
      }
      let html = '<div class="table-responsive"><table class="table table-striped"><thead><tr><th>#</th><th>Name</th><th>ID</th><th>Time</th><th>Status</th></tr></thead><tbody>';
      data.forEach((r, i) => {
        html += `<tr><td>${i+1}</td><td>${r.name || r.user || '—'}</td><td>${r.user_id || r.id || '—'}</td><td>${r.time || r.timestamp || '—'}</td><td>${r.status || 'Present'}</td></tr>`;
      });
      html += '</tbody></table></div>';
      root.innerHTML = html;
    } else if (res.status === 401) {
      window.location = '/login';
    } else {
      root.innerHTML = '<div class="text-danger">Failed to load attendance.</div>';
    }
  } catch (e) {
    root.innerHTML = '<div class="text-danger">Backend unreachable.</div>';
  }
}

loadAttendance();

// Basic filter
const filterInput = document.getElementById('filter-input');
filterInput.addEventListener('input', () => {
  const q = filterInput.value.toLowerCase();
  const rows = document.querySelectorAll('#attendance-list table tbody tr');
  rows.forEach(r => {
    const name = r.cells[1].textContent.toLowerCase();
    r.style.display = name.includes(q) ? '' : 'none';
  });
});
</script>
{% endblock %}
```


### File: static/css/style.css
```css
body { background: #f8f9fa; }
.card { border-radius: 12px; }
.navbar-brand { font-weight: 600; }
```


### File: static/js/main.js
```javascript
// Placeholder for common JS. Add global helpers here if needed.
console.log('Frontend loaded');
