import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)


# Preserve original activities and reset before each test
original_activities = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities = copy.deepcopy(original_activities)
    yield
    app_module.activities = copy.deepcopy(original_activities)


def test_get_activities():
    # Arrange: (fixture resets the in-memory DB)

    # Act
    res = client.get("/activities")

    # Assert
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_duplicate():
    # Arrange
    email = "test.user@mergington.edu"
    activity = "Chess Club"
    activity_enc = quote(activity, safe="")

    # Act: sign up
    res = client.post(f"/activities/{activity_enc}/signup", params={"email": email})

    # Assert: signup succeeded
    assert res.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    # Act: attempt duplicate signup
    res2 = client.post(f"/activities/{activity_enc}/signup", params={"email": email})

    # Assert: duplicate is rejected
    assert res2.status_code == 400


def test_delete_participant():
    # Arrange
    email = "delete.me@mergington.edu"
    activity = "Programming Class"
    activity_enc = quote(activity, safe="")

    # Act: add participant
    res = client.post(f"/activities/{activity_enc}/signup", params={"email": email})

    # Assert: added
    assert res.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    # Act: remove participant
    res2 = client.delete(f"/activities/{activity_enc}/participants", params={"email": email})

    # Assert: removed
    assert res2.status_code == 200
    assert email not in app_module.activities[activity]["participants"]

    # Act: remove again
    res3 = client.delete(f"/activities/{activity_enc}/participants", params={"email": email})

    # Assert: now returns 404
    assert res3.status_code == 404
