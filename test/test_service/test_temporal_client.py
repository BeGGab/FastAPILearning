from unittest.mock import AsyncMock, Mock, patch

import pytest
from temporalio.exceptions import WorkflowAlreadyStartedError

from src.temporal.client import run_create_author_saga
from src.temporal.models import (
    CompensationResult,
    CreateAuthorSagaInput,
    CreateAuthorSagaResult,
)
from src.temporal.workflows.create_author_saga_workflow import CreateAuthorSagaWorkflow


def _payload(request_id: str = "req-1") -> CreateAuthorSagaInput:
    return CreateAuthorSagaInput(
        request_id=request_id,
        name="Author",
        books=[],
        biography_text=None,
        year_of_birth=None,
        year_of_death=None,
    )


def _result(author_id: str = "a-id") -> CreateAuthorSagaResult:
    return CreateAuthorSagaResult(
        author_id=author_id,
        biography_created=False,
        compensated_author=CompensationResult(attempted=False, success=False),
        compensated_biography=CompensationResult(attempted=False, success=False),
    )


@pytest.mark.asyncio
async def test_run_create_author_saga_starts_new_workflow() -> None:
    payload = _payload("req-new")
    expected = _result("author-new")

    handle = AsyncMock()
    handle.result = AsyncMock(return_value=expected)

    temporal_client = AsyncMock()
    temporal_client.start_workflow = AsyncMock(return_value=handle)

    settings = Mock(
        temporal_host="localhost:7233",
        temporal_namespace="default",
        temporal_task_queue="authors",
    )

    with patch("src.temporal.client.Settings", return_value=settings), patch(
        "src.temporal.client.Client.connect",
        new=AsyncMock(return_value=temporal_client),
    ):
        result = await run_create_author_saga(payload)

    assert result == expected
    temporal_client.start_workflow.assert_awaited_once_with(
        CreateAuthorSagaWorkflow.run,
        payload,
        id="create-author-req-new",
        task_queue="authors",
    )


@pytest.mark.asyncio
async def test_run_create_author_saga_uses_existing_workflow_on_duplicate_id() -> None:
    payload = _payload("req-dup")
    expected = _result("author-dup")

    handle = AsyncMock()
    handle.result = AsyncMock(return_value=expected)

    temporal_client = AsyncMock()
    temporal_client.start_workflow = AsyncMock(
        side_effect=WorkflowAlreadyStartedError(
            workflow_id="create-author-req-dup",
            workflow_type="CreateAuthorSagaWorkflow",
        )
    )
    temporal_client.get_workflow_handle = Mock(return_value=handle)

    settings = Mock(
        temporal_host="localhost:7233",
        temporal_namespace="default",
        temporal_task_queue="authors",
    )

    with patch("src.temporal.client.Settings", return_value=settings), patch(
        "src.temporal.client.Client.connect",
        new=AsyncMock(return_value=temporal_client),
    ):
        result = await run_create_author_saga(payload)

    assert result == expected
    temporal_client.start_workflow.assert_awaited_once()
    temporal_client.get_workflow_handle.assert_called_once_with("create-author-req-dup")
