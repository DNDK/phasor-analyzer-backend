from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy import inspect
${imports if imports else ""}

def get_columns(table_name):
    inspector = inspect(op.get_bind())
    return [c['name'] for c in inspector.get_columns(table_name)]