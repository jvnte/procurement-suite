from contextlib import asynccontextmanager
from typing import AsyncIterator, TypedDict, cast

from fastapi import APIRouter, Depends, FastAPI, Request
from uvicorn import Config, Server

from asklio_api.config import AppConfig
from asklio_api.intake import IntakeApi
from asklio_api.routers.intake import router as intake_router


class ShellState(TypedDict):
    """State that is shared between requests."""

    intake: IntakeApi


def build_app(intake: IntakeApi) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[ShellState]:
        yield {"intake": intake}

    app = FastAPI(lifespan=lifespan)
    app.include_router(intake_router)
    return app


class Shell:
    """Provide user access to our application."""

    def __init__(self, config: AppConfig, intake: IntakeApi) -> None:
        self.config = config
        self.app = build_app(intake)
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
