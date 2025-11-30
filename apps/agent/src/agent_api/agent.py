from typing import Any, Protocol

from pydantic_ai import Agent, AgentRunResult, BinaryContent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from agent_api.models.procurement import ProcurementRequestCreate


class AgentApi(Protocol):
    async def complete(self, file_content: bytes) -> AgentRunResult[Any]: ...


class IntakeAgent(AgentApi):
    """Manages agent operations including document processing."""

    def __init__(self, openai_api_key: str) -> None:
        self.agent = Agent(
            OpenAIChatModel("gpt-5", provider=OpenAIProvider(api_key=openai_api_key)),
            output_type=ProcurementRequestCreate,
        )

    async def complete(
        self, file_content: bytes
    ) -> AgentRunResult[ProcurementRequestCreate]:
        """
        Process document and extract information.

        Args:
            file_content: Binary content of the uploaded file

        Returns:
            Dictionary containing extracted information
        """
        return await self.agent.run(
            [
                "Extract the procurement information from this document.",
                BinaryContent(data=file_content, media_type="application/pdf"),
            ]
        )
