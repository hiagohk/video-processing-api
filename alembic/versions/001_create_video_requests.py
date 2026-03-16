
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'video_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('video_url', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('idempotency_key', sa.String(), unique=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
        )
    )

def downgrade():
    op.drop_table('video_requests')
