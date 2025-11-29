from typing import Protocol


class AgentApi(Protocol):
    async def complete(self, file_content: bytes) -> dict[str, str]: ...


class IntakeAgent(AgentApi):
    """Manages agent operations including document processing."""

    def __init__(self) -> None:
        pass

    async def complete(self, file_content: bytes) -> dict[str, str]:
        """
        Process document and extract information.

        Args:
            file_content: Binary content of the uploaded file

        Returns:
            Dictionary containing extracted information
        """
        # TODO: Add logic to process the document and extract information
        return {"status": "pending"}
