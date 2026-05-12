from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy import delete, select, func
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from openai import OpenAI

from app.database import Base, SessionLocal, engine, get_db
from app.engine import AstrologyCalculationError, calculate_vedic_chart
from app.location import CityLookupError, GeocodedCity, geocode_city
from app.models import ChatLog, SavedChart
from app.prompts import (
    VEDIC_ASTROLOGY_SYSTEM_PROMPT,
    build_user_prompt,
)
from app.schemas import (
    ChartRequest,
    ChartResponse,
    ChatLogOut,
    ClearLogsResponse,
    LocationSearchResponse,
)

# Load environment variables
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

FRONTEND_ORIGIN = os.getenv(
    "FRONTEND_ORIGIN",
    "https://dasha-astro.vercel.app",
)

ADMIN_EMAIL = os.getenv(
    "ADMIN_EMAIL",
    "admin@example.com",
).lower()

NOMINATIM_USER_AGENT = os.getenv(
    "NOMINATIM_USER_AGENT",
    "dasha-astro-geocoder",
)

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY",
    "",
)

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-4.1-mini",
)

# FastAPI App
app = FastAPI(
    title="Dasha Astro API",
    version="0.2.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_ORIGIN,
        "https://dasha-astro.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup
@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


# Root Route
@app.get("/")
def root():
    return {
        "message": "Dasha Astro Backend Running",
        "docs": "/docs",
    }


# Health Check
@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "llm_provider": "openai",
        "model": OPENAI_MODEL,
    }


# Location Search
@app.get(
    "/api/location/search",
    response_model=LocationSearchResponse,
)
def search_location(
    query: str = Query(..., min_length=2, max_length=120),
) -> LocationSearchResponse:
    try:
        city = geocode_city(
            query,
            user_agent=NOMINATIM_USER_AGENT,
        )

    except CityLookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return LocationSearchResponse(
        query=city.query,
        display_name=city.display_name,
        latitude=city.latitude,
        longitude=city.longitude,
        timezone=city.timezone,
    )


# Generate Chart
@app.post(
    "/api/chart",
    response_model=ChartResponse,
)
def create_chart(
    payload: ChartRequest,
    db: Session = Depends(get_db),
) -> ChartResponse:
    chart = _calculate_or_422(payload)

    _save_chart(
        db,
        payload,
        chart,
    )

    return ChartResponse(chart=chart)


# Streaming Endpoint
@app.post("/api/chart/stream")
def create_chart_and_stream(
    payload: ChartRequest,
    db: Session = Depends(get_db),
) -> StreamingResponse:

    if payload.user_email:
        twenty_four_hours_ago = datetime.utcnow() - timedelta(days=1)
        usage_count = db.scalar(
            select(func.count(ChatLog.id)).where(
                ChatLog.user_email == payload.user_email,
                ChatLog.created_at >= twenty_four_hours_ago
            )
        )
        if usage_count is not None and usage_count >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="You have reached your daily limit of 5 free readings. Please try again tomorrow.",
            )

    chart = _calculate_or_422(payload)

    _save_chart(
        db,
        payload,
        chart,
    )


    # Fetch chat history for context
    history = []
    if payload.user_email:
        past_logs = db.scalars(
            select(ChatLog).where(
                ChatLog.user_email == payload.user_email
            ).order_by(ChatLog.created_at.desc()).limit(3)
        ).all()
        history = list(reversed(past_logs))

    prompt = build_user_prompt(
        chart,
        payload.question,
        payload.user_name,
    )

    return StreamingResponse(
        _openai_stream_and_log(
            payload,
            chart,
            prompt,
            history,
        ),
        media_type="text/plain; charset=utf-8",
    )


# Admin Logs
@app.get(
    "/admin/logs",
    response_model=list[ChatLogOut],
)
def list_logs(
    x_user_email: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> list[ChatLog]:
    _require_admin(x_user_email)

    return list(
        db.scalars(
            select(ChatLog).order_by(
                ChatLog.created_at.desc()
            )
        ).all()
    )


# Clear Logs
@app.delete(
    "/admin/logs",
    response_model=ClearLogsResponse,
)
def clear_logs(
    x_user_email: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> ClearLogsResponse:
    _require_admin(x_user_email)

    result = db.execute(delete(ChatLog))

    db.commit()

    return ClearLogsResponse(
        deleted=result.rowcount or 0,
    )


# Helpers
def _calculate_or_422(
    payload: ChartRequest,
) -> dict:
    try:
        if (
            payload.latitude is not None
            and payload.longitude is not None
            and payload.timezone
        ):
            city = GeocodedCity(
                query=payload.city_name,
                display_name=payload.city_name,
                latitude=payload.latitude,
                longitude=payload.longitude,
                timezone=payload.timezone,
            )

            return calculate_vedic_chart_from_city(
                payload,
                city,
            )

        return calculate_vedic_chart(
            birth_date=payload.date_of_birth,
            birth_time=payload.time_of_birth,
            city_name=payload.city_name,
            user_agent=NOMINATIM_USER_AGENT,
        )

    except (
        CityLookupError,
        AstrologyCalculationError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


def calculate_vedic_chart_from_city(
    payload: ChartRequest,
    city: GeocodedCity,
) -> dict:
    from app.engine import build_chart_from_coordinates

    return build_chart_from_coordinates(
        birth_date=payload.date_of_birth,
        birth_time=payload.time_of_birth,
        city=city,
    )


def _save_chart(
    db: Session,
    payload: ChartRequest,
    chart: dict,
) -> None:
    birth = chart["birth"]

    saved = SavedChart(
        user_email=str(payload.user_email)
        if payload.user_email
        else None,
        user_name=payload.user_name,
        city_name=payload.city_name,
        latitude=birth["latitude"],
        longitude=birth["longitude"],
        timezone=birth["timezone"],
        birth_date=payload.date_of_birth,
        birth_time=payload.time_of_birth.strftime(
            "%H:%M:%S"
        ),
        chart_json=chart,
    )

    db.add(saved)

    db.commit()


def _openai_stream_and_log(
    payload: ChartRequest,
    chart: dict,
    prompt: str,
    history: list[ChatLog] = None,
) -> Iterator[str]:
    response_text: list[str] = []

    error_text: str | None = None

    try:
        if not OPENAI_API_KEY:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured."
            )

        client = OpenAI(
            api_key=OPENAI_API_KEY,
        )

        messages = [
            {
                "role": "system",
                "content": VEDIC_ASTROLOGY_SYSTEM_PROMPT,
            }
        ]

        if history:
            for log in history:
                messages.append({"role": "user", "content": log.prompt_text})
                messages.append({"role": "assistant", "content": log.ai_response})

        messages.append({"role": "user", "content": prompt})

        stream = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.35,
            stream=True,
        )

        for chunk in stream:
            token = (
                chunk.choices[0]
                .delta
                .content
            )

            if token:
                response_text.append(token)
                yield token

    except Exception as exc:
        error_text = (
            f"OpenAI request failed: {exc}"
        )

        yield error_text

    finally:
        full_response = (
            "".join(response_text)
            if response_text
            else error_text or ""
        )

        with SessionLocal() as db:
            db.add(
                ChatLog(
                    user_email=str(payload.user_email)
                    if payload.user_email
                    else None,
                    user_name=payload.user_name,
                    city_name=payload.city_name,
                    prompt_text=prompt,
                    chart_json=chart,
                    ai_response=full_response,
                    model=OPENAI_MODEL,
                )
            )

            db.commit()


def _require_admin(
    user_email: str | None,
) -> None:
    if (
        not user_email
        or user_email.lower()
        != ADMIN_EMAIL
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )