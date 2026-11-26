"""Opening a crisis at 1:55, sending its two messages, and the 7:10 re-route."""

import re

import pytest
from fastapi.testclient import TestClient

from app import main
from app.board import load_board, work_out_statuses
from app.crisis import Crisis, open_crisis

client = TestClient(main.app)

PROBLEM = "slides won't show in Novelty"


@pytest.fixture(autouse=True)
def clear_logged_notes() -> None:
    main.logged_notes.clear()


def open_now() -> Crisis:
    board = main.current_board()
    return open_crisis(PROBLEM, board, work_out_statuses(board))


def test_crisis_picks_sam_and_passes_over_kai() -> None:
    board = load_board()
    crisis = open_crisis(PROBLEM, board, work_out_statuses(board))

    assert crisis.room == "Novelty"
    assert crisis.skill == "screens"
    assert crisis.tech.name == "Sam"
    assert [person.name for person in crisis.passed_over] == ["Kai"]
    assert crisis.instruction == (
        "Sam: troubleshoot the presenter's screen in Novelty, Field Notes workshop at 2:00 p.m."
    )
    assert [person.name for person in crisis.helpers] == ["Casey", "Priya"]
    assert crisis.request == (
        "Casey, Priya: meet Morgan in Novelty to help put a fallback presentation together."
    )


def test_page_has_chat_panels_and_notes() -> None:
    response = client.get("/")

    assert 'hx-post="/crisis"' in response.text
    assert 'id="rooms"' in response.text
    assert 'id="people"' in response.text
    assert 'id="feed"' in response.text
    assert 'hx-post="/notes/twist"' in response.text


def test_open_crisis_returns_a_card_with_two_sends() -> None:
    response = client.post("/crisis", data={"problem": PROBLEM})

    assert response.status_code == 200
    assert "Alert open" in response.text
    assert "Not Kai: busy in Connection (note 06, 1:50 p.m.)" in response.text
    assert response.text.count('hx-post="/crisis/send"') == 2


def test_send_logs_notes_and_marks_the_crisis_sent() -> None:
    client.post("/crisis", data={"problem": PROBLEM})
    crisis = open_now()
    client.post(
        "/crisis/send",
        data={"kind": "instruction", "text": crisis.instruction, "room": "Novelty", "names": "Sam"},
    )
    client.post(
        "/crisis/send",
        data={"kind": "request", "text": crisis.request, "room": "Novelty", "names": ""},
    )

    assert [note.number for note in main.logged_notes] == [9, 10, 11]
    card = client.get("/fragments/crisis", params={"problem": PROBLEM}).text
    assert "logged as note 10" in card
    assert "logged as note 11" in card
    board = client.get("/fragments/board").text
    morgan_on_map = re.search(r'data-map-person="Morgan" data-status="(\w+)"', board)
    assert morgan_on_map.group(1) == "busy"


def test_opening_a_crisis_marks_the_room_with_an_issue() -> None:
    client.post("/crisis", data={"problem": PROBLEM})

    board = client.get("/fragments/board").text
    assert 'data-room-status="issue"' in board
    assert "slides won&#39;t show in Novelty · note 09" in board


def test_twist_reroutes_the_crisis_to_kai() -> None:
    client.post("/notes/twist")

    crisis = open_now()
    assert crisis.tech.name == "Kai"
    assert crisis.instruction.startswith("Kai: troubleshoot the presenter's screen in Novelty")
    assert [person.name for person in crisis.passed_over] == ["Sam"]
    assert crisis.passed_over[0].source.number == 10
    card = client.get("/fragments/crisis", params={"problem": PROBLEM}).text
    assert "Not Sam: busy (note 10" in card
    assert "tied up with another member" in client.get("/fragments/board").text


def test_add_note_form_updates_people_and_feed() -> None:
    client.post(
        "/notes",
        data={
            "author": "Kai",
            "text": "Free now",
            "person": "Kai",
            "status": "available",
            "room": "Connection",
            "activity": "on the phone",
        },
    )

    board = client.get("/fragments/board").text
    assert re.search(r'data-person="Kai" data-status="available"', board)
    assert "on the phone" in board
    assert "Free now" in client.get("/fragments/feed").text


def test_open_need_can_be_taken_and_twist_answers_it() -> None:
    client.post("/crisis", data={"problem": PROBLEM})
    needs = client.get("/fragments/needs").text
    assert 'data-need="9" data-taken="no"' in needs
    assert 'Suggested: <span class="font-medium">Sam</span>' in needs

    client.post("/notes/twist")

    needs = client.get("/fragments/needs").text
    assert 'data-need="9" data-taken="yes"' in needs
    assert "Taken by Kai, note 10" in needs


def test_ill_take_it_posts_a_response() -> None:
    client.post("/crisis", data={"problem": PROBLEM})
    client.post("/needs/9/take", data={"person": "Sam"})

    assert main.logged_notes[-1].responds_to == 9
    assert "Taken by Sam, note 10" in client.get("/fragments/needs").text


def test_posting_an_alert_sends_morgan_to_the_room() -> None:
    client.post("/crisis", data={"problem": PROBLEM})

    board = client.get("/fragments/board").text
    assert re.search(r'data-person="Morgan" data-status="busy"', board)
    assert "with the presenter" in board


def test_card_status_update_answers_a_need() -> None:
    assert 'id="update-Kai"' in client.get("/").text
    client.post("/crisis", data={"problem": PROBLEM})
    client.post(
        "/notes",
        data={
            "author": "Kai",
            "person": "Kai",
            "status": "busy",
            "room": "Novelty",
            "text": "On my way",
            "responds_to": "9",
        },
    )

    assert "Taken by Kai, note 10" in client.get("/fragments/needs").text
