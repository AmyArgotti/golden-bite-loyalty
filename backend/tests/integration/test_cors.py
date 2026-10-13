from fastapi.testclient import TestClient

from app.main import app


def test_browser_preflight_allows_local_customer_frontend():
    response = TestClient(app).options(
        "/api/v1/me",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_browser_preflight_rejects_unconfigured_origin():
    response = TestClient(app).options(
        "/api/v1/me",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
