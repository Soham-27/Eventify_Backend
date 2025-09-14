"""update_booking_status_constraint

Revision ID: 57cfe8c03bbc
Revises: bfe2d12829e2
Create Date: 2025-09-14 00:29:23.997068

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '57cfe8c03bbc'
down_revision: Union[str, Sequence[str], None] = 'bfe2d12829e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the existing constraint
    op.drop_constraint('check_booking_status', 'bookings', type_='check')
    
    # Create the new constraint with PENDING status
    op.create_check_constraint(
        'check_booking_status',
        'bookings',
        "status IN ('PENDING', 'CONFIRMED', 'CANCELLED')"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the new constraint
    op.drop_constraint('check_booking_status', 'bookings', type_='check')
    
    # Restore the old constraint
    op.create_check_constraint(
        'check_booking_status',
        'bookings',
        "status IN ('CONFIRMED', 'CANCELLED')"
    )
