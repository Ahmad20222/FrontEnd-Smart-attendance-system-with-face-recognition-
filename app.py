from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
import requests, os
from datetime import timedelta

app = Flask(__name__, template_folder='template')
app.secret_key = os.environ.get("SECRET_KEY", "479e2b3b4a6a4364899f6e442a5f1cd6c6bc97f870f4901623c63e53b055f5ab")  # added so sessions work
app.permanent_session_lifetime = timedelta(hours=1)

BACKEND_URL = os.environ.get('BACKEND_URL', 'http://127.0.0.1:8000')
USE_BACKEND = os.environ.get('USE_BACKEND', '1') == '1'  # set USE_BACKEND=0 to disable backend calls



@app.route('/')
def index():
    return redirect(url_for('login')) if 'admin' not in session else redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        try:
            return render_template("login.html")
        except Exception as e:
            app.logger.exception("Template render error")
            return f"Template render error: {e}", 500
    username = request.form.get("username")
    password = request.form.get("password")

    if USE_BACKEND:
        try:
            resp = requests.post(
                f"{BACKEND_URL}/admin/login",
                data={"username": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10,
            )
        except requests.RequestException:
            return render_template("login.html", error="Backend unreachable"), 502

        if resp.status_code != 200:
            return render_template("login.html", error="Invalid credentials"), 401

        data = resp.json()
        # store token & admin in server-side session
        session["access_token"] = data.get("access_token")
        session["admin"] = data.get("admin")
        return redirect(url_for("dashboard"))

    # Dev fallback (no backend)
    if username == "admin" and password == "admin":
        session["access_token"] = "dev-token"
        session["admin"] = {"email": "admin"}
        return redirect(url_for("dashboard"))
    return render_template("login.html", error="Invalid credentials"), 401


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('login'))
    admin = session.get('admin')
    return render_template('dashboard.html', admin=admin)

@app.route('/api/attendance')
def attendance_api_proxy():
    if 'admin' not in session:
        return jsonify({'detail': 'Unauthorized'}), 401

    # If backend calls are disabled, return an empty result (or a stub)
    if not USE_BACKEND:
        return jsonify([]), 200

    token = session.get('access_token')
    headers = {'Authorization': f"Bearer {token}"} if token else {}
    try:
        resp = requests.get(f'{BACKEND_URL}/attendance', headers=headers, timeout=5)
        try:
            payload = resp.json()
        except ValueError:
            payload = {'detail': resp.text}
        return jsonify(payload), resp.status_code
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
    headers = {'Authorization': f"Bearer {session['token']}"} if session.get('token') else {}
    try:
        resp = requests.get(f'{BACKEND_URL}/attendance/report', headers=headers, timeout=10, stream=True)
        if resp.status_code == 200:
            tmp_path = 'attendance_report.csv'
            with open(tmp_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            return send_file(tmp_path, as_attachment=True, download_name='attendance_report.csv')
    except requests.exceptions.RequestException:
        pass
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, port=5000)
