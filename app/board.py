"""The desk board rules: notes in, each person's status out.

The rules decide who is where. The latest note about a person sets their
status and room; skills add up across notes. No note means unknown.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path

NOTES_PATH = Path(__file__).parent / "data" / "notes.json"

STATUS_ORDER = {"available": 0, "busy": 1, "unknown": 2}


@dataclass
class Fact:
    person: str
    status: str
    room: str | None
    skills: list[str]
    activity: str | None = None


@dataclass
class RoomStatus:
    room: str
    text: str
    level: str  # "ok" or "issue"


@dataclass
class Note:
    number: int
    time: str
    title: str
    text: str
    facts: list[Fact]
    author: str | None = None
    sent_kind: str | None = None  # "instruction" or "request" for a simulated send
    room_statuses: list[RoomStatus] = field(default_factory=list)
    responds_to: int | None = None  # the need (alert note number) this note answers


@dataclass
class Place:
    name: str
    about: str
    note: int


@dataclass
class Booking:
    place: str
    what: str
    note: int


@dataclass
class Board:
    people: list[str]
    you: str
    notes: list[Note]
    places: list[Place] = field(default_factory=list)
    bookings: list[Booking] = field(default_factory=list)


@dataclass
class PersonStatus:
    name: str
    status: str = "unknown"
    room: str | None = None
    skills: list[str] = field(default_factory=list)
    source: Note | None = None
    is_you: bool = False
    activity: str | None = None


def load_board(path: Path = NOTES_PATH) -> Board:
    raw = json.loads(path.read_text(encoding="utf-8"))
    notes = [_note_from_dict(item) for item in raw["notes"]]
    places = [Place(**item) for item in raw.get("places", [])]
    bookings = [Booking(**item) for item in raw.get("bookings", [])]
    return Board(
        people=raw["people"], you=raw["you"], notes=notes, places=places, bookings=bookings
    )


def _note_from_dict(item: dict) -> Note:
    facts = [Fact(**fact) for fact in item["facts"]]
    room_statuses = [RoomStatus(**status) for status in item.get("room_statuses", [])]
    return Note(
        number=item["number"],
        time=item["time"],
        title=item["title"],
        text=item["text"],
        facts=facts,
        room_statuses=room_statuses,
        author=item.get("author"),
    )


def work_out_statuses(board: Board) -> list[PersonStatus]:
    statuses = {name: PersonStatus(name=name, is_you=name == board.you) for name in board.people}
    for note in sorted(board.notes, key=lambda n: n.number):
        for fact in note.facts:
            person = statuses.setdefault(fact.person, PersonStatus(name=fact.person))
            _apply_fact(person, fact, note)
    return list(statuses.values())


def _apply_fact(person: PersonStatus, fact: Fact, note: Note) -> None:
    person.status = fact.status
    person.room = fact.room
    person.activity = fact.activity
    person.source = note
    for skill in fact.skills:
        if skill not in person.skills:
            person.skills.append(skill)


UNKNOWN_PLACE = "Location unknown"


@dataclass
class MapPlace:
    name: str
    about: str | None = None
    about_note: int | None = None
    bookings: list[Booking] = field(default_factory=list)
    people: list[PersonStatus] = field(default_factory=list)
    status: RoomStatus | None = None
    status_note: Note | None = None
    schedule: list[Note] = field(default_factory=list)


def build_map(board: Board, statuses: list[PersonStatus]) -> list[MapPlace]:
    """Group people by the room the rules put them in; no room goes under unknown."""
    places = {
        place.name: MapPlace(name=place.name, about=place.about, about_note=place.note)
        for place in board.places
    }
    for booking in board.bookings:
        places.setdefault(booking.place, MapPlace(name=booking.place)).bookings.append(booking)
    for note in sorted(board.notes, key=lambda n: n.number):
        for room_status in note.room_statuses:
            place = places.setdefault(room_status.room, MapPlace(name=room_status.room))
            place.status = room_status
            place.status_note = note
    for place in places.values():
        place.schedule = room_schedule(board, place.name)
    unknown = MapPlace(name=UNKNOWN_PLACE)
    for person in sort_statuses(statuses):
        if person.room is None:
            unknown.people.append(person)
        else:
            places.setdefault(person.room, MapPlace(name=person.room)).people.append(person)
    return [*places.values(), unknown]


def room_schedule(board: Board, room: str) -> list[Note]:
    """The day in one room: bookings, people placed there, and alerts, oldest first."""
    booking_notes = {booking.note for booking in board.bookings if booking.place == room}
    schedule = []
    for note in sorted(board.notes, key=lambda n: n.number):
        in_room = any(fact.room == room for fact in note.facts) or any(
            status.room == room for status in note.room_statuses
        )
        if in_room or note.number in booking_notes:
            schedule.append(note)
    return schedule


def has_skill(person: PersonStatus, skill: str | None) -> bool:
    """True when any of the person's skills mentions the asked-for skill."""
    return skill is not None and any(skill in own for own in person.skills)


def sort_statuses(statuses: list[PersonStatus], skill: str | None = None) -> list[PersonStatus]:
    def sort_key(person: PersonStatus) -> tuple[int, int, str]:
        return (STATUS_ORDER[person.status], 0 if has_skill(person, skill) else 1, person.name)

    return sorted(statuses, key=sort_key)
