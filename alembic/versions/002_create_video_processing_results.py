
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "video_processing_results",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "video_request_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("video_requests.id"),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "duration_seconds",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "processed_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade():
    op.drop_table("video_processing_results")