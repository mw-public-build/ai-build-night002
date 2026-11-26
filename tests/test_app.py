import re

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


def test_signed_in_person_is_pinned_on_top_until_sign_out() -> None:
    visitor = TestClient(app)
    visitor.post("/join", data={"name": "Kai", "skills": "", "room": "Connection"})

    page = visitor.get("/").text
    order = re.findall(r'data-person="(\w+)"', page)
    assert order[0] == "Kai"
    assert "data-you" in page
    assert "Signed in as" in page

    page = visitor.get("/signout").text
    assert "data-you" not in page
    assert 'href="/join"' in page
    main.logged_notes.clear()


def test_three_columns_order_on_each_screen_size() -> None:
    page = client.get("/").text
    columns = dict(re.findall(r'data-column="(\w+)" class="([^"]+)"', page))

    assert set(columns) == {"people", "rooms", "feed"}
    # Phone: Feed, People, Rooms.
    assert "order-1" in columns["feed"].split()
    assert "order-2" in columns["people"].split()
    assert "order-3" in columns["rooms"].split()
    # Medium: People and Rooms side by side, Feed full width below.
    assert "md:order-1" in columns["people"] and "md:order-2" in columns["rooms"]
    assert "md:order-3" in columns["feed"] and "md:col-span-2" in columns["feed"]
    # Wide: People, Feed (widest), Rooms.
    assert "xl:order-1" in columns["people"]
    assert "xl:order-2" in columns["feed"]
    assert "xl:order-3" in columns["rooms"]
    assert "xl:grid-cols-[1fr_1.6fr_1fr]" in page
