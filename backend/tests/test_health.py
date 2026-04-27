"""Smoke tests — health endpoint & mode enum"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.models import OrbitMode, JobStatus, STATUS_LABEL

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "static_orbit" in data["modes"]
    assert "live_orbit" in data["modes"]


def test_orbit_modes_exist():
    assert OrbitMode.static_orbit == "static_orbit"
    assert OrbitMode.live_orbit   == "live_orbit"


def test_status_labels_complete():
    for status in JobStatus:
        assert status in STATUS_LABEL, f"{status} 缺少 STATUS_LABEL"


def test_results_404():
    r = client.get("/api/results/nonexistent-job-id")
    assert r.status_code == 404
