from __future__ import annotations

from aiohttp import web


async def start_health_server(port: int) -> web.AppRunner:
    """Tiny HTTP endpoint so platforms such as Render can health-check the worker."""

    async def ok(_: web.Request) -> web.Response:
        return web.Response(text="Salah bot is running")

    app = web.Application()
    app.router.add_get("/", ok)
    app.router.add_get("/health", ok)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", port).start()
    return runner
