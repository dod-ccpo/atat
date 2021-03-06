"""state machine states extended

Revision ID: 26319c44a8d5
Revises: 59973fa17ded
Create Date: 2020-01-22 15:54:03.186751

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "26319c44a8d5"  # pragma: allowlist secret
down_revision = "59973fa17ded"  # pragma: allowlist secret
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "portfolio_state_machines",
        "state",
        existing_type=sa.Enum(
            "UNSTARTED",
            "STARTING",
            "STARTED",
            "COMPLETED",
            "FAILED",
            "TENANT_CREATED",
            "TENANT_IN_PROGRESS",
            "TENANT_FAILED",
            "BILLING_PROFILE_CREATED",
            "BILLING_PROFILE_IN_PROGRESS",
            "BILLING_PROFILE_FAILED",
            "ADMIN_SUBSCRIPTION_CREATED",
            "ADMIN_SUBSCRIPTION_IN_PROGRESS",
            "ADMIN_SUBSCRIPTION_FAILED",
            name="fsmstates",
            native_enum=False,
        ),
        type_=sa.Enum(
            "UNSTARTED",
            "STARTING",
            "STARTED",
            "COMPLETED",
            "FAILED",
            "TENANT_CREATED",
            "TENANT_IN_PROGRESS",
            "TENANT_FAILED",
            "BILLING_PROFILE_CREATION_CREATED",
            "BILLING_PROFILE_CREATION_IN_PROGRESS",
            "BILLING_PROFILE_CREATION_FAILED",
            "BILLING_PROFILE_VERIFICATION_CREATED",
            "BILLING_PROFILE_VERIFICATION_IN_PROGRESS",
            "BILLING_PROFILE_VERIFICATION_FAILED",
            "BILLING_PROFILE_TENANT_ACCESS_CREATED",
            "BILLING_PROFILE_TENANT_ACCESS_IN_PROGRESS",
            "BILLING_PROFILE_TENANT_ACCESS_FAILED",
            "TASK_ORDER_BILLING_CREATION_CREATED",
            "TASK_ORDER_BILLING_CREATION_IN_PROGRESS",
            "TASK_ORDER_BILLING_CREATION_FAILED",
            "TASK_ORDER_BILLING_VERIFICATION_CREATED",
            "TASK_ORDER_BILLING_VERIFICATION_IN_PROGRESS",
            "TASK_ORDER_BILLING_VERIFICATION_FAILED",
            "BILLING_INSTRUCTION_CREATED",
            "BILLING_INSTRUCTION_IN_PROGRESS",
            "BILLING_INSTRUCTION_FAILED",
            name="fsmstates",
            native_enum=False,
            create_constraint=False,
        ),
        existing_nullable=False,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "portfolio_state_machines",
        "state",
        existing_type=sa.Enum(
            "UNSTARTED",
            "STARTING",
            "STARTED",
            "COMPLETED",
            "FAILED",
            "TENANT_CREATED",
            "TENANT_IN_PROGRESS",
            "TENANT_FAILED",
            "BILLING_PROFILE_CREATION_CREATED",
            "BILLING_PROFILE_CREATION_IN_PROGRESS",
            "BILLING_PROFILE_CREATION_FAILED",
            "BILLING_PROFILE_VERIFICATION_CREATED",
            "BILLING_PROFILE_VERIFICATION_IN_PROGRESS",
            "BILLING_PROFILE_VERIFICATION_FAILED",
            "BILLING_PROFILE_TENANT_ACCESS_CREATED",
            "BILLING_PROFILE_TENANT_ACCESS_IN_PROGRESS",
            "BILLING_PROFILE_TENANT_ACCESS_FAILED",
            "TASK_ORDER_BILLING_CREATION_CREATED",
            "TASK_ORDER_BILLING_CREATION_IN_PROGRESS",
            "TASK_ORDER_BILLING_CREATION_FAILED",
            "TASK_ORDER_BILLING_VERIFICATION_CREATED",
            "TASK_ORDER_BILLING_VERIFICATION_IN_PROGRESS",
            "TASK_ORDER_BILLING_VERIFICATION_FAILED",
            "BILLING_INSTRUCTION_CREATED",
            "BILLING_INSTRUCTION_IN_PROGRESS",
            "BILLING_INSTRUCTION_FAILED",
            name="fsmstates",
            native_enum=False,
        ),
        type_=sa.Enum(
            "UNSTARTED",
            "STARTING",
            "STARTED",
            "COMPLETED",
            "FAILED",
            "TENANT_CREATED",
            "TENANT_IN_PROGRESS",
            "TENANT_FAILED",
            "BILLING_PROFILE_CREATED",
            "BILLING_PROFILE_IN_PROGRESS",
            "BILLING_PROFILE_FAILED",
            "ADMIN_SUBSCRIPTION_CREATED",
            "ADMIN_SUBSCRIPTION_IN_PROGRESS",
            "ADMIN_SUBSCRIPTION_FAILED",
            name="fsmstates",
            native_enum=False,
        ),
        existing_nullable=False,
    )
    # ### end Alembic commands ###
