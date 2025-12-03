# Smart Attendance System

A comprehensive face recognition-based attendance management system built with FastAPI backend. This system uses advanced AI technology to automatically recognize faces and record attendance.



## ✨ Features

- **Face Recognition**: Advanced face recognition using InsightFace model
- **Automatic Attendance**: Real-time attendance marking using camera
- **Multiple Enrollment Methods**: 
  - Browser camera enrollment
  - System camera enrollment
  - Image-based enrollment
- **Admin Dashboard**: User-friendly web interface for managing attendance
- **JWT Authentication**: Secure token-based authentication
- **Attendance Reports**: View and export attendance records
- **Duplicate Prevention**: Prevents multiple attendance entries per day

## 🛠 Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLModel** - SQL databases with Python objects
- **InsightFace** - State-of-the-art face recognition library
- **OpenCV** - Computer vision library for image processing
- **JWT** - Secure authentication tokens
- **SQLite** - Lightweight database

### Frontend
- **Flask** - Web framework for serving HTML templates
- **Vanilla JavaScript** - Client-side interactions
- **HTML/CSS** - Modern, responsive UI

## 📦 Prerequisites

- **Python 3.11.9** (Recommended) - We strongly recommend using Python 3.11.9 for optimal compatibility
- pip (Python package installer)
- Camera (webcam or external camera) for face enrollment and recognition
- Git (optional, for cloning the repository)

### Python Version Recommendation

**Important**: We recommend using **Python 3.11.9** specifically because:
- Best compatibility with InsightFace and ONNX Runtime
- Optimal performance with NumPy 2.2.6
- Stable with all required dependencies
- Tested extensively with this version

You can download Python 3.11.9 from: https://www.python.org/downloads/

## 📁 Project Structure

```
work2/
├── Smart-Attendance-System-backend-main/    # Backend (FastAPI)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── config/
│   │   │   └── dbsetup.py          # Database configuration
│   │   ├── models/                 # SQLModel database models
│   │   │   ├── administrator.py
│   │   │   ├── attendance.py
│   │   │   ├── embedding.py
│   │   │   ├── person.py
│   │   │   └── status.py
│   │   ├── routers/                # API route handlers
│   │   │   ├── admin_router.py
│   │   │   ├── attendance_router.py
│   │   │   ├── person_router.py
│   │   │   └── status_router.py
│   │   ├── services/               # Business logic services
│   │   │   ├── auth.py
│   │   │   ├── enrollment_service.py
│   │   │   ├── face_service.py
│   │   │   └── password_utils.py
│   │   └── cruds/                  # Database CRUD operations
│   │       ├── admin_crud.py
│   │       ├── attendance_crud.py
│   │       ├── embedding_crud.py
│   │       ├── person_crud.py
│   │       └── status_crud.py
│   ├── enroll_images/              # Temporary directory for enrollment images
│   ├── attendanceSys.db            # SQLite database (auto-generated)
│   └── README.md                   # Backend documentation
│
├── FrontEnd-Smart-attendance-system-with-face-recognition-/  # Frontend (Flask)
│   ├── app.py                      # Flask application entry point
│   ├── templates/                  # HTML templates
│   │   ├── login.html              # Login page
│   │   ├── dashboard.html          # Main dashboard
│   │   ├── enroll.html             # Student enrollment page
│   │   └── take_attendance.html    # Attendance taking page
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css           # Stylesheet
│   │   └── js/
│   │       └── main.js             # Frontend JavaScript logic
│  
│   
│
├── requirements.txt                # Root level requirements (if exists)
├── readme.md                       # This file (main documentation)
└── venv/                           # Virtual environment (not in repo)
```

## 🚀 Installation Guide

### Step 1: Verify Python Version

First, verify that you have Python 3.11.9 installed:

```bash
python --version
```

You should see: `Python 3.11.9`

If you have a different version, please install Python 3.11.9 from the official Python website.

### Step 2: Clone or Navigate to Project Directory

If you cloned the repository:

```bash
cd Smart-Attendance-System-backend-main
```

### Step 3: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the beginning of your command prompt, indicating the virtual environment is active.

### Step 4: Upgrade pip

```bash
python -m pip install --upgrade pip
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: Installation may take several minutes as it includes heavy dependencies like InsightFace and ONNX Runtime.

### Step 6: Create Environment Variables File

Create a `.env` file in the root directory (`Smart-Attendance-System-backend-main/`) with the following content:

```env
# Database Configuration
DATABASE_URL=sqlite:///./attendanceSys.db

# JWT Authentication Configuration
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Optional: Logging Level
LOG_LEVEL=INFO
```

**Security Warning**: Change `JWT_SECRET` to a strong random string in production. You can generate one using:

```python
import secrets
print(secrets.token_urlsafe(32))
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the backend root directory with these variables:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | SQLite database file path | `sqlite:///./attendanceSys.db` | Yes |
| `JWT_SECRET` | Secret key for JWT token signing | - | Yes |
| `ALGORITHM` | JWT algorithm | `HS256` | Yes |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time in minutes | `1440` (24 hours) | Yes |

### Database

The system uses SQLite by default. The database file (`attendanceSys.db`) will be created automatically on first run. Tables are created automatically when the application starts.

##  Running the Application

### Backend Server

1. Make sure your virtual environment is activated (you should see `(venv)` in your terminal)

2. Navigate to the backend directory:
```bash
cd Smart-Attendance-System-backend-main
```

3. Run the FastAPI server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or using FastAPI CLI:
```bash
fastapi run app/main.py --reload
```

The server will start on: **http://localhost:8000**

### Frontend Server

Open a new terminal window and:

1. Navigate to the frontend directory:
```bash
cd FrontEnd-Smart-attendance-system-with-face-recognition-
```

2. Activate the virtual environment (if not already activated):
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install frontend dependencies (if not already installed):
```bash
pip install -r requirements.txt
```

4. Update the backend URL in `static/js/main.js` (if needed):
```javascript
const BACKEND_URL = "http://localhost:8000";
```

5. Run the Flask server:
```bash
flask run --port 5000
```

Or:
```bash
python app.py
```

The frontend will start on: **http://localhost:5000**

## 📚 API Documentation

Once the backend server is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main API Endpoints

#### Authentication
- `POST /admin/signup` - Create a new administrator account
- `POST /admin/login` - Login and get JWT token

#### Attendance
- `GET /attendance/records` - Get all attendance records
- `POST /attendance/enroll_camera` - Enroll using system camera
- `POST /attendance/enroll_browser_camera` - Enroll using browser camera
- `POST /attendance/take_attendance` - Mark attendance from image

#### Person Management
- `POST /person/` - Create a new person
- `GET /person/` - Get person by ID

#### Status Management
- `POST /status/` - Create a new status

**Note**: Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-token>
```

## 📖 Usage Guide

### 1. Create Admin Account

First, create an administrator account using the API:

```bash
curl -X POST "http://localhost:8000/admin/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "your-secure-password"
  }'
```

Or use the Swagger UI at http://localhost:8000/docs

### 2. Access the Frontend

1. Open your browser and navigate to: http://localhost:5000
2. Login with your admin credentials
3. You'll be redirected to the dashboard

### 3. Enroll a Person

1. Click on "Enroll Student" in the dashboard
2. Enter first name and last name
3. Click "Start Enrollment"
4. Allow camera access when prompted
5. Position yourself in front of the camera
6. Wait for 10 images to be captured automatically
7. The system will process and enroll the person

### 4. Take Attendance

1. Click on "Take Attendance" in the dashboard
2. Click "START" button
3. Allow camera access
4. Look at the camera
5. The system will recognize you and mark attendance automatically

### 5. View Attendance Records

Attendance records are displayed in the "Take Attendance" page. Each record shows:
- Person name
- Date and time
- Status (Present, Absent, etc.)

## 🔧 Troubleshooting

### Common Issues

#### 1. Python Version Error

**Problem**: `ModuleNotFoundError` or version incompatibility errors

**Solution**: Ensure you're using Python 3.11.9:
```bash
python --version
```

If not, download and install Python 3.11.9 from https://www.python.org/downloads/

#### 2. Camera Not Working

**Problem**: Camera access denied or camera not detected

**Solutions**:
- Check camera permissions in your browser/system settings
- Ensure no other application is using the camera
- Try using a different browser (Chrome recommended)
- For system camera enrollment, ensure camera drivers are installed

#### 3. Face Not Detected

**Problem**: "No face detected" error during enrollment or attendance

**Solutions**:
- Ensure good lighting conditions
- Face the camera directly
- Remove glasses or hat if possible
- Keep a distance of 1-2 meters from camera
- Ensure face fills at least 30% of the frame

#### 4. Database Errors

**Problem**: Database connection or table creation errors

**Solution**: Delete the database file and restart the server:
```bash
rm attendanceSys.db  # Linux/Mac
del attendanceSys.db  # Windows
```

The database will be recreated on next startup.

#### 5. Import Errors

**Problem**: `ModuleNotFoundError` for app modules

**Solution**: Ensure you're running commands from the correct directory and virtual environment is activated:
```bash
# Make sure you're in the backend directory
cd Smart-Attendance-System-backend-main

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Verify you can import the app
python -c "from app.main import app; print('OK')"
```

#### 6. InsightFace Model Download

**Problem**: First run takes a long time or fails

**Solution**: InsightFace automatically downloads models on first use. Ensure you have:
- Stable internet connection
- Sufficient disk space (~500MB)
- Wait for the download to complete

#### 7. Port Already in Use

**Problem**: `Address already in use` error

**Solution**: 
- Check if another instance is running: `netstat -ano | findstr :8000` (Windows) or `lsof -i :8000` (Linux/Mac)
- Kill the process or use a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

#### 8. CORS Errors

**Problem**: Frontend can't connect to backend

**Solution**: Ensure CORS origins are configured correctly in `app/main.py`. Update the `origins` list if using different ports or domains.

### Getting Help

If you encounter issues not covered here:

1. Check the logs in your terminal for error messages
2. Verify all environment variables are set correctly
3. Ensure all dependencies are installed: `pip list`
4. Try recreating the virtual environment
5. Check that both backend and frontend servers are running

## 💻 Development

### Project Setup for Development

1. Clone the repository
2. Create and activate virtual environment
3. Install development dependencies:
```bash
pip install -r requirements.txt
```

### Code Structure

The project follows a clean architecture pattern:

- **Models**: Database models using SQLModel
- **CRUDs**: Database operations
- **Services**: Business logic (face recognition, auth, etc.)
- **Routers**: API endpoints
- **Config**: Configuration and database setup


### Code Style

The codebase uses:
- Type hints throughout
- Docstrings for all functions and classes
- PEP 8 style guide
- English comments and documentation

## 🔒 Security Notes

### Production Deployment

Before deploying to production:

1. **Change JWT Secret**: Use a strong, randomly generated secret
2. **Use Environment Variables**: Never commit `.env` file to version control
3. **Enable HTTPS**: Use SSL/TLS certificates
4. **Database Security**: Consider using PostgreSQL or MySQL instead of SQLite
5. **Rate Limiting**: Implement rate limiting for API endpoints
6. **Input Validation**: All inputs are validated, but review for your use case
7. **CORS Configuration**: Restrict CORS to specific domains
8. **Password Policy**: Enforce strong password requirements
9. **Logging**: Configure proper logging and monitoring
10. **Backup**: Regular database backups

### Security Best Practices

- Never share your JWT tokens
- Use strong passwords for admin accounts
- Keep dependencies updated: `pip list --outdated`
- Regularly review access logs
- Implement proper session management

## 📝 Notes

- The system prevents duplicate attendance entries for the same person on the same day
- Face recognition threshold is set to 0.65 (65% similarity)
- Enrollment captures 10 images and uses average embedding for better accuracy
- Database is SQLite by default (suitable for development and small deployments)

