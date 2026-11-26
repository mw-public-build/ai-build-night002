"""The web app: pages, HTMX fragments and a health check."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.board import (
    Board,
    Fact,
    Note,
    RoomStatus,
    build_map,
    load_board,
    sort_statuses,
    work_out_statuses,
)
from app.crisis import Crisis, match_room, open_crisis

APP_DIR = Path(__file__).parent

app = FastAPI(title="AI Build Night 002")
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=APP_DIR / "templates")

# Notes logged while the app runs (simulated sends). Kept in memory for the demo.
logged_notes: list[Note] = []


def current_board() -> Board:
    board = load_board()
    board.notes.extend(logged_notes)
    return board


def board_context(board: Board) -> dict:
    statuses = work_out_statuses(board)
    return {
        "people": sort_statuses(statuses),
        "places": build_map(board, statuses),
        "latest_note": max(board.notes, key=lambda note: note.number),
        "notes": sorted(board.notes, key=lambda note: note.number, reverse=True),
        "needs": list(reversed(open_needs(board))),
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html", board_context(current_board()))


async def read_form(request: Request) -> dict[str, str]:
    """Parse a url-encoded form with the standard library (no python-multipart)."""
    body = (await request.body()).decode("utf-8")
    return {key: values[0] for key, values in parse_qs(body).items()}


NOTES_CHANGED = {"HX-Trigger": "notes-changed"}

# The 7:10 update, loaded with one click for the demo.
TWIST_NOTES = [
    {
        "author": "Kai",
        "title": "Welcome update from Kai",
        "text": "Welcome done, I'm free. I'll take the Novelty screen.",
        "responds_to_room": "Novelty",
        "fact": Fact(
            person="Kai",
            status="available",
            room="Connection",
            skills=[],
            activity="on the phone",
        ),
    },
    {
        "author": "Casey",
        "title": "Desk update from Casey",
        "text": "Sam got pulled into another member's setup and can't leave.",
        "fact": Fact(
            person="Sam",
            status="busy",
            room=None,
            skills=[],
            activity="tied up with another member",
        ),
    },
]


@app.get("/preview", response_class=HTMLResponse)
def preview(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "preview.html")


@app.get("/fragments/board", response_class=HTMLResponse)
def board_fragment(request: Request) -> HTMLResponse:
    context = board_context(current_board())
    return templates.TemplateResponse(request, "partials/board.html", context)


@app.get("/fragments/feed", response_class=HTMLResponse)
def feed_fragment(request: Request) -> HTMLResponse:
    context = board_context(current_board())
    return templates.TemplateResponse(request, "partials/feed.html", context)


@app.post("/crisis", response_class=HTMLResponse)
async def crisis(request: Request) -> HTMLResponse:
    form = await read_form(request)
    problem = form.get("problem", "")
    board = current_board()
    room = match_room(problem, board)
    if room:
        status = RoomStatus(room=room, text=problem, level="issue")
        with_presenter = Fact(
            person=board.you, status="busy", room=room, skills=[], activity="with the presenter"
        )
        note = log_note(board, f"Alert in {room}", problem, [with_presenter], author=board.you)
        note.room_statuses.append(status)
    response = crisis_response(request, problem)
    response.headers.update(NOTES_CHANGED)
    return response


@app.get("/fragments/crisis", response_class=HTMLResponse)
def crisis_fragment(request: Request, problem: str = "") -> HTMLResponse:
    return crisis_response(request, problem)


def crisis_response(request: Request, problem: str) -> HTMLResponse:
    board = current_board()
    opened = open_crisis(problem, board, work_out_statuses(board))
    return templates.TemplateResponse(request, "partials/crisis.html", {"crisis": opened})


@app.post("/crisis/send", response_class=HTMLResponse)
async def send(request: Request) -> HTMLResponse:
    form = await read_form(request)
    kind = form.get("kind", "request")
    names = [name for name in form.get("names", "").split(",") if name]
    log_send(current_board(), kind, form.get("text", ""), form.get("room") or None, names)
    return HTMLResponse("", headers=NOTES_CHANGED)


@app.post("/notes", response_class=HTMLResponse)
async def add_note(request: Request) -> HTMLResponse:
    form = await read_form(request)
    facts = []
    if form.get("person"):
        fact = Fact(
            person=form["person"],
            status=form.get("status", "unknown"),
            room=form.get("room") or None,
            skills=[],
            activity=form.get("activity") or None,
        )
        facts.append(fact)
    author = form.get("author") or None
    title = f"Note from {author}" if author else "Note"
    note = log_note(current_board(), title, form.get("text", ""), facts, author, form.get("time"))
    if form.get("responds_to", "").isdigit():
        note.responds_to = int(form["responds_to"])
    if form.get("status_room") and form.get("status_text"):
        room_status = RoomStatus(
            room=form["status_room"],
            text=form["status_text"],
            level=form.get("status_level", "issue"),
        )
        note.room_statuses.append(room_status)
    return HTMLResponse("", headers=NOTES_CHANGED)


@app.post("/notes/twist", response_class=HTMLResponse)
def load_twist() -> HTMLResponse:
    for item in TWIST_NOTES:
        board = current_board()
        note = log_note(board, item["title"], item["text"], [item["fact"]], item["author"])
        room = item.get("responds_to_room")
        need = next((n for n in reversed(open_needs(board)) if n.room == room), None)
        if need:
            note.responds_to = need.note.number
    return HTMLResponse("", headers=NOTES_CHANGED)


@dataclass
class Need:
    note: Note
    room: str | None
    crisis: Crisis
    taken_by: Note | None = None


def open_needs(board: Board) -> list[Need]:
    """Alerts posted so far, each with the rules' suggestion and who took it."""
    statuses = work_out_statuses(board)
    needs = []
    for note in board.notes:
        if not note.room_statuses or note.sent_kind:
            continue
        crisis = open_crisis(note.text, board, statuses)
        taken = [n for n in board.notes if n.responds_to == note.number]
        needs.append(Need(note, note.room_statuses[0].room, crisis, taken[-1] if taken else None))
    return needs


@app.get("/fragments/needs", response_class=HTMLResponse)
def needs_fragment(request: Request) -> HTMLResponse:
    needs = list(reversed(open_needs(current_board())))
    return templates.TemplateResponse(request, "partials/needs.html", {"needs": needs})


@app.post("/needs/{number}/take", response_class=HTMLResponse)
async def take_need(request: Request, number: int) -> HTMLResponse:
    form = await read_form(request)
    person = form.get("person", "")
    board = current_board()
    need = next((n for n in open_needs(board) if n.note.number == number), None)
    if need and person:
        fact = Fact(
            person=person,
            status="busy",
            room=need.room,
            skills=[],
            activity=f"on need #{number:02d}",
        )
        note = log_note(
            board,
            f"{person} took need #{number:02d}",
            f"I'll take it: {need.note.text}",
            [fact],
            author=person,
        )
        note.responds_to = number
    return HTMLResponse("", headers=NOTES_CHANGED)


def log_note(
    board: Board,
    title: str,
    text: str,
    facts: list[Fact],
    author: str | None = None,
    time: str | None = None,
    sent_kind: str | None = None,
) -> Note:
    """Append a note in memory. With no time given, it takes the latest note's time."""
    latest = max(board.notes, key=lambda note: note.number)
    note = Note(
        number=latest.number + 1,
        time=time or latest.time,
        title=title,
        text=text,
        facts=facts,
        author=author,
        sent_kind=sent_kind,
    )
    logged_notes.append(note)
    return note


def log_send(board: Board, kind: str, text: str, room: str | None, names: list[str]) -> Note:
    """Log a simulated send as a note. The request sends Morgan to the room."""
    if kind == "instruction":
        title = f"{board.you} sent an instruction to {', '.join(names)}"
        facts = []
    else:
        title = f"{board.you} heading to {room or 'the room'} with the presenter"
        facts = [Fact(person=board.you, status="busy", room=room, skills=[])]
    return log_note(board, title, text, facts, author=board.you, sent_kind=kind)


@app.get("/fragments/ping", response_class=HTMLResponse)
def ping(request: Request) -> HTMLResponse:
    server_time = datetime.now().strftime("%H:%M:%S")
    return templates.TemplateResponse(request, "partials/ping.html", {"server_time": server_time})
