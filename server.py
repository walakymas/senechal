"""Single-process entry point: HTTP API (aiohttp) + Discord bot on one asyncio loop.

Replaces running `senechal.py` (worker) and `gunicorn web.wsgi` (web) separately.
Needs DATABASE_URL and the Discord token (`token` env var or config.yml), like before.
Listens on $PORT (default 8000).
"""
import asyncio
import logging
import os

from aiohttp import web

from api.app import create_app
from config import Config
from database.database import Database
import bot_bridge
from logs import setup_logging
import senechal

log = logging.getLogger(__name__)


def _init_database():
    with Database.lock:
        Database.initiate()


async def main():
    setup_logging()
    Config.reload()
    await asyncio.to_thread(_init_database)

    runner = web.AppRunner(create_app())
    await runner.setup()
    port = int(os.environ.get('PORT', 8000))
    await web.TCPSite(runner, '0.0.0.0', port).start()
    log.info("API listening on :%s", port)

    client = senechal.build_client()
    bot_bridge.client = client
    bot_bridge.loop = asyncio.get_running_loop()
    try:
        await client.start(Config.config['token'])
    finally:
        await client.close()
        await runner.cleanup()


if __name__ == '__main__':
    asyncio.run(main())
