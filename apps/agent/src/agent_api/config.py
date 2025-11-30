from __future__ import annotations

import os
from typing import NamedTuple


class AppConfig(NamedTuple):
    """Configuration on how to run the app"""

    host: str
    port: int
    openai_key: str
    mcp_server_url: str

    @classmethod
    def from_env(cls) -> AppConfig:
        """Load configuration from environment variables"""
        return cls(
            host=os.environ["API_HOST"],
            port=int(os.environ["API_PORT"]),
            openai_key=str(os.environ["OPENAI_API_KEY"]),
            mcp_server_url=str(os.environ["MCP_SERVER_URL"]),
        )

    @classmethod
    def with_free_port(cls) -> AppConfig:
        """Create a configuration with a free port, useful for testing"""
        return cls(host="0.0.0.0", port=0, openai_key="", mcp_server_url="")
