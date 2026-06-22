---
name: go-vite-svelte-builder
description: Plan, scaffold, or refactor a Go-routed application with an embedded Vite + Svelte frontend. Use when building a Golang/Vite/Svelte project, extracting page shells and JSON APIs, defining package seams, or turning a feature spec into this stack without drifting into a heavy SPA by default.
---

# Go Vite Svelte Builder

Use this skill when the target stack is Go backend + Vite-bundled Svelte frontend, especially when Go should keep routing, auth, CSRF, and production asset serving.

## Workflow

1. Lock the contract before scaffolding.

- For non-trivial work, write or update a short spec first.
- Include: `Summary`, `Current State`, `Goals`, `Non-Goals`, `Locked Product Decisions` or `Product Contract`, `Architecture` / `Package boundary`, API/UI/data shape, `Implementation Phases`, `Testing Plan`, and `Acceptance Criteria`.
- If both a `PLAN` and `SPEC` exist, treat the `SPEC` as the current build contract.

2. Keep the stack boundary explicit.

- Go owns routes, auth/session handling, CSRF, service wiring, HTML shell rendering, and static asset serving.
- Svelte owns authenticated page UI, shared components, client-side state, and async interactions.
- Leave login or similar auth bootstrap pages server-rendered unless the task explicitly moves them.

3. Prefer a server-routed multipage app over a heavy SPA by default.

- Keep stable URLs owned by Go.
- Render a minimal shell from Go.
- Inject a typed bootstrap payload with `page`, `user`, `csrfToken`, and page `data`.
- Mount the page-specific Svelte entry into that shell.
- Read [references/stack-shape.md](references/stack-shape.md) for the default layout and delivery checklist.

4. Preserve a single behavior path.

- Web pages, JSON APIs, CLI flows, and future agent flows should call the same service/package seam when practical.
- Do not create an API-only runner or duplicate business logic in page handlers.

5. Build backend seams before UI polish.

- Add or clarify package boundaries first.
- Prefer service packages over burying product logic in `web`.
- Keep SQL in storage packages only.
- Keep schema and query shapes Postgres-safe even if SQLite is used first.

6. Prefer explicit JSON APIs.

- Add `/api` or `/api/v1` endpoints instead of switching page handlers between HTML and JSON based on `Accept`.
- Use the Go bootstrap payload for first render, then use JSON APIs for refreshes and mutations.
- Keep external API DTOs separate from HTML view structs when that avoids drift.

7. Reuse a design system early.

- Define CSS variables and Tailwind theme values before building many pages.
- Build shared layout and control primitives before page-local variants.
- When working inside an existing product, preserve the established design language instead of restyling everything.

8. Add rollout and observability on purpose.

- For optional surfaces, consider feature-flag seams at both the UI and service/route layers.
- Add low-cardinality metrics and clear timeout or stale-state behavior for background work.
- Avoid labels built from raw IDs, usernames, file names, or arbitrary error text.

9. Sequence implementation in this order when possible.

1. storage shape or schema
2. service package and tests
3. page shell and bootstrap contract
4. JSON endpoints
5. Svelte pages and shared components
6. Vite build and `go:embed` wiring
7. rollout docs and verification

10. Review before calling it done.

- Check auth and CSRF boundaries.
- Check API versus HTML separation.
- Check typed bootstrap payloads instead of cookie or DOM scraping.
- Check shared-component and design-token reuse.
- Check service-layer enforcement for gated features.
- Check operator-facing docs when env vars, startup, routing, or build steps change.

## Defaults

- Prefer `web/ui/` for frontend source and `web/ui/dist/` for Vite output in an existing Go app.
- Prefer `go:embed` for production asset delivery.
- Prefer typed bootstrap structs in Go over inline page scripts.
- Prefer shared Svelte helpers/components over per-page fetch patterns.
