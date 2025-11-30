from contextlib import asynccontextmanager
from typing import AsyncIterator, TypedDict, cast

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import Config, Server

from procurement_api.config import AppConfig
from procurement_api.intake import IntakeApi
from procurement_api.routers.intake import router as intake_router


class ShellState(TypedDict):
    """State that is shared between requests."""

    intake: IntakeApi


def build_app(intake: IntakeApi) -> FastAPI:
    @asynccontextmanager
    async def app_lifespan(app: FastAPI) -> AsyncIterator[ShellState]:
        yield {"intake": intake}

    app = FastAPI(lifespan=app_lifespan)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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
