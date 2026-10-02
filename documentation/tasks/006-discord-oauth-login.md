# Task 006: Discord OAuth2 web login (authentication only)

## Metadata
- **ID:** 006 · **Status:** `in-progress` (needs Discord credentials to verify) · **Type:** `behaviour-changing`
- **Branch:** `collab/single-process` (builds on task 005)
- **Operational impact:** set `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET` (and optionally
  `DISCORD_REDIRECT_URI`, default `http://localhost:8000/auth/callback`, `FRONTEND_URL`, default
  `http://localhost:4200`); register the redirect URI in the Discord Developer Portal.

## Scope
- **In:** `GET /auth/login`, `GET /auth/callback` (`api/auth.py`); `TokenTable.issue`; Angular
  "Login with Discord" (`AngrySenechal2/src/app/app.component.*`).
- **Out:** authorization (write endpoints stay unprotected; `Config.authorization` unchanged),
  guild-membership check, cookie sessions. The old `/token` + `.token` bot flow is untouched.

## How it works
1. Frontend -> `/auth/login?return=<origin>` -> Discord authorize (`scope=identify`, random `state`).
2. `/auth/callback`: checks `state`, exchanges the code, reads `/users/@me`.
3. Only known players: `PlayerTable().get_by_did(<discord id>)`; unknown -> `#error=unknown_player`.
4. Inserts an active token (1 day) into `tokens`, redirects to `<origin>/#token=<token>`.
   The fragment is never sent to a server. The frontend stores it in `localStorage`, clears the URL.
   `return` is accepted only if it is in the CORS allow-list, else `FRONTEND_URL`.

## Verification
- Without credentials `/auth/login` -> 503; invalid `state` -> 400; frontend compiles.
- Not yet run with real Discord credentials.

## Risk & rollback
- `git revert`; `/token` flow still available in the backend.
