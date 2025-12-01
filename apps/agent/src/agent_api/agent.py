from typing import Any, Protocol, Sequence

from pydantic_ai import Agent as PydanticAgent
from pydantic_ai import AgentRunResult, BinaryContent, UserContent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from agent_api.models.procurement import ProcurementRequestCreate


class Agent(Protocol):
    """Protocol for agents that can process user prompts."""

    async def run(
        self, user_prompt: str | Sequence[UserContent]
    ) -> AgentRunResult[Any]: ...


class AgentApi(Protocol):
    """Protocol for the intake agent API."""

    async def complete(self, file_content: bytes) -> AgentRunResult[Any]: ...


class IntakeAgent(Agent):
    """Agent that extracts procurement information from documents."""

    def __init__(self, openai_api_key: str) -> None:
        self.agent = PydanticAgent(
            OpenAIChatModel("gpt-5", provider=OpenAIProvider(api_key=openai_api_key)),
            output_type=ProcurementRequestCreate,
        )

    async def run(
        self, user_prompt: str | Sequence[UserContent]
    ) -> AgentRunResult[ProcurementRequestCreate]:
        """
        Process a user prompt with the agent.

        Args:
            user_prompt: The prompt to send to the agent (can be string or sequence of user content)

        Returns:
            AgentRunResult with the extracted procurement information
        """
        return await self.agent.run(user_prompt)


class IntakeAgentApi(AgentApi):
    """Manages intake operations including document processing."""

    def __init__(self, agent: Agent) -> None:
        self.agent = agent

    async def complete(
        self, file_content: bytes
    ) -> AgentRunResult[ProcurementRequestCreate]:
        """
        Process document and extract information.

        Args:
            file_content: Binary content of the uploaded file

        Returns:
            AgentRunResult containing extracted information
        """
        return await self.agent.run(
            [
                "Extract the procurement information from this document.",
                BinaryContent(data=file_content, media_type="application/pdf"),
            ]
        )
