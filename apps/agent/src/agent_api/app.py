import asyncio

from agent_api.agent import IntakeAgent
from agent_api.config import AppConfig
from agent_api.shell import Shell


class App:
    """The application runs the shell."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.agent = IntakeAgent()
        self.shell = Shell(self.config, self.agent)

    async def run(self) -> None:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.shell.run())

    def shutdown(self) -> None:
        self.shell.shutdown()
