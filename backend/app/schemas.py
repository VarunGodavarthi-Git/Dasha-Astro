from datetime import date, datetime, time
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ChartRequest(BaseModel):
    date_of_birth: date
    time_of_birth: time
    city_name: str = Field(..., min_length=2, max_length=120)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    timezone: str | None = Field(default=None, min_length=1, max_length=120)
    question: str | None = Field(default=None, max_length=1200)
    user_email: EmailStr | None = None
    user_name: str | None = Field(default=None, max_length=255)


class ChartResponse(BaseModel):
    chart: dict[str, Any]


class LocationSearchResponse(BaseModel):
    query: str
    display_name: str
    latitude: float
    longitude: float
    timezone: str


class ChatLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_email: str | None
    user_name: str | None
    city_name: str
    prompt_text: str
    ai_response: str
    model: str
    created_at: datetime


class ClearLogsResponse(BaseModel):
    deleted: int
