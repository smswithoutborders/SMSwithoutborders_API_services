"""
This program is free software: you can redistribute it under the terms
of the GNU General Public License, v. 3.0. If a copy of the GNU General
Public License was not distributed with this file, see <https://www.gnu.org/licenses/>.
"""

from src.db_models import Signups
from base_logger import get_logger

logger = get_logger(__name__)
database = Signups._meta.database


def create_record(country_code, source):
    """
    Create a signup record.

    Args:
        country_code (str): The country code of the signup.
        source (str): The source of the signup (e.g., "bridges" or "platforms").
    """
    with database.atomic():
        signup = Signups.create(
            country_code=country_code,
            source=source,
        )

    logger.info("Signup record created successfully")
    return signup
