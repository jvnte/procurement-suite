import pytest

from agent_api.config import AppConfig


@pytest.fixture
def config() -> AppConfig:
    """Create a test configuration with a free port."""
    return AppConfig.with_free_port()
