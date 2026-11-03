from contextlib import asynccontextmanager
import os
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.auth import BrowserLoginRequired
from app.database import Base, engine
from app.routes import router
from app.auth import router as auth_router
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

load_dotenv()

SESSION_SECRET = os.getenv("SESSION_SECRET")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Convenient for a demo. Use migrations for a larger application.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Issue Tracker",
    description="Sample application for demonstrating MCP-based UAT.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    session_cookie="issue_tracker_session",
    same_site="lax",
    https_only=False,  # Local development only; set True in production.
    max_age=60 * 60 * 8,
)

@app.exception_handler(BrowserLoginRequired)
async def browser_login_required(
    request: Request,
    exc: BrowserLoginRequired,
):
    # The next parameter is built from the local request path.
    from urllib.parse import urlencode

    query = urlencode({"next": exc.next_url})
    return RedirectResponse(f"/login?{query}", status_code=303)



app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

app.include_router(router)
app.include_router(auth_router)