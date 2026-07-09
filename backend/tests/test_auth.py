import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient):
    """Test user signup succeeds with valid data."""
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "testuser@example.com",
            "password": "strongpassword123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["full_name"] == "Test User"
    assert "id" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient):
    """Test user signup fails when email is already registered."""
    signup_data = {
        "email": "duplicate@example.com",
        "password": "strongpassword123",
        "full_name": "Duplicate User",
    }
    # First signup
    res1 = await client.post("/api/v1/auth/signup", json=signup_data)
    assert res1.status_code == 201

    # Second signup with same email
    res2 = await client.post("/api/v1/auth/signup", json=signup_data)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test login yields a JWT token when valid credentials are used."""
    # Create user first
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "loginuser@example.com",
            "password": "loginpassword123",
            "full_name": "Login User",
        },
    )

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "loginuser@example.com",
            "password": "loginpassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    """Test login fails when using an incorrect password."""
    # Create user
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "wrongpwd@example.com",
            "password": "correctpassword123",
            "full_name": "Pwd User",
        },
    )

    # Login with wrong password
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "wrongpwd@example.com",
            "password": "wrongpassword123",
        },
    )
    assert response.status_code == 400
    assert "Incorrect email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_workspace(client: AsyncClient):
    """Test creating a workspace registers the workspace and tags the creator as owner."""
    # Create user and login
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "workspaceowner@example.com",
            "password": "strongpassword123",
            "full_name": "Workspace Owner",
        },
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "workspaceowner@example.com",
            "password": "strongpassword123",
        },
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create workspace
    response = await client.post(
        "/api/v1/workspaces",
        json={"name": "Dev Studio", "slug": "dev-studio"},
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Dev Studio"
    assert data["slug"] == "dev-studio"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_workspaces(client: AsyncClient):
    """Test listing workspaces associated with the current user."""
    # Create user and login
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "memberuser@example.com",
            "password": "strongpassword123",
            "full_name": "Member User",
        },
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "memberuser@example.com",
            "password": "strongpassword123",
        },
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create workspace 1
    await client.post(
        "/api/v1/workspaces",
        json={"name": "Workspace A", "slug": "workspace-a"},
        headers=headers,
    )
    # Create workspace 2
    await client.post(
        "/api/v1/workspaces",
        json={"name": "Workspace B", "slug": "workspace-b"},
        headers=headers,
    )

    # List workspaces
    response = await client.get("/api/v1/workspaces", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    slugs = [w["slug"] for w in data]
    assert "workspace-a" in slugs
    assert "workspace-b" in slugs


@pytest.mark.asyncio
async def test_add_workspace_member_and_list(client: AsyncClient):
    """Test workspace member addition and list operations."""
    # Create owner and login
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "owner@example.com",
            "password": "strongpassword123",
            "full_name": "Owner User",
        },
    )
    login_res = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "owner@example.com",
            "password": "strongpassword123",
        },
    )
    owner_token = login_res.json()["access_token"]
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    # Create target invitee user
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "invitee@example.com",
            "password": "strongpassword123",
            "full_name": "Invitee User",
        },
    )

    # Create workspace
    ws_res = await client.post(
        "/api/v1/workspaces",
        json={"name": "Team Space", "slug": "team-space"},
        headers=owner_headers,
    )
    workspace_id = ws_res.json()["id"]

    # Add member
    add_res = await client.post(
        f"/api/v1/workspaces/{workspace_id}/members",
        json={"email": "invitee@example.com", "role": "admin"},
        headers=owner_headers,
    )
    assert add_res.status_code == 200
    add_data = add_res.json()
    assert add_data["role"] == "admin"
    assert add_data["workspace_id"] == workspace_id

    # List members
    list_res = await client.get(
        f"/api/v1/workspaces/{workspace_id}/members", headers=owner_headers
    )
    assert list_res.status_code == 200
    members = list_res.json()
    assert len(members) == 2  # Creator (owner) + Invitee (admin)
    roles = [m["role"] for m in members]
    assert "owner" in roles
    assert "admin" in roles


@pytest.mark.asyncio
async def test_unauthorized_workspace_access(client: AsyncClient):
    """Test non-members cannot query workspace members."""
    # Create User A (workspace owner)
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "usera@example.com",
            "password": "strongpassword123",
            "full_name": "User A",
        },
    )
    login_a = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "usera@example.com",
            "password": "strongpassword123",
        },
    )
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Create User B (non-member of workspace A)
    await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "userb@example.com",
            "password": "strongpassword123",
            "full_name": "User B",
        },
    )
    login_b = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "userb@example.com",
            "password": "strongpassword123",
        },
    )
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates workspace
    ws_res = await client.post(
        "/api/v1/workspaces",
        json={"name": "Secret Project", "slug": "secret-project"},
        headers=headers_a,
    )
    workspace_id = ws_res.json()["id"]

    # User B attempts to access workspace members (should fail with 403)
    response = await client.get(
        f"/api/v1/workspaces/{workspace_id}/members", headers=headers_b
    )
    assert response.status_code == 403
    assert "Not a member" in response.json()["detail"]
