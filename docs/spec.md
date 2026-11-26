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
