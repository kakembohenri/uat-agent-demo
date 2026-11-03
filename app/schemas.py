from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Priority = Literal["Low", "Medium", "High"]
IssueStatus = Literal["Open", "In Progress", "Resolved"]


class IssueCreate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str = Field(default="", max_length=5000)
    priority: Priority = "Medium"
    user_id: int

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Title cannot be empty.")

        return value


class IssueUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=150)
    description: str | None = Field(default=None, max_length=5000)
    priority: Priority | None = None
    status: IssueStatus | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()

            if not value:
                raise ValueError("Title cannot be empty.")

        return value

class UserSnippetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str

class IssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    priority: Priority
    status: IssueStatus
    created_at: datetime
    updated_at: datetime

    user_id: int
    owner: UserSnippetResponse