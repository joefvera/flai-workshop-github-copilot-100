"""
Backend tests for the Mergington High School Activities API.

Each test follows the Arrange-Act-Assert (AAA) pattern:
  - Arrange : set up the preconditions and inputs.
  - Act     : call the endpoint under test.
  - Assert  : verify the response and side-effects.

The `client` fixture (defined in conftest.py) handles the shared Arrange
baseline: it resets in-memory state to a pristine copy before every test.
"""

import src.app as app_module


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_all(client):
    # Arrange — no extra setup needed; the fixture provides a fully populated
    #           activities dict.

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # nine activities defined in app.py
    assert "Chess Club" in data
    assert "Programming Class" in data


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_already_registered_returns_400(client):
    # Arrange — sign up the email once so a duplicate attempt can be made
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act — try to sign up the same email again
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_signup_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Underwater Basket Weaving"
    email = "nobody@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/unregister
# ---------------------------------------------------------------------------

def test_unregister_success(client):
    # Arrange — sign up an email first so there is someone to remove
    activity_name = "Programming Class"
    email = "todelete@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")
    assert email in app_module.activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "someone@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_unregister_not_registered_returns_404(client):
    # Arrange — use a valid activity but an email that was never signed up
    activity_name = "Soccer Team"
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    assert "not registered" in response.json()["detail"].lower()
