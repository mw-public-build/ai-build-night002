# ai-build-night002

A web app built live at AI Build Night 002. What it does is decided on
stream; until then it is a working skeleton.

The user-level `CLAUDE.md` holds the shared rules. This file adds what
is specific to this project.

## Doc set

- **Requirements.** `docs/requirements.md`.
- **Spec.** `docs/spec.md`. It is the allowlist for packages and tools.
- **Plan.** `docs/plan.md`.

## Layout

- **`app/main.py`.** The FastAPI app: pages, HTMX fragments and `/health`.
- **`app/templates/`.** Jinja2 pages; `partials/` holds HTMX fragments.
- **`app/static/`.** Built CSS, the pinned htmx file and the fonts.
- **`styles/app.css`.** The Tailwind source and the theme.
- **`tests/`.** pytest, with FastAPI's test client.

## Commands

- **Run.** `uv run uvicorn app.main:app --reload --port 8000`
- **Test.** `uv run pytest`
- **Lint.** `uv run ruff check .` and `uv run ruff format --check .`
- **Build CSS.** See the README. Rebuild after changing templates or
  `styles/app.css`, and commit `app/static/css/app.css`.

## Rules

- No Anthropic or Claude names or logos in the UI. The look is warm and
  quiet, with a teal-blue accent.
- Icons are Heroicons, pasted into templates as inline SVG.
- htmx and the fonts are files in the repo; no CDNs.
