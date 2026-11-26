"""The 1:55 answer, from the eight KWENCH notes."""

import re

from fastapi.testclient import TestClient

from app.board import PersonStatus, build_map, load_board, sort_statuses, work_out_statuses
from app.main import app

client = TestClient(app)


def statuses_by_name() -> dict[str, PersonStatus]:
    return {person.name: person for person in work_out_statuses(load_board())}


def test_sam_is_available_in_novelty_from_note_07() -> None:
    sam = statuses_by_name()["Sam"]

    assert sam.status == "available"
    assert sam.room == "Novelty"
    assert sam.source.number == 7
    assert sam.source.time == "1:54 p.m."
    assert sam.skills == ["screens", "laptop setup"]


def test_kai_is_busy_in_connection_from_note_06() -> None:
    kai = statuses_by_name()["Kai"]

    assert kai.status == "busy"
    assert kai.room == "Connection"
    assert kai.source.number == 6
    assert kai.skills == ["meeting-room screens"]


def test_morgan_is_at_the_front_desk_and_is_you() -> None:
    morgan = statuses_by_name()["Morgan"]

    assert morgan.room == "Front desk"
    assert morgan.source.number == 3
    assert morgan.is_you


def test_casey_and_priya_are_unknown_with_no_note() -> None:
    people = statuses_by_name()

    for name in ("Casey", "Priya"):
        assert people[name].status == "unknown"
        assert people[name].room is None
        assert people[name].source is None


def test_sort_puts_available_first_then_busy_then_unknown() -> None:
    names = [person.name for person in sort_statuses(work_out_statuses(load_board()))]

    assert names == ["Morgan", "Sam", "Kai", "Casey", "Priya"]


def test_asked_for_skill_goes_first_within_a_group() -> None:
    people = sort_statuses(work_out_statuses(load_board()), skill="screens")

    assert people[0].name == "Sam"


def test_map_lists_sam_as_available_in_novelty() -> None:
    board = load_board()
    places = {place.name: place for place in build_map(board, work_out_statuses(board))}

    novelty = places["Novelty"]
    sam = next(person for person in novelty.people if person.name == "Sam")
    assert sam.status == "available"
    assert sam.source.number == 7
    assert [booking.note for booking in novelty.bookings] == [2]
    assert [person.name for person in places["Location unknown"].people] == ["Casey", "Priya"]


def test_page_shows_cards_in_sorted_order_with_sources() -> None:
    response = client.get("/")

    assert response.status_code == 200
    order = re.findall(r'data-person="(\w+)"', response.text)
    assert order == ["Morgan", "Sam", "Kai", "Casey", "Priya"]
    assert "bg-green-50" in response.text
    assert "bg-red-50" in response.text
    assert "From note 07 · 1:54 p.m." in response.text
    assert "From note 06 · 1:50 p.m." in response.text
    assert "No note on where they are now." in response.text


def test_room_schedule_lists_the_day_from_the_notes() -> None:
    board = load_board()
    places = {place.name: place for place in build_map(board, work_out_statuses(board))}

    assert [note.number for note in places["Novelty"].schedule] == [2, 5, 7]
    assert [note.number for note in places["Connection"].schedule] == [5, 6]
    assert 'data-schedule="Novelty"' in client.get("/").text
