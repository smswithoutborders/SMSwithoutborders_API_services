"""
This program is free software: you can redistribute it under the terms
of the GNU General Public License, v. 3.0. If a copy of the GNU General
Public License was not distributed with this file, see <https://www.gnu.org/licenses/>.
"""

from collections import defaultdict
from peewee import fn
from src.db_models import Entity, Signups
from src.utils import decrypt_and_decode


def get_signup_users(filters=None, group_by=None, options=None):
    """Retrieve signup user data based on specified filters and grouping.

    Args:
        filters (dict, optional): A dictionary containing filtering options:
            - start_date (str): Start date for filtering records (YYYY-MM-DD).
            - end_date (str): End date for filtering records (YYYY-MM-DD).
            - country_code (str): Country code to filter results by.
        group_by (str, optional): Determines how the data is grouped:
            - "country": Group results by country.
            - "date": Group results by date.
            - None: No grouping, returns total signup users.
        options (dict, optional): A dictionary containing additional options:
            - granularity (str): Granularity of date grouping ("day" or "month").
            - top (int): Number of top results to return.
            - page (int): Current page for paginated results.
            - page_size (int): Number of records per page.
            - batch_size (int): Batch size for decrypting filtered rows.

    Returns:
        dict: A dictionary containing the results and optional pagination:
            - data (list): The retrieved data, structure depends on `group_by`.
                - If `group_by="country"`, list of dicts with country and user counts.
                - If `group_by="date"`, list of dicts with date and user counts.
                - If `group_by=None`, list with total user count.
            - pagination (dict): Pagination details (if applicable):
                - total_records (int): Total number of matching records.
                - page (int): Current page (omitted if `group_by` is None).
                - page_size (int): Records per page (omitted if `group_by` is None).
                - total_pages (int): Total pages (omitted if `group_by` is None).
            - total_signup_users (int): Total number of signup users across all records.
    """
    filters = filters or {}
    options = options or {}

    start_date = filters.get("start_date")
    end_date = filters.get("end_date")
    country_code = filters.get("country_code")

    granularity = options.get("granularity", "day")
    top = options.get("top")
    page = options.get("page", 1)
    page_size = options.get("page_size", 50)

    if group_by not in {None, "country", "date"}:
        raise ValueError("Invalid group_by value. Use 'country', 'date', or None.")

    if group_by == "date" and granularity not in {"day", "month"}:
        raise ValueError("Invalid granularity. Use 'day' or 'month'.")

    if top is not None:
        if not isinstance(top, int) or top <= 0:
            raise ValueError("'top' must be a positive integer.")
        if page is not None or page_size is not None:
            raise ValueError("'top' cannot be used with 'page' or 'page_size'.")

    if page is not None:
        if not isinstance(page, int) or page <= 0:
            raise ValueError("'page' must be a positive integer.")

    if page_size is not None:
        if not isinstance(page_size, int) or page_size <= 0:
            raise ValueError("'page_size' must be a positive integer.")

    if group_by is None and (
        top is not None or page is not None or page_size is not None
    ):
        raise ValueError(
            "Pagination ('top', 'page', 'page_size') is not allowed when group_by is None."
        )

    query = Signups.select()
    if start_date:
        query = query.where(Signups.date_created >= start_date)
    if end_date:
        query = query.where(Signups.date_created <= end_date)

    if country_code:
        query = query.where(Signups.country_code == country_code)

    total_signup_users = query.select(fn.COUNT(Signups.id)).scalar()

    if group_by == "country":
        query = (
            query.select(
                Signups.country_code, fn.COUNT(Signups.id).alias("signup_users")
            )
            .group_by(Signups.country_code)
            .order_by(fn.COUNT(Signups.id).desc())
        )
    elif group_by == "date":
        timeframe = Signups.date_created.truncate(granularity).alias("timeframe")
        query = (
            query.select(timeframe, fn.COUNT(Signups.id).alias("signup_users"))
            .group_by(timeframe)
            .order_by(timeframe.desc())
        )

    total_records = query.count()

    if top:
        query = query.limit(top)
    elif group_by is not None:
        offset = (page - 1) * page_size
        query = query.limit(page_size).offset(offset)

    result = [
        (
            {
                "country_code": row.country_code,
                "signup_users": row.signup_users,
            }
            if group_by == "country"
            else {
                "timeframe": str(row.timeframe.date()),
                "signup_users": row.signup_users,
            }
        )
        for row in query
    ]

    pagination = (
        {
            "page": page,
            "page_size": page_size,
            "total_pages": (total_records + page_size - 1) // page_size,
            "total_records": total_records,
        }
        if group_by is not None
        else {}
    )

    return {
        "data": result,
        "pagination": pagination,
        "total_signup_users": total_signup_users,
    }


def get_retained_users(filters=None, group_by=None, options=None):
    """Retrieve retained user data based on specified filters and grouping.

     Args:
        filters (dict, optional): A dictionary containing filtering options:
            - start_date (str): Start date for filtering records (YYYY-MM-DD).
            - end_date (str): End date for filtering records (YYYY-MM-DD).
            - country_code (str): Country code to filter results by.
        group_by (str, optional): Determines how the data is grouped:
            - "country": Group results by country.
            - "date": Group results by date.
            - None: No grouping, returns total retained users.
        options (dict, optional): A dictionary containing additional options:
            - granularity (str): Granularity of date grouping ("day" or "month").
            - top (int): Number of top results to return.
            - page (int): Current page for paginated results.
            - page_size (int): Number of records per page.
            - batch_size (int): Batch size for decrypting filtered rows.

    Returns:
        dict: A dictionary containing the results and optional pagination:
            - data (list): The retrieved data, structure depends on `group_by`.
                - If `group_by="country"`, list of dicts with country and user counts.
                - If `group_by="date"`, list of dicts with date and user counts.
                - If `group_by=None`, list with total user count.
            - pagination (dict): Pagination details (if applicable):
                - total_records (int): Total number of matching records.
                - page (int): Current page (omitted if `group_by` is None).
                - page_size (int): Records per page (omitted if `group_by` is None).
                - total_pages (int): Total pages (omitted if `group_by` is None).
            - total_retained_users (int): Total number of retained users across all records.
    """
    filters = filters or {}
    options = options or {}

    start_date = filters.get("start_date")
    end_date = filters.get("end_date")
    country_code = filters.get("country_code")

    granularity = options.get("granularity", "day")
    top = options.get("top")
    page = options.get("page", 1)
    page_size = options.get("page_size", 50)
    batch_size = options.get("batch_size", 1000)

    if group_by not in {None, "country", "date"}:
        raise ValueError("Invalid group_by value. Use 'country', 'date', or None.")

    if group_by == "date" and granularity not in {"day", "month"}:
        raise ValueError("Invalid granularity. Use 'day' or 'month'.")

    if top is not None:
        if not isinstance(top, int) or top <= 0:
            raise ValueError("'top' must be a positive integer.")
        if page is not None or page_size is not None:
            raise ValueError("'top' cannot be used with 'page' or 'page_size'.")

    if page is not None:
        if not isinstance(page, int) or page <= 0:
            raise ValueError("'page' must be a positive integer.")

    if page_size is not None:
        if not isinstance(page_size, int) or page_size <= 0:
            raise ValueError("'page_size' must be a positive integer.")

    if group_by is None and (
        top is not None or page is not None or page_size is not None
    ):
        raise ValueError(
            "Pagination ('top', 'page', 'page_size') is not allowed when group_by is None."
        )

    query = Entity.select()
    if start_date:
        query = query.where(Entity.date_created >= start_date)
    if end_date:
        query = query.where(Entity.date_created <= end_date)

    def decrypt_filter_rows(query, country_code, batch_size):
        decrypted_rows = []
        batch_number = 1
        while True:
            batch_query = query.paginate(batch_number, batch_size)
            batch_results = list(batch_query)
            if not batch_results:
                break
            decrypted_rows.extend(
                row
                for row in batch_results
                if decrypt_and_decode(row.country_code) == country_code
            )
            batch_number += 1
        return decrypted_rows

    if country_code:
        filtered_rows = decrypt_filter_rows(query, country_code, batch_size)
        query = Entity.select().where(Entity.eid << [row.eid for row in filtered_rows])

    total_retained_users = query.select(fn.COUNT(Entity.eid)).scalar()

    result = []
    total_records = 0

    if group_by == "country":
        country_aggregates = defaultdict(int)
        for row in query:
            decrypted_country = decrypt_and_decode(row.country_code)
            country_aggregates[decrypted_country] += 1

        result = sorted(
            [
                {"country_code": k, "retained_users": v}
                for k, v in country_aggregates.items()
            ],
            key=lambda x: x["retained_users"],
            reverse=True,
        )
        total_records = len(result)
        if top:
            result = result[:top]
        else:
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            result = result[start_idx:end_idx]

    elif group_by == "date":
        timeframe = Entity.date_created.truncate(granularity).alias("timeframe")
        query = (
            query.select(timeframe, fn.COUNT(Entity.eid).alias("retained_users"))
            .group_by(timeframe)
            .order_by(timeframe.desc())
        )

        total_records = query.count()
        query = query.limit(top) if top else query.paginate(page, page_size)
        result = [
            {
                "timeframe": str(row.timeframe.date()),
                "retained_users": row.retained_users,
            }
            for row in query
        ]

    elif group_by is None:
        result = []

    else:
        raise ValueError(
            "Invalid group_by value. Use 'country', 'date', or leave empty."
        )

    pagination = (
        {
            "page": page,
            "page_size": page_size,
            "total_pages": (total_records + page_size - 1) // page_size,
            "total_records": total_records,
        }
        if group_by is not None and not top
        else {}
    )

    return {
        "data": result,
        "pagination": pagination,
        "total_retained_users": total_retained_users,
    }
