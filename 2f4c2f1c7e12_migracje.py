"""migracje

Revision ID: 2f4c2f1c7e12
Revises: 
Create Date: 2023-08-23 17:17:12.495826

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f4c2f1c7e12'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = ('default',)
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
