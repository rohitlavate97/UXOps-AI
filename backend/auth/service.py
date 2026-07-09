import uuid
from typing import List, Optional

from auth.models import User, Workspace, WorkspaceMember
from auth.schemas import UserCreate, WorkspaceCreate, WorkspaceMemberCreate
from auth.security import get_password_hash, verify_password
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class AuthService:
    # --- User Operations ---
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def create_user(db: AsyncSession, obj_in: UserCreate) -> User:
        db_user = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_active=True,
            is_superuser=False,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def authenticate_user(
        db: AsyncSession, email: str, password: str
    ) -> Optional[User]:
        user = await AuthService.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    # --- Workspace Operations ---
    @staticmethod
    async def get_workspace_by_slug(db: AsyncSession, slug: str) -> Optional[Workspace]:
        stmt = select(Workspace).where(Workspace.slug == slug)
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_workspace_by_id(
        db: AsyncSession, workspace_id: uuid.UUID
    ) -> Optional[Workspace]:
        stmt = select(Workspace).where(Workspace.id == workspace_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def create_workspace(
        db: AsyncSession, obj_in: WorkspaceCreate, creator_id: uuid.UUID
    ) -> Workspace:
        db_workspace = Workspace(
            name=obj_in.name,
            slug=obj_in.slug,
            is_active=True,
        )
        db.add(db_workspace)
        await db.flush()  # Populates db_workspace.id

        # Add creator as owner member
        db_member = WorkspaceMember(
            workspace_id=db_workspace.id,
            user_id=creator_id,
            role="owner",
        )
        db.add(db_member)
        await db.commit()
        await db.refresh(db_workspace)
        return db_workspace

    # --- Membership Operations ---
    @staticmethod
    async def add_workspace_member(
        db: AsyncSession,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str = "member",
    ) -> WorkspaceMember:
        db_member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=user_id,
            role=role,
        )
        db.add(db_member)
        await db.commit()

        # Load user relationship to prevent lazy loading issues in serialization
        stmt = (
            select(WorkspaceMember)
            .where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
            .options(selectinload(WorkspaceMember.user))
        )
        result = await db.execute(stmt)
        return result.scalars().one()

    @staticmethod
    async def get_workspace_member(
        db: AsyncSession, workspace_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[WorkspaceMember]:
        stmt = select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_user_workspaces(
        db: AsyncSession, user_id: uuid.UUID
    ) -> List[Workspace]:
        stmt = (
            select(Workspace)
            .join(WorkspaceMember)
            .where(WorkspaceMember.user_id == user_id, Workspace.is_active)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_workspace_members(
        db: AsyncSession, workspace_id: uuid.UUID
    ) -> List[WorkspaceMember]:
        stmt = (
            select(WorkspaceMember)
            .where(WorkspaceMember.workspace_id == workspace_id)
            .options(selectinload(WorkspaceMember.user))
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())
