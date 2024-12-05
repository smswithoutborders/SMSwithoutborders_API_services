"""
This program is free software: you can redistribute it under the terms
of the GNU General Public License, v. 3.0. If a copy of the GNU General
Public License was not distributed with this file, see <https://www.gnu.org/licenses/>.
"""

from datetime import datetime
from peewee import fn
from src.db_models import Entity, Signups
from src.utils import decrypt_and_decode

MAX_PAGE_SIZE = 100
MIN_PAGE_SIZE = 10


def validate_date_format(date_str: str) -> datetime:
    """Validate the date format and return a datetime object."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(
            f"Date '{date_str}' is not in the correct format. Expected 'YYYY-MM-DD'."
        ) from exc


def fetch_signup_records(
    page: int = 1, page_size: int = 10, start_date: str = None, end_date: str = None
):
    """Fetch the number of users who signed up."""

    if page < 1:
        raise ValueError("Page must be a positive integer.")
    if not MIN_PAGE_SIZE <= page_size <= MAX_PAGE_SIZE:
        raise ValueError(
            f"Page size must be between {MIN_PAGE_SIZE} and {MAX_PAGE_SIZE}."
        )

    if not start_date or not end_date:
        raise ValueError("start_date and end_date must be provided.")

    start_date = validate_date_format(start_date)
    end_date = validate_date_format(end_date)

    if start_date > end_date:
        raise ValueError("start_date must be earlier than or equal to end_date.")

    signups_query = (
        Signups.select(
            fn.DATE(Signups.date_created).alias("date"),
            Signups.country_code,
            fn.COUNT(Signups.id).alias("signup_count"),
            fn.SUM(fn.COUNT(Signups.id)).over().alias("total_signup_count"),
        )
        .where(Signups.date_created.between(start_date, end_date))
        .group_by(fn.DATE(Signups.date_created), Signups.country_code)
        .order_by(Signups.date_created.desc())
        .paginate(page, page_size)
    )

    signup_data = {}
    total_signup_count = 0
    unique_countries = set()

    for record in signups_query:
        date = str(record.date)
        country = record.country_code
        signup_count = int(record.signup_count)

        unique_countries.add(country)

        if date not in signup_data:
            signup_data[date] = {}

        if country not in signup_data[date]:
            signup_data[date][country] = {"signup_count": 0}

        signup_data[date][country]["signup_count"] += signup_count
        total_signup_count = int(record.total_signup_count)

    return {
        "total_signup_count": total_signup_count,
        "total_country_count": len(unique_countries),
        "data": signup_data,
    }


def fetch_retained_user_records(
    page: int = 1, page_size: int = 10, start_date: str = None, end_date: str = None
):
    """Fetch the number of retained (active) users."""

    if page < 1:
        raise ValueError("Page must be a positive integer.")
    if not MIN_PAGE_SIZE <= page_size <= MAX_PAGE_SIZE:
        raise ValueError(
            f"Page size must be between {MIN_PAGE_SIZE} and {MAX_PAGE_SIZE}."
        )

    if not start_date or not end_date:
        raise ValueError("start_date and end_date must be provided.")

    start_date = validate_date_format(start_date)
    end_date = validate_date_format(end_date)

    if start_date > end_date:
        raise ValueError("start_date must be earlier than or equal to end_date.")

    entities_query = (
        Entity.select(
            fn.DATE(Entity.date_created).alias("date"),
            Entity.country_code,
            fn.COUNT(Entity.eid).alias("retained_user_count"),
            fn.SUM(Entity.is_bridge_enabled.cast("integer")).alias(
                "retained_user_count"
            ),
            fn.SUM(Entity.is_bridge_enabled.cast("integer"))
            .over()
            .alias("total_retained_user_count"),
        )
        .where(Entity.date_created.between(start_date, end_date))
        .group_by(fn.DATE(Entity.date_created), Entity.country_code)
        .order_by(Entity.date_created.desc())
        .paginate(page, page_size)
    )

    retained_user_data = {}
    total_retained_user_count = 0
    unique_countries = set()

    for record in entities_query:
        date = str(record.date)
        country = decrypt_and_decode(record.country_code)
        retained_user_count = int(record.retained_user_count)

        unique_countries.add(country)

        if date not in retained_user_data:
            retained_user_data[date] = {}

        if country not in retained_user_data[date]:
            retained_user_data[date][country] = {"retained_user_count": 0}

        retained_user_data[date][country]["retained_user_count"] += retained_user_count
        total_retained_user_count = int(record.total_retained_user_count)

    return {
        "total_retained_user_count": total_retained_user_count,
        "total_country_count": len(unique_countries),
        "data": retained_user_data,
    }
