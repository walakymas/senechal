# Task 022: Angular upgrade 14 → 22

## Metadata
- **ID:** 022
- **Status:** `in-review`  <!-- built, 18 unit tests and a browser smoke test pass at every major; not seen by a human, not committed -->
- **Type:** `behaviour-preserving` for the data and the API; **the look changes slightly** (Angular Material "MDC" components) — see *Visual differences*
- **Branch:** `collab/angular-15` in the `AngrySenechal2` repo (from `collab/infra-and-deps`; the name is from the first step, the branch now holds the whole series)
- **Created:** 2026-10-06
- **Reviewed via PR:** <!-- link once opened -->
- **Operational impact:**
  - **Node ≥ 22.22.3 is required** wherever the frontend is built or served (`ng serve` of the systemd service `senechal-ng`, `npm ci` in `deploy/deploy.sh`, the Docker images — now `node:22-alpine`). Angular 22's CLI refuses older Node.
  - `package-lock.json` is regenerated: run `npm ci`.
  - Rebuild the frontend images (`docker compose build frontend`).
  - The pages look a little different (see below): please click through them once.

## Context
- **Problem / motivation:** Angular 14 reached end of life long ago (`npm audit`: 113 advisories, 7 of them critical), Node 16 is EOL, and the dev tooling (`protractor`, `tslint`, `codelyzer`, a View Engine JSON editor) was dead or unmaintainable.
- **Related review finding:** `03-security-audit.md` §7 (row 19), Task 020 *Left open*.
- **Definition of done:** Angular on the latest release, the app builds in production mode, every page renders, the unit tests run, no dead tooling. Met.

## Method
One major at a time with `ng update` (core + CLI, then Material), each state **built in production mode and walked through by a headless Chromium** against the real backend (throwaway PostgreSQL + the API from `Dockerfile.senechal`, seeded with synthetic characters; **the running stack was not touched**): `/`, a character, an NPC, `/team`, `/maps`, `/feast`, `/chargen`, `/admin`, and — logged in — the JSON editor dialog. A step is accepted only with 0 page errors. Between 16 and 17 the Material "MDC" migration (`ng generate @angular/material:mdc-migration`) was run, because the legacy components are removed in 17.

| From → to | Node used | What the update did | What I had to fix by hand |
|-----------|-----------|--------------------|---------------------------|
| 14 → 15 | 16 | CLI 13→14→15; Material imports rewritten to `legacy-*`; `target ES2022`, `useDefineForClassFields: false` | `Í*ngIf` typo in `npc-detail2.component.html` (a runtime error on every NPC page, already in 14); the View Engine library `ang-jsoneditor` replaced (below) |
| 15 → 16 | 16 | TypeScript 5.1, zone.js 0.13 | — |
| MDC | 16 | all Material components migrated to the MDC versions | — (see *Visual differences*) |
| 16 → 17 | 20 | TypeScript 5.4 | — |
| 17 → 18 | 22 | `HttpClientModule` → `provideHttpClient(withInterceptorsFromDi())` | the migration left `HttpClientModule` in the `providers` array (compile error) |
| 18 → 19 | 22 | `standalone: false` added to every component | — |
| 19 → 20 | 22 | TypeScript 5.8 | — |
| 20 → 21 | 22 | `provideZoneChangeDetection()` added to keep zone-based change detection | — |
| 21 → 22 | 22 | **TypeScript 6.0** | TS 6 turns `strict` on by default (hundreds of errors in code written without it): `strict: false` is now explicit; removed the deprecated `baseUrl` and `downlevelIteration`; removed the `extendedDiagnostics` block the migration had added (the Angular 22 compiler rejects it without `strictTemplates`) |

Result: `@angular/*` **22.2.1**, CLI 22.2.1, Material/CDK 22.2.1, TypeScript 6.0.3, zone.js 0.15, **rxjs 7.8.2** (was 6.6), Node 22.

## What else changed
- **JSON editor**: `ang-jsoneditor` (a View Engine package; `ngcc` is gone since Angular 16) is replaced by `src/app/json-editor/json-editor.component.ts`, a small wrapper of `jsoneditor` with the same use (`formControlName` + `[data]`); `allowedCommonJsDependencies: ["jsoneditor"]`.
- **Dead packages removed**: `angular-inline-editors`, `angular-material-icons`, `material-design-icons`, `material-icons-font` (nothing used them), `protractor`, `tslint`, `codelyzer`, `ts-node`, `jasmine-spec-reporter`, the `e2e/` folder, `tslint.json`, the `lint` and `e2e` scripts and the `e2e` target (the protractor builder no longer exists). **There is no linter now**: ESLint (`ng add angular-eslint`) is a follow-up.
- **Tests**: `ng test` works again (Karma + Jasmine 5, `ChromeHeadlessNoSandbox` launcher in `karma.conf.js`): the generated stub specs (all failing for missing providers) were rewritten to create each component with the app module; new specs for `AppComponent` and the JSON editor. **18 tests pass** in headless Chromium.
- `angular.json`: `defaultProject` gone, budgets 2.8 MB / 3.5 MB (the bundle is 2.50 MB), Dockerfiles on `node:22-alpine`.
- `dist/`: stale build artifacts that were tracked in git (`dist/AngrySenechal2/*`, June 2025) are untracked (`dist` is git-ignored); nothing deploys from them since Heroku is gone.
- `npm audit`: **113 → 12** advisories, **0 critical** (the remaining 12 are the `karma*` test tools and `@angular-devkit/build-angular`, development-time only; `npm audit --omit=dev` of the server is clean). `npm audit fix` (lockfile only, within the version ranges) was applied; `--force` was not. It moved the shipped `jsoneditor` 9.4.1 → 9.10.5 (a ReDoS fix; its `ace-builds` 1.4.12 → 1.44.0 is bigger).
- Bundle: 1.96 MB → **2.50 MB** initial (424 kB → 508 kB transferred): the MDC components, the newer `jsoneditor` / ace, nothing lazy-loaded yet (lazy routes would cut it).

## Visual differences (MDC)
Compared with screenshots of the same pages before (Angular 16 legacy) and after (MDC, and again at 22; those two are identical): the layout is the same, but
- the top menu bar is 8 px taller, the checkboxes and the rows that contain them are bigger (the trait / skill lists are longer),
- form fields (the *Modifier* and the health number) are drawn as MDC fields: a grey filled field with a small label instead of the plain line,
- the active tab label is accent-coloured, the name menu button has no round background.
The 8 `TODO(mdc-migration)` comments the schematic left in the CSS (`styles.css`, `character-detail`, `chargen`, `feast`, `team`) mark rules aimed at internal Material classes; they were not touched and nothing looked broken in the screenshots, but a human should check **the dialogs, the sliders on `/chargen` and the select boxes**.

## Left open
- A human look at the pages (above) — and the real data, which my synthetic characters do not cover.
- **`application` (esbuild) builder** instead of the deprecated `browser` builder (`ng update @angular/cli --name use-application-builder`): it moves the output to `dist/AngrySenechal2/browser`, so `server.js` / the Dockerfile need a path change.
- ESLint; migrating the components to standalone (the update only marked them `standalone: false`); signals / zoneless; lazy-loaded routes and the `trackBy` / `OnPush` work from Task 019 (can now use `@for … track`).
- The host that runs the `senechal-ng` service needs Node 22.22.3+ (`deploy/setup-systemd.sh` takes `ng` from the PATH).
- `disableHostCheck` (Task 019/020) is still there.

## Respect-the-owner checklist
- [x] Dedicated branch, not `main`.
- [x] Every major accepted only after a production build and a browser walk-through.
- [x] Deleted things listed above (dead packages, `e2e/`, `tslint.json`, tracked `dist/`).
- [x] Operational impact flagged.

## DOCUMENTATION — required
- [x] `documentation/CHANGELOG.md` entry.
- [x] `pm/STATUS.md` refreshed.
- [x] *Outcome* filled; files listed.
- [x] `CLAUDE.md` (workspace) and the frontend `README.md` updated (Angular 22, Node 22, tests).

## Files touched (repo `AngrySenechal2`)
| File | Change |
|------|--------|
| `package.json`, `package-lock.json` | Angular 22, TypeScript 6, rxjs 7, test stack, dead packages removed, lock regenerated (`npm audit fix`, lockfile only) |
| `angular.json`, `tsconfig*.json`, `karma.conf.js`, `src/main.ts`, `src/test.ts` | schematic changes, `strict: false`, budgets, headless launcher |
| `src/app/**` (≈ 20 files) | Material imports (MDC), `HttpClient` providers, `standalone: false`, the `Í*ngIf` typo, the JSON dialog |
| `src/app/json-editor/` (new) | own JSON editor component + spec |
| `src/app/**/*.spec.ts` | stub specs rewritten, new specs |
| `Dockerfile`, `Dockerfile.dev` | `node:22-alpine` |
| deleted | `e2e/`, `tslint.json`, tracked `dist/` files |

## Verification
- **How tested:** at every major: `ng build --configuration production` (Node 16 → 22 containers), then the browser walk-through (`SMOKE PASSED`, 0 page errors, JSON dialog shows the character). Final: `ng test` 18 / 18 in headless Chromium (again after `npm audit fix`, together with a last browser walk-through); `node server.test.js` on Node 22; `docker build` of `Dockerfile.dev` (CLI 22.2.1, user `node`) and `Dockerfile` (user `node`, `/` 200, missing asset 404); `npm audit`.
- **How the owner can reproduce:** `cd AngrySenechal2 && npm ci && npm run build && npm run test:server`; `CHROME_BIN=… npx ng test --watch=false --browsers=ChromeHeadlessNoSandbox`; then `docker compose build && docker compose up -d` and use the app.
- **Harness** (not committed): scripts in a temp folder that start a throwaway PostgreSQL, the API with seeded data and Playwright; ask if you want it as a repo test.

## Risk & rollback
- **Risk:** behaviour of real data and flows the smoke test does not reach (editing, claiming characters, dice, the feast screens, admin writes); the MDC look; hosts with Node < 22.
- **Rollback:** `git revert` the commit(s) of this branch, `npm ci`; the Angular 14 state is the previous commit.

## Outcome  *(fill on completion)*
- **Result:** Angular 22.2.1 on Node 22, all pages render, tests run; see above.
- **CHANGELOG entry:** 2026-10-06 — Angular upgrade 14 → 22 (Task 022)
- **Commit(s):** not committed yet
