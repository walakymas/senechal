"""Discord OAuth2 login (authentication only): identifies the user via Discord and lets in
only known players (player.did = Discord user id). On success the browser is redirected
back to the frontend with the session token in the URL fragment: <origin>/#token=<token>
(a fragment is never sent to a server, so it stays out of logs and Referer headers).

Env: DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET,
     DISCORD_REDIRECT_URI (default http://localhost:8000/auth/callback),
     FRONTEND_URL (default http://localhost:4200; used when no valid ?return= is given).
"""
import asyncio
import os
import secrets
import time
import uuid
from urllib.parse import urlencode

import aiohttp
from aiohttp import web

from database.playertable import PlayerTable
from database.tokenstable import TokenTable

DISCORD_API = 'https://discord.com/api'
STATE_TTL = 600
_states = {}  # state -> (return origin, created); single process, so memory is enough


def _config():
    return (os.environ.get('DISCORD_CLIENT_ID'), os.environ.get('DISCORD_CLIENT_SECRET'),
            os.environ.get('DISCORD_REDIRECT_URI', 'http://localhost:8000/auth/callback'))


def _frontend(requested, allowed):
    default = os.environ.get('FRONTEND_URL', 'http://localhost:4200').rstrip('/')
    return requested if requested in allowed else default


def _back(origin, **params):
    return web.HTTPFound(f"{origin}/#{urlencode(params)}")


def _login_user(discord_id):
    player = PlayerTable().get_by_did(discord_id)
    if not player:
        return None
    token = f"{uuid.uuid4()}"
    TokenTable().issue(token, player[0])
    return token


def make_handlers(allowed_origins):
    async def login(request):
        client_id, _, redirect_uri = _config()
        if not client_id:
            return web.Response(status=503, text='Discord login is not configured (DISCORD_CLIENT_ID).')
        now = time.time()
        for k in [k for k, v in _states.items() if now - v[1] > STATE_TTL]:
            del _states[k]
        state = secrets.token_urlsafe(24)
        _states[state] = (_frontend(request.query.get('return'), allowed_origins), now)
        return web.HTTPFound(f"{DISCORD_API}/oauth2/authorize?" + urlencode({
            'client_id': client_id, 'redirect_uri': redirect_uri, 'response_type': 'code',
            'scope': 'identify', 'state': state, 'prompt': 'none'}))

    async def callback(request):
        client_id, client_secret, redirect_uri = _config()
        origin, created = _states.pop(request.query.get('state'), (None, 0))
        if origin is None or time.time() - created > STATE_TTL:
            return web.Response(status=400, text='Invalid or expired login state. Please try again.')
        code = request.query.get('code')
        if not code:
            return _back(origin, error='denied')
        headers = {'User-Agent': 'DiscordBot (senechal, 1.0)'}
        try:
            async with aiohttp.ClientSession(headers=headers) as http:
                async with http.post(f"{DISCORD_API}/oauth2/token", data={
                        'client_id': client_id, 'client_secret': client_secret,
                        'grant_type': 'authorization_code', 'code': code,
                        'redirect_uri': redirect_uri}) as r:
                    if r.status != 200:
                        return _back(origin, error='discord')
                    access_token = (await r.json())['access_token']
                async with http.get(f"{DISCORD_API}/users/@me",
                                    headers={'Authorization': f'Bearer {access_token}'}) as r:
                    if r.status != 200:
                        return _back(origin, error='discord')
                    discord_id = int((await r.json())['id'])
        except (aiohttp.ClientError, asyncio.TimeoutError, KeyError, ValueError):
            return _back(origin, error='discord')
        token = await asyncio.to_thread(_login_user, discord_id)
        if token is None:
            return _back(origin, error='unknown_player')
        return _back(origin, token=token)

    return login, callback
