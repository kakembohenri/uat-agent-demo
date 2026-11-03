from pathlib import Path
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Query,
    Request,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.auth import get_browser_user, get_current_user
from app.database import get_db
from app.models import Issue
from app.schemas import (
    IssueCreate,
    IssueUpdate,
)
from app.models import User

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).parent / "templates")
)

DbSession = Annotated[Session, Depends(get_db)]
BrowserUser = Annotated[User, Depends(get_browser_user)]
ApiUser = Annotated[User, Depends(get_current_user)]


def find_issue(
    db: Session,
    issue_id: int,
    user_id: int,
) -> Issue:
    issue = db.scalar(
        select(Issue).where(
            Issue.id == issue_id,
            Issue.user_id == user_id,
        )
    )

    if issue is None:
        raise HTTPException(
            status_code=404,
            detail="Issue not found.",
        )

    return issue


# -------------------------
# Browser / HTML routes
# -------------------------

# @router.get("/", include_in_schema=False)
# def home():
#     return RedirectResponse("/issues", status_code=303)

@router.get("/", include_in_schema=False)
def home():
    return RedirectResponse("/login", status_code=303)


@router.get("/issues", response_class=HTMLResponse)
def list_issues(
    request: Request,
    db: DbSession,
    current_user: BrowserUser,
    q: str = Query(default="", max_length=150),
):
    statement = select(Issue).where(
        Issue.user_id == current_user.id
    )

    if q.strip():
        term = f"%{q.strip()}%"
        statement = statement.where(
            or_(
                Issue.title.ilike(term),
                Issue.description.ilike(term),
            )
        )

    statement = statement.order_by(Issue.created_at.desc())
    issues = db.scalars(statement).all()

    return templates.TemplateResponse(
        request=request,
        name="issues.html",
        context={
            "issues": issues,
            "q": q,
            "current_user": current_user
        },
    )


@router.get("/issues/new", response_class=HTMLResponse)
def new_issue_form(request: Request, current_user: BrowserUser):
    return templates.TemplateResponse(
        request=request,
        name="issue_form.html",
        context={"errors": [], "form": {}, 
            "current_user": current_user
                 },
    )


@router.post("/issues/new", response_class=HTMLResponse)
def create_issue_from_form(
    request: Request,
    db: DbSession,
    current_user: BrowserUser,
    title: Annotated[str, Form()],
    description: Annotated[str, Form()] = "",
    priority: Annotated[str, Form()] = "Medium",
):
    form = {
        "title": title,
        "description": description,
        "priority": priority,
        "user_id": current_user.id,
    }

    try:
        data = IssueCreate.model_validate(form)
    except ValidationError as exc:
        errors = [
            error["msg"].replace("Value error, ", "")
            for error in exc.errors()
        ]

        return templates.TemplateResponse(
            request=request,
            name="issue_form.html",
            context={"errors": errors, "form": form},
            status_code=422,
        )

    issue = Issue(
        title=data.title,
        description=data.description,
        priority=data.priority,
        user_id=current_user.id,
    )

    db.add(issue)
    db.commit()
    db.refresh(issue)

    return RedirectResponse(
        url=f"/issues/{issue.id}",
        status_code=303,
    )


@router.get("/issues/{issue_id}", response_class=HTMLResponse)
def issue_detail(
    request: Request,
    issue_id: int,
    db: DbSession,
    current_user: BrowserUser
):
    issue = find_issue(db, issue_id, current_user.id)

    return templates.TemplateResponse(
        request=request,
        name="issue_detail.html",
        context={"issue": issue, "errors": []},
    )


@router.post("/issues/{issue_id}/update")
def update_issue_from_form(
    issue_id: int,
    db: DbSession,
    current_user: BrowserUser,
    status_value: Annotated[str, Form(alias="status")],
    priority: Annotated[str, Form()],
):
    issue = find_issue(db, issue_id, current_user.id)

    try:
        data = IssueUpdate.model_validate(
            {
                "status": status_value,
                "priority": priority,
            }
        )
    except ValidationError as exc:
        # The API gives detailed validation errors. This browser
        # endpoint redirects back; its UI uses valid select options.
        raise HTTPException(
            status_code=422,
            detail=exc.errors(),
        ) from exc

    issue.status = data.status
    issue.priority = data.priority

    db.commit()

    return RedirectResponse(
        url=f"/issues/{issue.id}",
        status_code=303,
    )
