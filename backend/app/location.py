from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import OpenCage
from sqlalchemy.orm import Session
from sqlalchemy import select
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


def geocode_city(city_name: str, api_key: str, db: Session, geocoder: Any | None = None, country_codes: str | None = None) -> GeocodedCity:
    query = city_name.strip()
    if len(query) < 2:
        raise CityLookupError("Enter a valid city name.")

    normalized_query = query.lower()
    normalized_country = country_codes.lower() if country_codes else None

    # Check cache first
    cached = db.scalar(
        select(CachedLocation)
        .where(
            CachedLocation.query == normalized_query,
            CachedLocation.country == normalized_country
        )
    )
    if cached:
        return GeocodedCity(
            query=query,
            display_name=cached.display_name,
            latitude=cached.latitude,
            longitude=cached.longitude,
            timezone=cached.timezone,
        )

    if geocoder:
        locator = geocoder
        kwargs = {"exactly_one": True}
        if country_codes:
            # Assume geocoder accepts 'country' (like OpenCage) or 'country_codes'
            if hasattr(locator, "geocode") and hasattr(locator.geocode, "__func__") and "country_codes" in locator.geocode.__func__.__code__.co_varnames:
                kwargs["country_codes"] = country_codes
            else:
                kwargs["country"] = country_codes
    elif api_key:
        locator = OpenCage(api_key=api_key, timeout=10)
        kwargs = {"exactly_one": True}
        if country_codes:
            kwargs["country"] = country_codes
    else:
        # Fallback to Nominatim if no API key is provided
        from geopy.geocoders import Nominatim
        locator = Nominatim(user_agent="dasha-astro-geocoder", timeout=10)
        kwargs = {"exactly_one": True, "addressdetails": True}
        if country_codes:
            kwargs["country_codes"] = country_codes

    try:
        location = locator.geocode(query, **kwargs)
    except (GeocoderTimedOut, GeocoderServiceError) as exc:
        raise CityLookupError(f"Could not geocode '{query}'. Try again in a moment.") from exc

    if location is None:
        raise CityLookupError(f"Could not find coordinates for '{query}'.")

    latitude = float(location.latitude)
    longitude = float(location.longitude)
    timezone_name = resolve_timezone(latitude, longitude)

    display_name = getattr(location, "address", query)

    # Check if a race condition happened and it already exists
    existing_cached = db.scalar(
        select(CachedLocation)
        .where(
            CachedLocation.query == normalized_query,
            CachedLocation.country == normalized_country
        )
    )
    if not existing_cached:
        # Save to cache
        new_cached_location = CachedLocation(
            query=normalized_query,
            country=normalized_country,
            display_name=display_name,
            latitude=latitude,
            longitude=longitude,
            timezone=timezone_name
        )
        db.add(new_cached_location)
        # Rely on the session's flush/commit higher up the stack.
        # Note: If this fails during a flush later due to a unique constraint
        # that wasn't caught by the select above, the caller's transaction
        # will handle it.

    return GeocodedCity(
        query=query,
        display_name=display_name,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone_name,
    )


def resolve_timezone(latitude: float, longitude: float) -> str:
    return (
        _TIMEZONE_FINDER.timezone_at(lat=latitude, lng=longitude)
        or _TIMEZONE_FINDER.closest_timezone_at(lat=latitude, lng=longitude)
        or "UTC"
    )
