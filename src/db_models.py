"""Peewee Database ORM Models."""

import datetime
from peewee import (
    Model,
    CharField,
    TextField,
    DateTimeField,
    IntegerField,
    UUIDField,
    ForeignKeyField,
    BlobField,
    BooleanField,
)
from src.db import connect
from src.utils import create_tables
from settings import Configurations

database = connect()


class Entity(Model):
    """Model representing Entities Table."""

    eid = UUIDField(primary_key=True)
    phone_number_hash = CharField()
    password_hash = CharField(null=True)
    country_code = CharField()
    device_id = CharField(null=True)
    client_publish_pub_key = TextField(null=True)
    client_device_id_pub_key = TextField(null=True)
    publish_keypair = BlobField(null=True)
    device_id_keypair = BlobField(null=True)
    server_state = BlobField(null=True)
    is_bridge_enabled = BooleanField(default=True)
    date_created = DateTimeField(default=datetime.datetime.now)

    class Meta:
        """Meta class to define database connection."""

        database = database
        table_name = "entities"
        indexes = (
            (("phone_number_hash",), True),
            (("device_id",), True),
        )


class OTPRateLimit(Model):
    """Model representing OTP Rate Limits Table."""

    phone_number = CharField()
    attempt_count = IntegerField(default=0)
    date_expires = DateTimeField(null=True)
    date_created = DateTimeField(default=datetime.datetime.now)

    class Meta:
        """Meta class to define database connection."""

        database = database
        table_name = "otp_rate_limit"
        indexes = ((("phone_number",), True),)


class Token(Model):
    """Model representing Tokens Table."""

    eid = ForeignKeyField(Entity, backref="tokens", column_name="eid")
    platform = CharField()
    account_identifier_hash = CharField()
    account_identifier = CharField()
    account_tokens = TextField()
    date_created = DateTimeField(default=datetime.datetime.now)

    class Meta:
        """Meta class to define database connection."""

        database = database
        table_name = "tokens"
        indexes = ((("platform", "account_identifier_hash", "eid"), True),)


class PasswordRateLimit(Model):
    """Model representing Password Rate Limits Table."""

    eid = ForeignKeyField(Entity, backref="password_rate_limit", column_name="eid")
    attempt_count = IntegerField(default=0)
    date_expires = DateTimeField(null=True)
    date_created = DateTimeField(default=datetime.datetime.now)

    class Meta:
        """Meta class to define database connection."""

        database = database
        table_name = "password_rate_limit"


class OTP(Model):
    """Model representing OTP Table."""

    phone_number = CharField()
    otp_code = CharField(max_length=10)
    attempt_count = IntegerField(default=0)
    date_expires = DateTimeField()
    is_verified = BooleanField(default=False)
    date_created = DateTimeField(default=datetime.datetime.now)

    class Meta:
        """Meta class to define database connection."""

        database = database
        table_name = "otp"
        indexes = (
            (("phone_number",), False),
            (("date_expires",), False),
        )

    def is_expired(self):
        """Check if the OTP is expired."""
        return datetime.datetime.now() > self.date_expires

    def reset_attempt_count(self):
        """Reset the attempt count for the OTP."""
        self.attempt_count = 0
        self.save()

    def increment_attempt_count(self):
        """Increment the attempt count for the OTP."""
        self.attempt_count += 1
        self.save()


if Configurations.MODE in ("production", "development"):
    create_tables([Entity, OTPRateLimit, Token, PasswordRateLimit, OTP])
