from app import app


def test_health():
    resp = app.test_client().get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_index():
    resp = app.test_client().get("/")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["app"] == "dockerized-app-cicd"
    assert "version" in data


def test_metrics_endpoint():
    resp = app.test_client().get("/metrics")
    assert resp.status_code == 200
    assert "http_requests_total" in resp.get_data(as_text=True)


def test_metrics_increment():
    client = app.test_client()
    client.get("/health")
    body = client.get("/metrics").get_data(as_text=True)
    # The /health request should have been counted.
    assert 'endpoint="/health"' in body


def test_unknown_route_404():
    resp = app.test_client().get("/does-not-exist")
    assert resp.status_code == 404
