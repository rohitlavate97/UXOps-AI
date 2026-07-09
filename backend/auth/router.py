import uuid
from typing import List

from auth.dependencies import WorkspaceAccess, get_current_active_user
from auth.models import User, WorkspaceMember
from auth.schemas import (Token, UserCreate, UserResponse, WorkspaceCreate,
                          WorkspaceMemberCreate, WorkspaceMemberResponse,
                          WorkspaceResponse)
from auth.security import create_access_token
from auth.service import AuthService
from database.session import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["authentication"])
workspace_router = APIRouter(prefix="/workspaces", tags=["workspaces"])


# --- Authentication Endpoints ---


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user account."""
    existing_user = await AuthService.get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )
    user = await AuthService.create_user(db, obj_in=user_in)
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user and return a JWT access token."""
    user = await AuthService.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is deactivated.",
        )
    return {
        "access_token": create_access_token(subject=user.id),
        "token_type": "bearer",
    }


# --- Workspace Endpoints ---


@workspace_router.post(
    "", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED
)
async def create_workspace(
    workspace_in: WorkspaceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new workspace, naming the creator as the Owner."""
    existing_slug = await AuthService.get_workspace_by_slug(db, slug=workspace_in.slug)
    if existing_slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A workspace with this slug already exists.",
        )
    workspace = await AuthService.create_workspace(
        db, obj_in=workspace_in, creator_id=current_user.id
    )
    return workspace


@workspace_router.get("", response_model=List[WorkspaceResponse])
async def list_workspaces(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all active workspaces that the current user belongs to."""
    workspaces = await AuthService.get_user_workspaces(db, user_id=current_user.id)
    return workspaces


@workspace_router.post(
    "/{workspace_id}/members",
    response_model=WorkspaceMemberResponse,
    dependencies=[Depends(WorkspaceAccess(["owner", "admin"]))],
)
async def add_member(
    workspace_id: uuid.UUID,
    member_in: WorkspaceMemberCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a new member to the workspace. Requires Owner or Admin role."""
    target_user = await AuthService.get_user_by_email(db, email=member_in.email)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found with this email.",
        )

    # Check if user is already a member
    existing_member = await AuthService.get_workspace_member(
        db, workspace_id=workspace_id, user_id=target_user.id
    )
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this workspace.",
        )

    member = await AuthService.add_workspace_member(
        db, workspace_id=workspace_id, user_id=target_user.id, role=member_in.role
    )
    return member


@workspace_router.get(
    "/{workspace_id}/members",
    response_model=List[WorkspaceMemberResponse],
    dependencies=[Depends(WorkspaceAccess(["owner", "admin", "member", "viewer"]))],
)
async def list_members(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """List all members of a workspace."""
    members = await AuthService.get_workspace_members(db, workspace_id=workspace_id)
    return members
