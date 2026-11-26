from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_reports_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_index_loads_htmx_and_styles() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "/static/js/htmx-2.0.11.min.js" in response.text
    assert "/static/css/app.css" in response.text
    assert 'hx-get="/fragments/ping"' in response.text


def test_ping_returns_a_fragment() -> None:
    response = client.get("/fragments/ping")

    assert response.status_code == 200
    assert "<html" not in response.text
    assert "The server answered at" in response.text


def test_static_files_are_served() -> None:
    for path in (
        "/static/css/app.css",
        "/static/js/htmx-2.0.11.min.js",
        "/static/fonts/inter-latin-wght-normal.woff2",
        "/static/fonts/source-serif-4-latin-wght-normal.woff2",
    ):
        assert client.get(path).status_code == 200, path
