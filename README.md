# AI Build Night 002

The problem: Morgan at the front desk is a bottleneck. Every need goes through her. KWENCH Live relieves that: needs and status are shared with everyone, so people pick up problems themselves, and the latest notes show who's really free.

A web app built live with FastAPI, HTMX and Tailwind.

## KWENCH Live

Problems and needs are posted for everyone; people answer them as they
post their status. The rules show who's really free from the latest
notes, citing each one.

It is a live status page everyone at KWENCH can see: who is where, who is free,
and what needs help. Every status comes from a note in the feed, and the
page cites the note it came from. Fixed rules decide who is free; no AI
makes that call. The people and notes are the fictional KWENCH story.

Run it with `uv run uvicorn app.main:app --reload --port 8000` and open
http://localhost:8000. Restarting the server clears the posts added
during a demo. http://localhost:8000/preview shows the page in a desktop
frame and a phone frame side by side.

Demo:

1. Open the page. Sam is green (free in Novelty, note 07), Kai is red
   (busy with a welcome in Connection, note 06).
2. Post the alert "slides won't show in Novelty". It appears under
   **Open needs** in red, and Novelty gets a red status badge. The rules
   suggest Sam; Kai is passed over because of note 06. The alert card
   also drafts a message to Sam and a request to Casey and Priya to help
   build a fallback.
3. Press **Load 7:10 update**. Kai posts "Welcome done, I'm free. I'll
   take the Novelty screen." in answer to the need, and Casey posts that
   Sam got pulled into another member's setup.
4. Watch Sam turn red and Kai turn green. The need turns amber, "Taken
   by Kai", and the alert re-routes to Kai, citing the new note on why
   not Sam. Anyone can also press **I'll take it** on an open need.

## Run it

You need [uv](https://docs.astral.sh/uv/).

```
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000.

## Run it in a Codespace

On GitHub: **Code → Codespaces → Create codespace on main**. It installs
everything on start. Then run:

```
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

To share the demo, open
the **Ports** tab, right-click port 8000 and set **Port Visibility** to
**Public**.

## Tests and lint

```
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

## Rebuild the CSS

After changing templates or `styles/app.css`, rebuild and commit
`app/static/css/app.css`. Add `--watch` to rebuild on every save.

PowerShell:

```
$env:TAILWINDCSS_VERSION = "v4.3.5"; uv run tailwindcss -i styles/app.css -o app/static/css/app.css --minify
```

bash:

```
TAILWINDCSS_VERSION=v4.3.5 uv run tailwindcss -i styles/app.css -o app/static/css/app.css --minify
```

The first run downloads Tailwind's standalone program for that version.

## Credits

Fonts: Inter and Source Serif 4, SIL Open Font License (see
`app/static/fonts/`). Icons: Heroicons, MIT.
