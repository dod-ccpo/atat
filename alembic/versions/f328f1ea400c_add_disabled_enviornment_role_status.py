"""add disabled enviornment_role status

Revision ID: f328f1ea400c
Revises: e05d1f2682af
Create Date: 2019-10-29 15:16:04.037436

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f328f1ea400c"  # pragma: allowlist secret
down_revision = "e05d1f2682af"  # pragma: allowlist secret
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(
        """
        UPDATE environment_roles
        SET status = (CASE WHEN status = 'PENDING_DELETE' THEN 'COMPLETED' ELSE status END)
        """
    )

    op.alter_column(
        "environment_roles",
        "status",
        type_=sa.Enum(
            "PENDING", "COMPLETED", "DISABLED", name="status", native_enum=False,
        ),
        existing_type=sa.Enum(
            "PENDING", "COMPLETED", "PENDING_DELETE", name="status", native_enum=False
        ),
    )


def downgrade():
    conn = op.get_bind()
    conn.execute(
        """
        UPDATE environment_roles
        SET status = (CASE WHEN status = 'DISABLED' THEN 'PENDING_DELETE' ELSE status END)
        """
    )
    op.alter_column(
        "environment_roles",
        "status",
        type_=sa.Enum(
            "PENDING", "COMPLETED", "PENDING_DELETE", name="status", native_enum=False
        ),
        existing_type=sa.Enum(
            "PENDING", "COMPLETED", "DISABLED", name="status", native_enum=False,
        ),
    )
