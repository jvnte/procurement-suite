from typing import Protocol

from pydantic_ai import Agent, BinaryContent


class AgentApi(Protocol):
    async def complete(self, file_content: bytes) -> dict[str, str]: ...


class IntakeAgent(AgentApi):
    """Manages agent operations including document processing."""

    def __init__(self) -> None:
        self.agent = Agent(model="openai:gpt-4o")

    async def complete(self, file_content: bytes) -> dict[str, str]:
        """
        Process document and extract information.

        Args:
            file_content: Binary content of the uploaded file

        Returns:
            Dictionary containing extracted information
        """
        result = await self.agent.run(
            [
                "Extract the procurement information from this document.",
                BinaryContent(data=file_content, media_type="application/pdf"),
            ]
        )
        return {"status": "completed", "extracted_data": result.output}
