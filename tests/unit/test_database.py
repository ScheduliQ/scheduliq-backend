# tests/unit/test_database.py

import os
import importlib
import pytest

def test_get_collection_switches_db(monkeypatch):
    """
    Unit test for models/database.py.
    Uses pytest's built‑in 'monkeypatch' fixture to set an env var,
    then reloads the module to pick up the change.
    """
    # 1. Force FLASK_ENV to "testing"
    monkeypatch.setenv("FLASK_ENV", "testing")
    import models.database as db_mod
    importlib.reload(db_mod)

    # 2. The module-level 'db' should now point at the 'tests' database
    assert db_mod.db.name == "tests"

    # 3. get_collection should return a pymongo Collection whose name matches the argument
    col = db_mod.get_collection("just")
    assert col.name == "just"
