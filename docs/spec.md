# Spec

## Stack

The allowlist. Anything else is raised first and added here.

- **Python 3.13**, managed with **uv**.
- **FastAPI** and **uvicorn** for the server.
- **Jinja2** for templates.
- **htmx 2.0.11**, as a file in `app/static/js/`.
- **Tailwind CSS 4.3.5**, run through **pytailwindcss** (no Node).
- **Heroicons**, as inline SVG.
- **Fonts:** Inter (body) and Source Serif 4 (headings), from Fontsource,
  under the SIL Open Font License; files in `app/static/fonts/`.
- **Dev tools:** pytest, httpx2 (for the test client) and ruff.
- **Demo:** a GitHub Codespace from `.devcontainer/devcontainer.json`.

## Look

Warm off-white background, warm dark text, serif headings, sans body,
soft rounded corners and generous spacing. The accent is teal blue. The
colours are theme values in `styles/app.css`:

- **canvas.** `#faf9f5`, the page background.
- **surface.** `#ffffff`, cards.
- **ink.** `#1f1e1d`, text.
- **muted.** `#6b6a65`, secondary text.
- **line.** `#e8e6dc`, borders.
- **accent.** `#0e7490`, buttons and links.
- **accent-strong.** `#155e75`, hover and text on accent-soft.
- **accent-soft.** `#e6f3f6`, highlighted panels.

## Current state

- `/` shows a page with a button that fetches `/fragments/ping` with
  htmx and swaps in the server's time.
- `/health` returns `{"status": "ok"}`.

## The app

To be decided live.

## The build: Desk Board

For Morgan at the front desk: see in seconds who is really here and free, sorted, and get the right person to a member.

### Data
- **Notes.** The eight KWENCH notes from references/build-night-notes.txt, stored in app/data/notes.json. Each has a number, time, title, text, and hand-tagged facts: a list of {person, status (available|busy|unknown), room, skills}. New notes added on the page carry the same facts, picked in the form (this is how the 7:10 twist goes in).
- **People.** Name, skills (Sam: screens, laptop setup; Kai: meeting-room screens), and a status worked out by the rules.

### Rules (they decide; AI never does)
- The latest note about a person sets their status (available, busy or unknown) plus their room.
- No note about where someone is now means unknown, not present.
- Every status shows the note number and time it came from.
- Sort: available first, then busy, then unknown; within a group, people with the asked-for skill first.

### Page
- **Cards.** One per person: name, status badge, room, skills, source note. Morgan shown as "you".
- **Ask + route.** Morgan sees at a glance who everyone is and where they are (cards). She types one request, e.g. "slides won't show in Novelty". The AI (keyword rules, optional claude -p) routes it as two messages: an INSTRUCTION to the tech contact ("Sam: troubleshoot the presenter's screen in Novelty, workshop at 2:00") and a REQUEST to everyone else not locked into a task ("Meet Morgan in Novelty to help put a fallback presentation together"). She presses Send; both are logged as notes (simulated, no real messages). Then Morgan's own card switches to "heading to Novelty with the presenter", working on the fallback.
- **Add note.** A form that appends a note; cards re-sort via htmx.

### AI
- No API key: Michael uses a Claude Pro login. The main path is a keyword match that turns the request into {skill, room}, plus a template that phrases the answer with the note numbers.
- Optional: if the `claude` command is on the PC, call `claude -p` with a short timeout to phrase the answer more naturally. Any failure falls back to the template. No new packages.
- The page also answers "why not Kai?": the 11:00 note says Kai can cover, but the 1:50 note says Kai is busy.
