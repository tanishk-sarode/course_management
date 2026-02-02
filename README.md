# Online Course Enrollment System

A comprehensive backend system for managing online courses, instructors, and student enrollments built with FastAPI.

## Features

- **Authentication & Authorization**: JWT-based authentication with role-based access control (Student/Instructor)
- **User Management**: CRUD operations for students and instructors
- **Course Management**: Create, read, update, and delete courses (instructors only)
- **Enrollment System**: Students can enroll/unenroll from courses
- **Progress Tracking**: Track student progress through courses
- **Filtering**: Filter courses by category and instructor

## Technical Stack

- **Python 3.8+**
- **FastAPI**: Modern web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **JWT**: JSON Web Tokens for authentication
- **SQLite**: Lightweight database
- **Bcrypt**: Password hashing

## Installation

1. Navigate to the assignment directory:
```bash
cd assignment
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

Interactive API documentation (Swagger UI) is available at `http://localhost:8000/`

## API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` - Register a new user (student or instructor)
- `POST /auth/login` - Login and receive JWT tokens

### Users (`/users`)
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update current user profile
- `GET /users/` - List all users (with optional role filter)
- `GET /users/{user_id}` - Get user by ID
- `GET /users/instructors/` - List all instructors
- `GET /users/students/` - List all students

### Courses (`/courses`)
- `POST /courses/` - Create a new course (instructors only)
- `GET /courses/` - List all courses (with filters: category, instructor_id, is_published)
- `GET /courses/{course_id}` - Get course by ID
- `PUT /courses/{course_id}` - Update course (course instructor only)
- `DELETE /courses/{course_id}` - Delete course (course instructor only)
- `GET /courses/instructor/{instructor_id}` - Get courses by instructor
- `GET /courses/category/{category}` - Get courses by category

### Enrollments (`/enrollments`)
- `POST /enrollments/` - Enroll in a course (students only)
- `GET /enrollments/my-enrollments` - Get current student's enrollments
- `GET /enrollments/course/{course_id}` - Get enrollments for a course (instructors only)
- `PUT /enrollments/{enrollment_id}` - Update enrollment status
- `DELETE /enrollments/{enrollment_id}` - Unenroll from course (soft delete)
- `GET /enrollments/student/{student_id}` - Get student's enrollment history

### Progress (`/progress`)
- `GET /progress/my-progress` - Get current student's progress (students only)
- `GET /progress/enrollment/{enrollment_id}` - Get progress for specific enrollment
- `PUT /progress/enrollment/{enrollment_id}` - Update progress (students only)
- `GET /progress/course/{course_id}` - Get progress for all enrollments in course (instructors only)

## Data Models

### User
- Email, password (hashed), first name, last name
- Role: student or instructor
- Active status

### Course
- Title, description, category, level
- Published status
- Instructor (foreign key to User)

### Enrollment
- Student (foreign key to User)
- Course (foreign key to Course)
- Status: active, dropped, completed
- Enrollment date

### Progress
- Enrollment (foreign key to Enrollment)
- Completion percentage (0-100)
- Last accessed timestamp

## Role-Based Access Control

- **Students**:
  - Can register and login
  - Can view courses and instructors
  - Can enroll/unenroll from courses
  - Can update their own progress
  - Can view their own enrollments and progress

- **Instructors**:
  - Can register and login
  - Can create, update, and delete their own courses
  - Can view enrollments for their courses
  - Can view progress for their course enrollments
  - Can view all users

## Security

- Passwords are hashed using bcrypt
- JWT tokens are used for authentication
- Role-based access control ensures proper authorization
- Tokens expire after 30 minutes (configurable)

## Database

The application uses SQLite by default. The database file (`app.db`) is created automatically when the application starts.

To modify the database URL, update the `database_url` in the configuration file or set the `DATABASE_URL` environment variable.

## Configuration

Key settings are defined in `app/core/config.py`:
- `SECRET_KEY`: Used for JWT token generation (change in production!)
- `database_url`: SQLite database location
- `cors_origins`: Allowed CORS origins
- Token expiration times

## Testing the API

1. Register a new instructor:
```bash
POST /auth/register
{
  "email": "instructor@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "instructor"
}
```

2. Login to get tokens:
```bash
POST /auth/login
{
  "email": "instructor@example.com",
  "password": "password123"
}
```

3. Create a course (use the access_token from login):
```bash
POST /courses/
Authorization: Bearer <access_token>
{
  "title": "Introduction to Python",
  "description": "Learn Python programming from scratch",
  "category": "programming",
  "level": "beginner"
}
```

4. Register a student and enroll in the course following similar steps.

## Project Structure

```
assignment/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── common/
│   │   └── enums.py         # Enumerations (roles, categories, etc.)
│   ├── core/
│   │   ├── config.py        # Application configuration
│   │   ├── dependencies.py  # Dependency injection functions
│   │   └── security.py      # Authentication and security utilities
│   ├── database/
│   │   ├── base.py          # SQLAlchemy base class
│   │   └── session.py       # Database session management
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── course.py
│   │   ├── enrollment.py
│   │   ├── progress.py
│   │   └── review.py
│   ├── routers/             # API route handlers
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── courses.py
│   │   ├── enrollments.py
│   │   └── progress.py
│   └── schemas/             # Pydantic schemas for validation
│       ├── auth.py
│       ├── user.py
│       ├── course.py
│       ├── enrollment.py
│       └── progress.py
└── requirements.txt
```
