import asyncio
import io
from typing import Any

from fastapi.testclient import TestClient
from pydantic_ai import AgentRunResult

from agent_api.agent import AgentApi
from agent_api.config import AppConfig
from agent_api.models.procurement import (
    CommodityGroup,
    OrderLine,
    ProcurementRequestCreate,
)
from agent_api.shell import Shell, build_app


class MockAgentRunResult:
    """Mock implementation of AgentRunResult for testing."""

    def __init__(self, output: ProcurementRequestCreate):
        self.output = output
        self.data: Any = None
        self.usage: Any = None


class StubIntakeAgent(AgentApi):
    """Stub implementation of IntakeAgent for testing."""

    def __init__(self) -> None:
        self.last_file_content: bytes | None = None
        self.response: ProcurementRequestCreate | None = None

    async def complete(
        self, file_content: bytes
    ) -> AgentRunResult[ProcurementRequestCreate]:
        """Mock complete method that returns a predefined response."""
        self.last_file_content = file_content

        if self.response is None:
            # Return a default response
            self.response = ProcurementRequestCreate(
                requestor_name="Test User",
                title="Test Procurement",
                vendor_name="Test Vendor Inc",
                vat_id="DE123456789",
                commodity_group=CommodityGroup.SOFTWARE,
                order_lines=[
                    OrderLine(
                        position_description="Test Software License",
                        unit_price=100.0,
                        amount=1,
                        unit="licenses",
                        total_price=100.0,
                    )
                ],
                department="IT",
            )

        return MockAgentRunResult(self.response)  # type: ignore[return-value]


async def test_shell_can_be_shutdown(config: AppConfig):
    # given a running shell
    agent = StubIntakeAgent()
    shell = Shell(config, agent)
    loop = asyncio.get_event_loop()
    task = loop.create_task(shell.run())

    # wait for the server to start
    await asyncio.sleep(0.01)

    # when the shell is shutdown
    shell.shutdown()

    # then the shell task is done after 1 second
    await asyncio.wait_for(task, timeout=1.0)


def test_post_agent_intake_without_file_gives_422():
    # given an app
    stub_agent = StubIntakeAgent()
    app = build_app(stub_agent)

    # when we try to post without a file
    with TestClient(app) as client:
        response = client.post("/agent/intake")

        # then we get a 422 unprocessable entity response
        assert response.status_code == 422


def test_post_agent_intake_gives_200():
    # given an app with agent that has no predefined response
    stub_agent = StubIntakeAgent()
    # don't set a response, should use default
    app = build_app(stub_agent)

    # when we upload a PDF file
    pdf_content = b"%PDF-1.4\n%test"
    files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}

    with TestClient(app) as client:
        response = client.post("/agent/intake", files=files)

        # then we get the default response
        assert response.status_code == 200
        data = response.json()
        assert data["requestor_name"] == "Test User"
        assert data["title"] == "Test Procurement"
        assert data["vendor_name"] == "Test Vendor Inc"
        assert data["commodity_group"] == "Software"
