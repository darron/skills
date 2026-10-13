---
name: build-maintainable-go-tools
description: Build or substantially improve embeddable Go packages, companion CLIs, and their testing and release setup using Darron's engineering approach. Use for a new project or a substantial architecture/delivery pass; ordinary small edits do not require this whole workflow.
---

# Build maintainable Go tools

Build an understandable core, practical operator tools, and a delivery path that
works for real users. Adapt this approach to the product; do not reproduce otgo's
features or impose the same ceremony on every change.

For a new project, read [the approach and examples](references/approach.md).
For a focused task, read only the relevant section when more detail is needed.
The reference records accepted preferences and examples, not an immutable stack.

## Establish the product and boundaries

Read the existing repo conventions and identify the primary capability, its
callers, external compatibility requirements, and authorized delivery scope.
Use the current task and prior decisions before asking for clarification.

Prefer Go for the package/tool when it fits. Separate the reusable implementation
from command dispatch and operator UI. Have the CLI exercise the same core.
For a CLI-only product, preserve useful internal seams without manufacturing a
public SDK. Existing service and wire contracts must remain compatible even
when a local API changes.

Let embedding applications own output, process exit, signals, registries and
administrative servers. Make startup, running lifetime, cancellation and cleanup
explicit. Use copied state and typed errors where they support real callers.

## Choose dependencies and operation deliberately

Prefer the standard library, but use established dependencies when they avoid
maintaining delicate protocol/security code or improve interoperability. Use the
official Prometheus client for Prometheus integration rather than recreating its
exposition format. Keep optional integrations outside the core import path;
let the caller choose its registry and listener.

Provide useful help, errors, inspection commands and structured output where
appropriate. Include version, source SHA and clean/dirty/unknown build state.
For reusable state, prefer named profiles and XDG paths where they fit. Support
concurrent instances, discoverable paths, and defined flag/config precedence.
Setup should show the next concrete command, including the actual profile.

If the tool exposes a backend, enforce its protection across methods, paths,
streams and machine endpoints by default. Unsupported authentication must not
create an access exception. Keep administrative endpoints separate and private
by default. Bound resources, protect saved credentials, redact diagnostics and
state remaining trust relationships honestly.

## Prove behavior and review the tests

Use native Go tests and local integration fixtures. Exercise real HTTP, TLS,
WebSocket and storage behavior when that is the contract under test. Mock an
external boundary rather than the implementation being proved.

Add regression tests for fixes and hardening. Assert independently observable
outcomes: bytes delivered, zero unauthorized backend calls, resources released,
correct errors, and actual cancellation/revocation. Avoid circular expectations
copied from production constants and timing assumptions based on arbitrary sleeps.
For consequential boundaries, deliberately break the behavior in an isolated
copy and check that its regression fails.

Use race tests and bounded fuzzing where concurrency or hostile input warrants
them. Test the built CLI and embedding example, then real-service compatibility
for relevant changes. Distinguish local fixtures, hosted tests and installed
artifact verification. Repeat affected paths after consequential fixes.

For substantial or sensitive work, seek independent code and test-quality review
when authorized and available. Respect named review tools' invocation rules.
Validate findings with code and reproducible evidence; follow up on consequential
fixes. Scale this effort to risk, not a fixed reviewer count.

## Keep checks and documentation repeatable

Prefer thin Makefile targets around ordinary commands. Run full-package
formatting and golangci-lint, vet, relevant tests and builds. Check known reachable
vulnerabilities with govulncheck when appropriate. Test the supported minimum Go
series and a current patched supported release; do not freeze obsolete versions
because the original project used them.

Put installation and the main working flow early in the README. Provide Go
package docs and executable examples for exported contracts. Keep deeper guides
behind a small index. Use plain language and copyable commands; apply the
requested i-have-adhd simplification guidance when available. Archive historical
reviews and keep agent working plans out of public product docs by default.
Record dated validation evidence, scope and material unverified behavior.

## Finish the authorized delivery

When release/distribution is in scope, maintain CHANGELOG.md and publish high-level
notes on the release rather than adding a release-notes file to docs. Build CLI
executables for distribution; library consumers use Go modules.

Automate release-triggered package-manager updates rather than periodic cron
polling. For Homebrew, use the project's chosen tap and document the exact secret
and minimal permissions. Attach appropriate platform binaries and SHA256 files
to GitHub releases. Build immutable release source, verify version/SHA metadata,
check hashes, and run native smoke tests before publication.

Make retry/backfill behavior safe: skip identical assets, add missing files,
and refuse conflicting replacements. Separate build execution from publication
credentials; scope permissions and pin action revisions. Verify actual downloads
and the installed package-manager result. Checksums are not independent signatures.

Carry authorized work through to a concrete result without repeated permission
questions. Use project instructions for branch, license, platforms and publishing;
this skill grants no new authority. Identify physical authentication, provider
consent or other owner-only actions precisely when they genuinely block progress.
Report changes, evidence, availability and any material unfinished verification.
