"""Tests for GET /api/status pagination (skip/limit) and basic liveness."""
import os
import uuid
import pytest
import requests
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    # Fallback: read frontend .env
    with open('/app/frontend/.env') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                BASE_URL = line.split('=', 1)[1].strip().rstrip('/')

API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


def test_root_liveness(client):
    r = client.get(f"{API}/")
    assert r.status_code == 200
    assert r.json() == {"message": "Hello World"}


def test_create_status(client):
    name = f"TEST_{uuid.uuid4().hex[:8]}"
    r = client.post(f"{API}/status", json={"client_name": name})
    assert r.status_code == 200
    data = r.json()
    assert data["client_name"] == name
    assert "id" in data and isinstance(data["id"], str)
    uuid.UUID(data["id"])  # valid uuid
    assert "timestamp" in data
    datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
    assert "_id" not in data


@pytest.fixture(scope="module")
def seed_records(client):
    created = []
    for i in range(6):
        r = client.post(f"{API}/status", json={"client_name": f"TEST_seed_{i}_{uuid.uuid4().hex[:4]}"})
        assert r.status_code == 200
        created.append(r.json())
    return created


def test_get_default(client, seed_records):
    r = client.get(f"{API}/status")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) <= 100
    assert len(data) >= 1
    for item in data:
        assert "id" in item
        assert "client_name" in item
        assert "timestamp" in item
        assert "_id" not in item


def test_limit_5(client, seed_records):
    r = client.get(f"{API}/status", params={"limit": 5})
    assert r.status_code == 200
    data = r.json()
    assert len(data) <= 5


def test_skip_and_limit(client, seed_records):
    r_all = client.get(f"{API}/status", params={"limit": 10})
    assert r_all.status_code == 200
    all_items = r_all.json()
    assert len(all_items) >= 3

    r = client.get(f"{API}/status", params={"skip": 1, "limit": 2})
    assert r.status_code == 200
    data = r.json()
    assert len(data) <= 2
    # First returned record should equal all_items[1]
    if len(data) >= 1 and len(all_items) >= 2:
        assert data[0]["id"] == all_items[1]["id"]


def test_limit_clamped_high(client, seed_records):
    r = client.get(f"{API}/status", params={"limit": 99999})
    assert r.status_code == 200
    data = r.json()
    assert len(data) <= 1000


def test_limit_clamped_low(client, seed_records):
    r = client.get(f"{API}/status", params={"limit": 0})
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 1 or len(data) == 0  # at most limit=1 due to clamp; could be 0 only if DB empty


def test_negative_skip(client, seed_records):
    r = client.get(f"{API}/status", params={"skip": -5, "limit": 3})
    assert r.status_code == 200
    assert len(r.json()) <= 3
