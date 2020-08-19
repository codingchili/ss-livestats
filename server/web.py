from aiohttp import web

from server.log import log

async def index(request):
    return web.FileResponse('./web/index.html')


def serve():
    log("serving contents of /web.")
    app = web.Application()
    app.add_routes([web.get('/', index)])
    app.router.add_static('/', './web')
    web.run_app(app)
