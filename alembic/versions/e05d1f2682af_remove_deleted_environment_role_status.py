"""remove deleted environment_role status

Revision ID: e05d1f2682af
Revises: 1497926ddec1
Create Date: 2019-10-14 16:03:33.816215

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e05d1f2682af"  # pragma: allowlist secret
down_revision = "1497926ddec1"  # pragma: allowlist secret
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(
        """
        UPDATE environment_roles
        SET status = (CASE WHEN status = 'DELETED' THEN 'PENDING_DELETE' ELSE status END)
        """
    )
    op.alter_column(
        "environment_roles",
        "status",
        type_=sa.Enum(
            "PENDING", "COMPLETED", "PENDING_DELETE", name="status", native_enum=False
        ),
        existing_type=sa.Enum(
            "PENDING",
            "COMPLETED",
            "PENDING_DELETE",
            "DELETED",
            name="status",
            native_enum=False,
        ),
    )


def downgrade():
    op.alter_column(
        "environment_roles",
        "status",
        type_=sa.Enum(
            "PENDING",
            "COMPLETED",
            "PENDING_DELETE",
            "DELETED",
            name="status",
            native_enum=False,
        ),
        existing_type=sa.Enum(
            "PENDING", "COMPLETED", "PENDING_DELETE", name="status", native_enum=False
        ),
    )
