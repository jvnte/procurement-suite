import asyncio

from dotenv import load_dotenv

from asklio_api.app import App
from asklio_api.config import AppConfig

if __name__ == "__main__":
    load_dotenv()
    config = AppConfig.from_env()
    app = App(config)

    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        app.shutdown()
