from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from geopy.exc import GeocoderServiceError, GeocoderTimedOut, GeocoderAuthenticationFailure
from geopy.geocoders import OpenCage, Nominatim
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from timezonefinder import TimezoneFinder
from .models import CachedLocation


class CityLookupError(ValueError):
    pass


@dataclass(frozen=True)
class GeocodedCity:
    query: str
    display_name: str
    latitude: float
    longitude: float
    timezone: str


_TIMEZONE_FINDER = TimezoneFinder()


def geocode_city(
    city_name: str,
    user_agent: str,
    geocoder: Any | None = None,
    country_codes: str | None = None,
    db: Session | None = None,
) -> GeocodedCity:
    query = city_name.strip()
    if len(query) < 2:
        raise CityLookupError("Enter a valid city name.")

    query_key = query.lower()
    if country_codes:
        query_key = f"{query_key}:{country_codes.lower()}"

    if db is not None:
        cached = db.scalar(select(CachedLocation).where(CachedLocation.query_key == query_key))
        if cached:
            return GeocodedCity(
                query=query,
                display_name=cached.display_name,
                latitude=cached.latitude,
                longitude=cached.longitude,
                timezone=cached.timezone,
            )

    try:
        if not geocoder:
            api_key = os.getenv("OPENCAGE_API_KEY")
            if api_key:
                locator = OpenCage(api_key=api_key, timeout=10)
            else:
                locator = Nominatim(user_agent=user_agent, timeout=10)
        else:
            locator = geocoder

        kwargs = {
            "exactly_one": True,
        }

        if isinstance(locator, Nominatim):
             kwargs["addressdetails"] = True
             if country_codes:
                 kwargs["country_codes"] = country_codes
        else:
             if country_codes:
                 kwargs["countrycode"] = country_codes

        location = locator.geocode(query, **kwargs)
    except (GeocoderTimedOut, GeocoderServiceError, GeocoderAuthenticationFailure) as exc:
        raise CityLookupError(f"Could not geocode '{query}'. Try again in a moment.") from exc

    if location is None:
        raise CityLookupError(f"Could not find coordinates for '{query}'.")

    latitude = float(location.latitude)
    longitude = float(location.longitude)
    timezone_name = resolve_timezone(latitude, longitude)

    geocoded = GeocodedCity(
        query=query,
        display_name=getattr(location, "address", query),
        latitude=latitude,
        longitude=longitude,
        timezone=timezone_name,
    )

    if db is not None:
        new_cache = CachedLocation(
            query_key=query_key,
            display_name=geocoded.display_name,
            latitude=geocoded.latitude,
            longitude=geocoded.longitude,
            timezone=geocoded.timezone,
        )

        try:
            with db.begin_nested():
                db.add(new_cache)
        except IntegrityError:
            pass

    return geocoded


def resolve_timezone(latitude: float, longitude: float) -> str:
    return (
        _TIMEZONE_FINDER.timezone_at(lat=latitude, lng=longitude)
        or _TIMEZONE_FINDER.closest_timezone_at(lat=latitude, lng=longitude)
        or "UTC"
    )
