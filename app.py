from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
import requests, os
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret')
app.permanent_session_lifetime = timedelta(hours=8)

BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8000')

@app.route('/')
def index():
    return redirect(url_for('login')) if 'admin' not in session else redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            resp = requests.post(f'{BACKEND_URL}/api/auth/login', json={'username': username, 'password': password}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                session['admin'] = username
                session['token'] = data.get('access_token')
                return redirect(url_for('dashboard'))
            return render_template('login.html', error='Login failed')
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
    if 'admin' not in session:
        return jsonify({'detail': 'Unauthorized'}), 401
    headers = {'Authorization': f"Bearer {session['token']}"} if session.get('token') else {}
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
    headers = {'Authorization': f"Bearer {session['token']}"} if session.get('token') else {}
    try:
        resp = requests.get(f'{BACKEND_URL}/api/attendance/report', headers=headers, timeout=10, stream=True)
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
    app.run(debug=True, port=5000)
