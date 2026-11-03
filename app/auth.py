from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Form
from app.models import User
from app.database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

password_hash = PasswordHash.recommended()

DbSession = Annotated[Session, Depends(get_db)]


def normalize_email(email: str) -> str:
    return email.strip().lower()


def get_current_user(
    request: Request,
    db: DbSession,
) -> User:
    """Require an authenticated user for protected endpoints."""
    user_id = request.session.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    user = db.get(User, user_id)

    if user is None:
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is no longer valid.",
        )

    return user


class BrowserLoginRequired(Exception):
    def __init__(self, next_url: str):
        self.next_url = next_url


def get_browser_user(request: Request, db: DbSession) -> User:
    user_id = request.session.get("user_id")
    user = db.get(User, user_id) if user_id is not None else None

    if user is None:
        request.session.clear()

        # Keep the redirect local to the application.
        next_url = request.url.path
        if request.url.query:
            next_url += f"?{request.url.query}"

        raise BrowserLoginRequired(next_url)

    return user

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"error": None},
    )


@router.post("/register", response_class=HTMLResponse)
def register(
    request: Request,
    db: DbSession,
    email: str = Form(),
    password: str = Form(),
    confirm_password: str = Form(),
):
    email = normalize_email(email)

    error = None

    if len(email) > 254 or "@" not in email:
        error = "Enter a valid email address."
    elif len(password) < 6:
        error = "Password must be at least 6 characters."
    elif len(password) > 128:
        error = "Password is too long."
    elif password != confirm_password:
        error = "Passwords do not match."
    elif db.scalar(select(User).where(User.email == email)):
        error = "An account with that email already exists."

    if error:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": error, "email": email},
            status_code=400,
        )

    user = User(
        email=email,
        password_hash=password_hash.hash(password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    request.session.clear()
    request.session["user_id"] = user.id

    return RedirectResponse("/issues", status_code=303)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": None},
    )


@router.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    db: DbSession,
    email: str = Form(),
    password: str = Form(),
):
    email = normalize_email(email)

    user = db.scalar(select(User).where(User.email == email))

    if (
        user is None
        or len(password) > 128
        or not password_hash.verify(password, user.password_hash)
    ):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Invalid email or password.", "email": email},
            status_code=401,
        )

    # Rotate the session on login to avoid session fixation.
    request.session.clear()
    request.session["user_id"] = user.id

    return RedirectResponse("/issues", status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)