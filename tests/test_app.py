from fastapi.testclient import TestClient
from src.app import app

import pytest

@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    # verify some known activity exists
    assert "Chess Club" in data


def test_signup_and_remove_participant(client):
    activity_name = "Chess Club"
    email = "test+copilot@example.com"

    # Ensure email is not already in participants
    r = client.get("/activities")
    participants = r.json()[activity_name]["participants"]
    if email in participants:
        # remove if test email somehow present from previous runs
        client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Sign up (use params to ensure proper URL encoding)
    r = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert r.status_code in (200, 201)

    # Confirm participant added
    r = client.get("/activities")
    participants = r.json()[activity_name]["participants"]
    assert email in participants

    # Signing up again should return 400 (already signed up)
    r = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert r.status_code == 400

    # Remove participant (use params)
    r = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
    assert r.status_code == 200

    # Confirm participant removed
    r = client.get("/activities")
    participants = r.json()[activity_name]["participants"]
    assert email not in participants
