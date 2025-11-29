import inspect
from contextlib import asynccontextmanager
from typing import AsyncIterator, TypedDict, cast

from fastapi import APIRouter, Depends, FastAPI, Request
from fastmcp import FastMCP
from uvicorn import Config, Server

from asklio_api.config import AppConfig
from asklio_api.intake import IntakeApi
from asklio_api.routers.intake import router as intake_router


class ShellState(TypedDict):
    """State that is shared between requests."""

    intake: IntakeApi


def build_app(intake: IntakeApi) -> FastAPI:
    @asynccontextmanager
    async def app_lifespan(app: FastAPI):
        yield

    mcp = FastMCP()
    mcp.resource(
        name="Get Commodity Groups",
        uri="data://commodity_groups",
        title="Get information about all valid commodity groups",
        description=inspect.getdoc(intake.get_commodity_groups),
    )(intake.get_commodity_groups)
    mcp.tool(
        name="Perform Procurement Request",
        title="Try to perform a procurement request",
        description=inspect.getdoc(intake.create_procurement_request),
    )(intake.create_procurement_request)
    mcp_app = mcp.http_app(path="/mcp")

    @asynccontextmanager
    async def combined_lifespan(app: FastAPI) -> AsyncIterator[ShellState]:
        async with app_lifespan(app):
            async with mcp_app.lifespan(app):
                yield {"intake": intake}

    app = FastAPI(lifespan=combined_lifespan)
    app.mount("/v1", mcp_app)
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
