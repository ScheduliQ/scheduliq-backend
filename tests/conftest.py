# tests/conftest.py
import os
import pytest
import sys
import types

from dotenv import load_dotenv
import utils.scheduler as sched
sched.start_scheduler = lambda *a, **k: None

import app.constraints_routes as _cr
_cr.priorityByAI = lambda constraints, availability: availability

os.environ["FLASK_ENV"] = "testing"
os.environ["MONGO_URI"] = "mongodb://localhost:27017"

fake_fb_admin = types.ModuleType("firebase_admin")
fake_fb_admin.credentials = types.SimpleNamespace(
    Certificate=lambda *a, **k: None
)
fake_fb_admin.initialize_app = lambda *a, **k: None
fake_fb_admin.auth = types.SimpleNamespace(
    InvalidIdTokenError=Exception,
    ExpiredIdTokenError=Exception,
    RevokedIdTokenError=Exception,
    set_custom_user_claims=lambda uid, claims: None,
    create_user=lambda **kw: types.SimpleNamespace(
        uid="dummy",
        user_metadata=types.SimpleNamespace(creation_timestamp=0)
    ),
    verify_id_token=lambda token: {"email": "test@example.com"}
)
sys.modules["firebase_admin"]             = fake_fb_admin
sys.modules["firebase_admin.credentials"] = fake_fb_admin.credentials
sys.modules["firebase_admin.auth"]        = fake_fb_admin.auth

fake_cfg = types.ModuleType("configs.firebaseConfig")
fake_cfg.firebaseApp = None
sys.modules["configs.firebaseConfig"] = fake_cfg


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
