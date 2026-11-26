# AI Build Night 002

A web app built live with FastAPI, HTMX and Tailwind.

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
