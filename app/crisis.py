"""Open a crisis: turn Morgan's request into an instruction and a request.

Keyword match picks the skill and room; the board rules pick the people.
No AI call here; the wording is a template.
"""

from dataclasses import dataclass, field

from app.board import Board, Booking, Note, PersonStatus, has_skill, sort_statuses

SKILL_WORDS = {
    "screens": ("slide", "screen", "laptop", "projector", "display", "hdmi"),
}


@dataclass
class Crisis:
    problem: str
    room: str | None
    skill: str | None
    booking: Booking | None
    tech: PersonStatus | None
    helpers: list[PersonStatus] = field(default_factory=list)
    passed_over: list[PersonStatus] = field(default_factory=list)
    instruction: str = ""
    request: str = ""
    instruction_sent: Note | None = None
    request_sent: Note | None = None


def match_skill(problem: str) -> str | None:
    text = problem.lower()
    for skill, words in SKILL_WORDS.items():
        if any(word in text for word in words):
            return skill
    return None


def match_room(problem: str, board: Board) -> str | None:
    text = problem.lower()
    for place in board.places:
        if place.name.lower() in text:
            return place.name
    return None


def open_crisis(problem: str, board: Board, statuses: list[PersonStatus]) -> Crisis:
    skill = match_skill(problem)
    room = match_room(problem, board)
    booking = next((b for b in board.bookings if b.place == room), None)
    others = [person for person in sort_statuses(statuses, skill) if not person.is_you]
    skilled = [person for person in others if has_skill(person, skill)]
    tech = next((person for person in skilled if person.status == "available"), None)
    passed_over = [person for person in skilled if person is not tech]
    helpers = [person for person in others if person is not tech and person.status != "busy"]
    crisis = Crisis(problem, room, skill, booking, tech, helpers, passed_over)
    crisis.instruction = _instruction_text(crisis)
    crisis.request = _request_text(crisis, board.you)
    crisis.instruction_sent = _sent_note(board, "instruction", crisis.instruction)
    crisis.request_sent = _sent_note(board, "request", crisis.request)
    return crisis


def _sent_note(board: Board, kind: str, text: str) -> Note | None:
    """The note that logged this exact message, if it was sent. A re-route changes
    the text, so the new message shows a Send button again."""
    if not text:
        return None
    sent = [note for note in board.notes if note.sent_kind == kind and note.text == text]
    return sent[-1] if sent else None


def _instruction_text(crisis: Crisis) -> str:
    if crisis.tech is None:
        return ""
    where = crisis.room or crisis.tech.room or "the room"
    text = f"{crisis.tech.name}: troubleshoot the presenter's screen in {where}"
    if crisis.booking:
        text += f", {crisis.booking.what}"
    return text if text.endswith(".") else text + "."


def _request_text(crisis: Crisis, you: str) -> str:
    if not crisis.helpers:
        return ""
    names = ", ".join(person.name for person in crisis.helpers)
    where = crisis.room or "the room"
    return f"{names}: meet {you} in {where} to help put a fallback presentation together."
