# tests/conftest.py
import os
import pytest
os.environ["FLASK_ENV"] = "testing"
os.environ["MONGO_URI"] = "mongodb://localhost:27017"
import utils.scheduler as sched
sched.start_scheduler = lambda *a, **k: None
import app.constraints_routes as _cr
_cr.priorityByAI = lambda constraints, availability: availability

from run import app

@pytest.fixture(scope="session", autouse=True)
def set_testing_env():
    """
    Fixture to run once before any tests. Because it's autouse,
    you don't have to include it explicitly in test signatures.
    It sets FLASK_ENV=testing so your code picks up the 'tests' DB.
    """
    os.environ["FLASK_ENV"] = "testing"

@pytest.fixture(scope="session")
def test_client():
    """
    Creates a Flask test client (an HTTP client for your app).
    scope="session" means we reuse it for all tests in a run.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client   # yield hands the client to your tests
