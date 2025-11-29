import asyncio

from asklio_api.app import App
from asklio_api.config import AppConfig


async def test_app_can_be_shutdown(config: AppConfig):
    # Given a running app
    app = App(config)
    task = asyncio.create_task(app.run())
    await asyncio.sleep(0.01)

    # When we shutdown the app
    app.shutdown()

    # Then the task completes
    await asyncio.wait_for(task, timeout=1.0)
