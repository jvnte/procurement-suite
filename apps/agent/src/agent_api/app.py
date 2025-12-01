import asyncio

from agent_api.agent import IntakeAgent, IntakeAgentApi
from agent_api.config import AppConfig
from agent_api.shell import Shell


class App:
    """The application runs the shell."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        agent = IntakeAgent(openai_api_key=config.openai_key)
        self.intake_agent_api = IntakeAgentApi(agent=agent)
        self.shell = Shell(self.config, self.intake_agent_api)

    async def run(self) -> None:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.shell.run())

    def shutdown(self) -> None:
        self.shell.shutdown()
