import json
import tempfile

import pytest

from procurement_api.config import AppConfig


@pytest.fixture
def config() -> AppConfig:
    """Create a test configuration with a temporary commodity groups file."""
    # Create a temporary commodity groups file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([{"category": "Test", "name": "Test Group"}], f)
        temp_path = f.name

    return AppConfig(host="0.0.0.0", port=0, commodity_group_data_path=temp_path)
