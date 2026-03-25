# Flask Backend Project

## Overview
This is a backend REST API built using Flask. It includes authentication, role-based access, and CRUD operations.

## Features
- User Registration & Login
- JWT Authentication
- Protected Routes
- Role-based Access (Admin/User)
- Notes CRUD APIs
- Task CRUD APIs

## Tech Stack
- Python (Flask)
- SQLite
- Flask-JWT-Extended
- SQLAlchemy
- Bcrypt

## Installation

1. Clone the repository:
git clone https://github.com/daneshreddy/flask-backend-task

2. Install dependencies:
pip install flask flask_sqlalchemy flask_jwt_extended bcrypt

3. Run the server:
python app.py

## API Endpoints

- POST /register
- POST /login
- GET /dashboard
- GET /admin

### Notes
- POST /notes
- GET /notes
- PUT /notes/<id>
- DELETE /notes/<id>

### Tasks
- POST /task
- GET /task
- PUT /task/<id>
- DELETE /task/<id>
