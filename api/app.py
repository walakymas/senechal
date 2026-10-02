"""aiohttp application exposing the same HTTP API as the former Django app (web/).

Routes, request format (form-encoded POST) and JSON output are kept identical so the
Angular frontend works unchanged. Views are synchronous (they use the shared psycopg2
connection), so each one runs in a worker thread via asyncio.to_thread.
"""
import asyncio
import os

from aiohttp import web

from api import views
from api.compat import Request

# Same list as CORS_ALLOWED_ORIGINS in web/settings.py
CORS_ALLOWED_ORIGINS = {
    "https://cdpn.io",
    "https://senechalweb.duckdns.org",
    "http://senechalweb.duckdns.org",
    "http://senechallocal.duckdns.org",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "https://codepen.io",
    "http://localhost:4200",
    "http://192.168.1.131",
    "http://senechaldev.duckdns.org",
}
CORS_ALLOW_METHODS = 'DELETE, GET, OPTIONS, PATCH, POST, PUT'
CORS_ALLOW_HEADERS = ('accept, accept-encoding, authorization, content-type, dnt, origin, '
                      'user-agent, x-csrftoken, x-requested-with')

ROUTES = [
    ('', views.index), ('json', views.get_character), ('mark', views.mark),
    ('event', views.event), ('pdf', views.pdf), ('pdfs', views.pdfs),
    ('modify', views.modify), ('npc', views.npc), ('players', views.pcs),
    ('newchar', views.newchar), ('base', views.base), ('list', views.list),
    ('token', views.token), ('user', views.user), ('adminList', views.adminList),
    ('updatePlayer', views.updatePlayer), ('cleanupTokens', views.cleanupTokens),
    ('checks', views.checks), ('feast', views.feast), ('feastConfig', views.feastConfig),
    ('maps', views.maps), ('add_map', views.add_map), ('update_map', views.update_map),
    ('delete_map', views.delete_map), ('addC2C', views.addC2C),
    ('connections', views.connections),
]


def _handler(view):
    async def handle(request):
        post = {}
        if request.method in ('POST', 'PUT', 'PATCH'):
            post = {k: v for k, v in (await request.post()).items()}
        req = Request(GET=dict(request.query), POST=post)
        try:
            resp = await asyncio.to_thread(view, req)
        except KeyError as ex:
            # Django would answer a missing form field with a 400 as well
            return web.Response(status=400, text=f'Missing parameter: {ex}')
        body = resp.content
        headers = dict(resp.headers)
        content_type = headers.pop('Content-Type')
        if hasattr(body, 'read'):  # FileResponse: stream the file, then let it go
            try:
                body = await asyncio.to_thread(body.read)
            finally:
                resp.content.close()
            return web.Response(body=body, status=resp.status, headers=headers,
                                content_type=content_type.split(';')[0])
        return web.Response(text=body, status=resp.status, headers=headers,
                            content_type=content_type.split(';')[0], charset='utf-8')
    return handle


@web.middleware
async def cors_middleware(request, handler):
    origin = request.headers.get('Origin')
    if request.method == 'OPTIONS' and origin:
        response = web.Response(status=200)
    else:
        response = await handler(request)
    if origin in CORS_ALLOWED_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Vary'] = 'Origin'
        if request.method == 'OPTIONS':
            response.headers['Access-Control-Allow-Methods'] = CORS_ALLOW_METHODS
            response.headers['Access-Control-Allow-Headers'] = CORS_ALLOW_HEADERS
            response.headers['Access-Control-Max-Age'] = '86400'
    return response


def create_app():
    app = web.Application(middlewares=[cors_middleware])
    for path, view in ROUTES:
        app.router.add_route('*', '/' + path, _handler(view))
    app.router.add_route('*', '/favicon.ico',
                         lambda r: web.HTTPFound('/static/images/favicon.ico'))
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web', 'static')
    if os.path.isdir(static_dir):
        app.router.add_static('/static/', static_dir)
    return app
