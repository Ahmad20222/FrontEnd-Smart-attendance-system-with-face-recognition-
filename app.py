from flask import Flask, render_template

app = Flask(__name__)

# --------------------------
# HTML ROUTES
# --------------------------

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/enroll')
def enroll_page():
    return render_template('enroll.html')

@app.route('/take_attendance')
def take_attendance_page():
    return render_template('take_attendance.html')


# --------------------------
# START SERVER
# --------------------------
if __name__ == "__main__":
    app.run(debug=False)
