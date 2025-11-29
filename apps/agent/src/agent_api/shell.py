from contextlib import asynccontextmanager
from typing import AsyncIterator, TypedDict

from fastapi import FastAPI
from uvicorn import Config, Server

from agent_api.agent import AgentApi, IntakeAgent
from agent_api.config import AppConfig
from agent_api.routers.agent import router as agent_router


class ShellState(TypedDict):
    """State that is shared between requests."""

    intake_agent: AgentApi


def build_app(intake_agent: AgentApi) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[ShellState]:
        yield {"intake_agent": intake_agent}

    app = FastAPI(lifespan=lifespan)
    app.include_router(agent_router)
    return app


class Shell:
    """Provide user access to our application."""

    def __init__(self, config: AppConfig, intake_agent: IntakeAgent) -> None:
        self.config = config
        self.app = build_app(intake_agent)
        self.server: Server | None = None

    async def run(self) -> None:
        config = Config(
            app=self.app,
            host=self.config.host,
            port=self.config.port,
            loop="asyncio",
            lifespan="on",
        )
        self.server = Server(config)
        await self.server.serve()

    def shutdown(self) -> None:
        """Gracefully shut down the server"""
        if self.server is None:
            raise RuntimeError("Server not running")
        self.server.should_exit = True
