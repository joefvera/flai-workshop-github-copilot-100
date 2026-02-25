import copy
import pytest
from fastapi.testclient import TestClient

import src.app as app_module
from src.app import app

# Snapshot of the original activities state taken at import time
_ORIGINAL_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture
def client():
    """
    Arrange (shared baseline): restore the activities dict to its original
    state before each test so tests are fully isolated, then yield a
    TestClient ready for use.
    """
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(_ORIGINAL_ACTIVITIES))
    yield TestClient(app)
