import uuid
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User, Workspace, WorkspaceMember
from auth.security import create_access_token
from database.models import Audit


@pytest.mark.asyncio
async def test_trigger_analysis_endpoint(client: AsyncClient, db_session: AsyncSession):
    """Test HTTP POST to trigger the analysis pipeline."""
    # Setup test user and workspace
    user = User(
        email="pipeline_user@uxops.ai", hashed_password="pw", full_name="Pipeline User"
    )
    workspace = Workspace(name="Pipeline Workspace", slug="pipeline-ws")
    db_session.add_all([user, workspace])
    await db_session.commit()

    member = WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role="owner")

    audit = Audit(
        workspace_id=workspace.id,
        created_by_id=user.id,
        title="Pipeline API Audit",
        status="PENDING",
    )
    db_session.add_all([member, audit])
    await db_session.commit()

    token = create_access_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"audit_id": str(audit.id)}

    # Mock the Celery task delay
    with patch("analysis.pipeline_router.run_full_audit_pipeline.delay") as mock_delay:

        class MockTask:
            id = "mock-task-id-123"

        mock_delay.return_value = MockTask()

        response = await client.post(
            f"/api/v1/workspaces/{workspace.id}/analyze",
            headers=headers,
            json=payload,
        )

        assert response.status_code == 202
        res_json = response.json()
        assert res_json["message"] == "Analysis pipeline triggered successfully."
        assert res_json["task_id"] == "mock-task-id-123"
        assert res_json["audit_id"] == str(audit.id)

        mock_delay.assert_called_once_with(str(audit.id))


@pytest.mark.asyncio
async def test_trigger_analysis_not_found(
    client: AsyncClient, db_session: AsyncSession
):
    """Test 404 response when audit is not found."""
    user = User(
        email="pipeline_user2@uxops.ai",
        hashed_password="pw",
        full_name="Pipeline User 2",
    )
    workspace = Workspace(name="Pipeline Workspace 2", slug="pipeline-ws-2")
    db_session.add_all([user, workspace])
    await db_session.commit()

    member = WorkspaceMember(workspace_id=workspace.id, user_id=user.id, role="owner")
    db_session.add(member)
    await db_session.commit()

    token = create_access_token(str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"audit_id": str(uuid.uuid4())}  # Random UUID not in DB

    response = await client.post(
        f"/api/v1/workspaces/{workspace.id}/analyze",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 404
    assert (
        response.json()["detail"]
        == "Audit not found or does not belong to this workspace"
    )
