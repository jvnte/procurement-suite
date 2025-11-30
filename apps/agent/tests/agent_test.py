import io
from typing import Any

from fastapi.testclient import TestClient
from pydantic_ai import AgentRunResult

from agent_api.agent import AgentApi
from agent_api.models.procurement import (
    CommodityGroup,
    OrderLine,
    ProcurementRequestCreate,
)
from agent_api.shell import build_app


class MockAgentRunResult:
    """Mock implementation of AgentRunResult for testing."""

    def __init__(self, output: ProcurementRequestCreate):
        self.output = output
        self.data: Any = None
        self.usage: Any = None


class StubIntakeAgent(AgentApi):
    async def complete(
        self, file_content: bytes
    ) -> AgentRunResult[ProcurementRequestCreate]:
        # Create a mock AgentRunResult

        return MockAgentRunResult(  # type: ignore[return-value]
            ProcurementRequestCreate(
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
        )


def test_post_agent_intake_gives_200():
    # given an app
    app = build_app(StubIntakeAgent())

    # when we upload a PDF file
    pdf_content = b"%PDF-1.4\n%fake pdf content"
    files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}

    with TestClient(app) as client:
        response = client.post("/agent/intake", files=files)

        # then we get a 200 OK response
        assert response.status_code == 200
        data = response.json()
        assert data["requestor_name"] == "Test User"
        assert data["title"] == "Test Procurement"
        assert data["vendor_name"] == "Test Vendor Inc"
        assert data["commodity_group"] == "Software"
