from fastapi.testclient import TestClient

from app import main
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


def test_preview_shows_desktop_and_phone_frames() -> None:
    response = client.get("/preview")

    assert response.status_code == 200
    assert response.text.count('<iframe src="/"') == 2


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


def test_join_adds_a_person_card() -> None:
    assert "Demo sign-in, no account is created." in client.get("/join").text

    response = client.post(
        "/join", data={"name": "Jo", "skills": "screens, catering", "room": "Connection"}
    )

    assert response.status_code == 200
    assert 'data-person="Jo" data-status="available"' in response.text
    assert "Jo joined, in Connection, available" in response.text
    main.logged_notes.clear()
