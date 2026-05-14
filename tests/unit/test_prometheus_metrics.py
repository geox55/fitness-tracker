"""Эндпоинт /metrics для Prometheus (мониторинг стека)."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_metrics_endpoint_returns_prometheus_format() -> None:
    client = TestClient(create_app())
    response = client.get("/metrics")
    assert response.status_code == 200
    body = response.text
    assert "# HELP" in body or "# TYPE" in body
