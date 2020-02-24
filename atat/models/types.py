import sqlalchemy
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID


def Id():
    return Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sqlalchemy.text("uuid_generate_v4()"),
    )
