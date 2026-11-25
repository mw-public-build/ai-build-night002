"""The web app: pages, HTMX fragments and a health check."""

from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

APP_DIR = Path(__file__).parent

app = FastAPI(title="AI Build Night 002")
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=APP_DIR / "templates")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html")


@app.get("/fragments/ping", response_class=HTMLResponse)
def ping(request: Request) -> HTMLResponse:
    server_time = datetime.now().strftime("%H:%M:%S")
    return templates.TemplateResponse(request, "partials/ping.html", {"server_time": server_time})
