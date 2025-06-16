# ScheduliQ - Backend

ScheduliQ is an intelligent employee scheduling system that uses constraint satisfaction programming to automatically generate optimal work schedules based on employee availability, skills, and organizational requirements.

## Project Overview

This backend application provides the API services, scheduling algorithm, and database management for the ScheduliQ system. It's built as a final project for a Software Engineering degree.

### Key Features

- **Intelligent Scheduling**: Constraint-based scheduling algorithm that optimizes for employee preferences and business needs
- **User Management**: Complete authentication and user management system with role-based access control
- **Real-time Updates**: WebSocket-based real-time notifications and schedule updates
- **Constraint Management**: Flexible configuration of scheduling rules and constraints
- **Reporting System**: Comprehensive reporting functionality for management oversight

## Technology Stack

- **Backend Framework**: Flask (Python)
- **Database**: MongoDB
- **Authentication**: Firebase Authentication
- **Scheduling Algorithm**: Google OR-Tools (Constraint Satisfaction Programming)
- **Background Processing**: Celery with Redis
- **Real-time Communication**: Socket.IO
- **Email Service**: Flask-Mail with Gmail SMTP

## Project Structure

```
scheduliq-backend/
│
├── app/                    # Main application directory
│   ├── algorithm/          # Scheduling algorithm implementation
│   ├── middlewares/        # Authentication and request middlewares
│   ├── *_routes.py         # API route definitions
│
├── models/                 # Database models and schemas
│
├── configs/                # Configuration files
│
├── utils/                  # Utility functions and helpers
│
├── tests/                  # Unit and integration tests
│
├── run.py                  # Application entry point
├── tasks.py                # Background task definitions
├── celery_app.py           # Celery configuration
├── socketio_server.py      # Socket.IO server configuration
└── Dockerfile              # Docker configuration
```

## API Endpoints

The backend exposes several RESTful API endpoints:

- **Authentication**: `/auth/*`
- **User Management**: `/user/*`
- **Constraints Management**: `/constraints/*`
- **Schedule Management**: `/schedule/*`
- **Manager Settings**: `/manager-settings/*`
- **Messaging System**: `/manager-messages/*`
- **Notifications**: `/notifications/*`
- **Reports**: `/reports/*`

## Scheduling Algorithm

The core of ScheduliQ is a constraint-based scheduling algorithm implemented using Google's OR-Tools library. The algorithm:

1. Takes into account employee availability and skill sets
2. Enforces business rules like minimum/maximum employees per shift
3. Distributes workload fairly among employees
4. Limits consecutive shifts per employee
5. Prioritizes role assignments based on importance
6. Optimizes based on employee preferences

## Setup and Installation

### Prerequisites

- Python 3.11 or higher
- MongoDB
- Redis (for Celery in production)
- Firebase project (for authentication)

### Local Development Setup

1. Clone the repository

   ```bash
   git clone https://github.com/yourusername/scheduliq-backend.git
   cd scheduliq-backend
   ```

2. Create and activate a virtual environment

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (create a `.env` file)

5. Run the application
   ```bash
   python run.py
   ```

### Docker Deployment

Build and run the Docker container:

```bash
docker build -t scheduliq-backend .
docker run -p 5000:5000 scheduliq-backend
```

## Testing

The project includes a comprehensive testing suite with unit, integration, and end-to-end tests to ensure the reliability and correctness of the system.

### Test Structure

```
tests/
│
├── unit/                  # Tests for individual components
│   ├── test_database.py
│   └── test_weekly_schedule_model.py
│
├── integration/           # Tests for API endpoints
│   ├── test_constraints_routes.py
│   └── test_schedule_routes.py
│
├── e2e/                   # End-to-end workflow tests
│   └── test_schedule_lifecycle.py
│
└── conftest.py            # Test configuration and fixtures
```

### Testing Approach

1. **Unit Tests**: Focused on testing individual components and models in isolation:

   - Database connection and operations
   - Weekly schedule model functionality
   - User model operations

2. **Integration Tests**: Testing the interaction between components:

   - API endpoint testing (routes)
   - Database operations through the API
   - Response validation

3. **End-to-End Tests**: Testing complete user workflows:
   - Full schedule creation, modification, and deletion cycle
   - Authentication flows
   - Constraint management workflows

### Test Environment

- Uses a dedicated test database (`tests`) to avoid affecting production data
- Mock Firebase authentication for testing without real credentials
- Pytest fixtures for common setup and teardown operations

### Running Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with coverage report
pytest --cov=app --cov=models --cov=utils
```


## Contributors

- Kobi Alen
- Matan Kahlon

## License

This project was developed as an academic final project for a Software Engineering degree and is intended for educational purposes only. All rights reserved.
