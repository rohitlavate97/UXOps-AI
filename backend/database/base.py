# Import all the models, so that Base has them before being
# imported by Alembic
from auth.models import User, Workspace, WorkspaceMember  # noqa
from database.base_class import Base  # noqa
