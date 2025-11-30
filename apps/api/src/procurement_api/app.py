import asyncio

from procurement_api.config import AppConfig
from procurement_api.intake import Intake
from procurement_api.repository import InMemoryRepository
from procurement_api.shell import Shell


class App:
    """The application runs the shell."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    async def run(self) -> None:
        async with asyncio.TaskGroup() as tg:
            repository = InMemoryRepository()
            self.intake = Intake(self.config.commodity_group_data_path, repository)
            self.shell = Shell(self.config, self.intake)

            tg.create_task(self.shell.run())

    def shutdown(self) -> None:
        self.shell.shutdown()
