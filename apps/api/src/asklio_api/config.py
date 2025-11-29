from __future__ import annotations

import json
import os
from typing import NamedTuple

from asklio_api.models.commodity_group import CommodityGroupInfo


class AppConfig(NamedTuple):
    """Configuration on how to run the app"""

    host: str
    port: int
    commodity_group_data_path: str

    @classmethod
    def from_env(cls) -> AppConfig:
        """Load configuration from environment variables"""
        return cls(
            host=os.environ["API_HOST"],
            port=int(os.environ["API_PORT"]),
            commodity_group_data_path=os.environ["COMMODITY_GROUPS_DATA_PATH"],
        )

    @classmethod
    def with_free_port(cls, commodity_group_data_path: str) -> AppConfig:
        """Create a configuration with a free port, useful for testing"""
        return cls(
            host="0.0.0.0",
            port=0,
            commodity_group_data_path=commodity_group_data_path,
        )
