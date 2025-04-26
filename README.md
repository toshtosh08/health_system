# Health Information System

A Flask-based web application for managing health programs and client data, featuring program creation, client registration, enrollment, search, profiles, a secure API, unit tests, and audit logging. Built as a course project to demonstrate full-stack development, security, and testing.

## Features
- **Program Management**: Create and list health programs (e.g., "TB" for Tuberculosis).
- **Client Registration**: Register clients with name, date of birth, gender, and contact info.
- **Client Enrollment**: Enroll clients in programs with validation to prevent duplicates.
- **Search and Profiles**: Search clients by name and view detailed profiles, including enrollment history.
- **Secure API**: Authenticated API endpoints (`/api/login`, `/api/client/<id>`) using JWT for secure access.
- **Audit Logging**: Logs all key actions (e.g., program creation, client registration) to `audit.log`.
- **Unit Testing**: Comprehensive test suite (`tests/test_routes.py`) covering all routes and API endpoints.
- **Security**: Input validation, password hashing, and JWT authentication.

## Tech Stack
- **Backend**: Flask, SQLAlchemy, SQLite (`health_system.db`)
- **Frontend**: HTML, CSS, Jinja2 templates
- **Authentication**: PyJWT for API token-based security
- **Testing**: Python `unittest`
- **Logging**: Python `logging` module
- **Development**: PyCharm, Python 3.11

## Project Structure
