# Stack Shape

## Default Layout

Use this as the default shape unless the repo already has an established layout:

```text
cmd/server/          Go server entrypoint
web/                 HTTP handlers, shell templates, embedded assets
web/ui/              Vite + Svelte frontend source
web/ui/src/lib/      shared UI components, bootstrap helpers, API helpers
web/ui/src/pages/    page entrypoints or page components
internal/            shared Go packages
storage/             database access and queries
featureflags/        optional feature-flag seam
```

## Go Responsibilities

- route ownership and auth
- session and CSRF handling
- bootstrap payload generation
- JSON API endpoints
- service wiring and background workers
- `go:embed` static asset serving in production

## Frontend Responsibilities

- page rendering inside the authenticated shell
- shared components and design tokens
- page-local state and async updates
- mutation UX and optimistic UI only when the server contract is already clear

## Bootstrap Contract

Default bootstrap payload:

```json
{
  "page": "projects.detail",
  "user": {},
  "csrfToken": "...",
  "data": {}
}
```

Rules:

- include everything needed for first render
- keep it typed in Go
- avoid scraping cookies or DOM fragments when bootstrap can carry the value directly

## API Defaults

- page routes return HTML shells only
- async reads and mutations use `/api` or `/api/v1`
- prefer stable route names over raw paths when instrumenting metrics
- keep request and response shapes explicit and versioned when they will be reused outside the browser

## Delivery Checklist

- schema and query shape are Postgres-safe
- `web` stays thin
- service logic is reused across web and API surfaces
- feature gating, when used, is enforced below the UI
- metrics use low-cardinality labels only
- Vite output is embedded and cache-busted
- README or operator docs are updated when config or startup behavior changes
