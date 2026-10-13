# Darron's approach to building software

This describes the approach used to build go-opentunnel and otgo, then translates
it into guidance for future projects. It captures product and engineering
preferences, rather than prescribing another tunnel client.

## The approach in one paragraph

Build a small, understandable core that other applications can embed. Give it a
usable CLI that exercises the same implementation and makes operation easy.
Prefer Go and the standard library, adding established dependencies when they
reduce the amount of delicate code we must maintain. Make persistence, security,
diagnostics and shutdown explicit. Test actual behavior, including failures and
integration with the real service. Use independent reviews to challenge both
the implementation and its tests. Finish with clear documentation and automated,
verifiable releases that people can actually install.

## 1. Start with the capability and its real use

The original request was an embeddable Go client compatible with an existing
service. The CLI initially existed to exercise that package. Later, a real use
case—protecting a local application without modifying its backend—made the CLI
an operational product in its own right.

The reusable lesson is to establish the primary use case and prove it early.
Supporting tools should make that capability easier to test, understand and
operate. They may grow when a real need appears; their initial role need not
become a permanent restriction.

For an implementation of an existing protocol, inspect the upstream contract
and preserve interoperability. Go API ergonomics may differ from JavaScript,
and local APIs may change before adoption. The external service contract still
has to work.

Avoid adding a framework or service layer merely because the project could
eventually need one. Add the next capability because someone can describe what
they will do with it.

## 2. Make the core genuinely embeddable

The package should let a caller own its application:

- Return results and useful errors; leave terminal output and process exit to
  the CLI.
- Make startup, running lifetime, cancellation and cleanup understandable.
- Support caller configuration, storage and integration points where useful.
- Keep process-wide behavior out of ordinary library construction: no surprise
  signals, global metrics registration or administrative listeners.
- Expose state safely enough for an application to inspect and present it.

The CLI should consume the package instead of maintaining another copy of its
protocol or lifecycle logic. Operator-specific features can live in internal
packages; they need not expand the public SDK.

Optional integrations should remain optional at the import boundary. Here,
statistics are available from the core, while a separate adapter uses the
official Prometheus client. An embedding application chooses its registry and
where to serve it. That is a useful pattern for other integrations too.

## 3. Prefer simple tooling and deliberate dependencies

The explicit preference was Go with as few non-standard-library packages as
practical. That is a maintenance preference, not a rule to reimplement every
established ecosystem component.

Use the standard library when it provides an adequate, understandable solution.
Use a mature dependency when the alternative creates substantial protocol,
security or interoperability work. WebSocket transport and the official
Prometheus client were appropriate exceptions here.

Judge dependencies by what they save us from maintaining, their runtime impact
and where they enter the architecture. The root package's compiled dependencies
matter separately from the module's complete dependency list.

Use a small set of ordinary tools with clear entry points:

| Need | Choice in this project | Reusable preference |
| --- | --- | --- |
| Implementation | Go | A language/runtime that supports simple deployment and embedding |
| Repeatable commands | Makefile | Thin wrappers around commands developers can inspect |
| Tests and concurrency checks | `go test`, race detector | Native tools before another test framework |
| Formatting and lint | `golangci-lint fmt --diff`, `golangci-lint run ./...` | Check the whole relevant codebase |
| Vulnerability checks | `govulncheck` | Check known reachable vulnerabilities; distinguish this from a security audit |
| Automation | GitHub Actions | Versioned workflows with bounded jobs and scoped credentials |
| Release helpers | Small standard-library Python scripts | Straightforward automation with its own tests |
| Distribution | Go modules, Homebrew, GitHub assets | Support developers and operators through their usual tools |

Do not freeze the toolchain for historical reasons. Document a minimum supported
version, test it, and also test/build with a current patched supported version.
The particular versions used here are project facts, not permanent skill rules.

## 4. Treat the CLI as part of the product

A CLI should help someone succeed without remembering how the implementation
works.

Provide useful help, actionable errors and inspectable state. A version command
should identify the version, source SHA and clean/dirty state, with an honest
`unknown` when metadata is unavailable. Where automation is useful, offer
structured output without mixing status chatter into it.

Save settings that people will reuse. Named profiles let multiple backends run
independently on one machine. The operator should be able to find configuration
paths, list known profiles and endpoints, and obtain a launch command while
instances are running or stopped. Use XDG locations where appropriate and
document what lives there.

Keep command-line flags and saved configuration consistent: validate both,
define precedence, and provide an explicit way to disable an optional setting.
Do not require someone to repeat a metrics address on every launch if it can be
saved safely.

Setup should end with the next action. Showing a copyable command containing the
actual profile name is more useful than a generic success page. Browser login
pages deserve readable styling, recognizable controls and a coherent visual
identity. Polish follows demonstrated use; it is part of making the software
usable, rather than an excuse to introduce a frontend stack.

## 5. Put protection at the right boundary

The auth proxy exists because the backend applications should not all have to
implement authentication themselves. A shared boundary protects every backend
path by default, including paths we did not know about during development.

That leads to reusable questions:

- Does an unauthenticated request reach any backend code?
- Do assets, alternate methods, streams, WebSockets and machine endpoints pass
  through the same protection?
- Does an unsupported client remain denied instead of acquiring an exception?
- Can credentials, cookies or spoofed identity headers reach the wrong party?
- Can cached responses or existing streams defeat logout or revocation?

Security includes failure and lifecycle behavior: bounded buffers, queues and
work; private storage; cancellation; expiry; rotation; shutdown; and safe error
rendering. Test those boundaries along with successful login.

Keep administrative visibility separate from public exposure. Here, optional
metrics use a separate loopback listener, not a public auth-proxy route, and
omit credentials and tunnel identities.

Document what protection actually guarantees, who remains trusted and what is
outside its control. Locally held TLS keys, for example, do not remove every
trust relationship with the operator of a public domain. A security document
should remain accurate as our understanding changes.

These are defaults for projects with a comparable exposure boundary. A local
batch tool does not need an auth proxy merely to match this project.

## 6. Demand tests that would catch the failure

The strongest testing preference was not a coverage percentage. It was that
tests should be meaningful and test what their names claim.

Use layers according to the behavior being verified:

| Layer | What it establishes |
| --- | --- |
| Focused unit/property tests | Parsing, validation, encoding, limits and independent invariants |
| Local integration fixtures | Components interacting over real HTTP, WebSockets, TLS and storage |
| Built CLI and example application | Commands and embedding paths exercise the package correctly |
| Race and fuzz tests | Concurrent failures and unexpected inputs within a bounded run |
| Real-service tests | Actual upstream compatibility, provisioning and end-to-end use |
| Installed/released artifact checks | People receive an executable that reports and behaves as expected |

Mock the external boundary where necessary, rather than replacing the behavior
we are trying to prove. A zero backend-request counter is strong evidence for
an anonymous-access test. Real streamed bytes and transport closure are stronger
than an in-memory response recorder for stream revocation.

Tests should use independent expected values where feasible. An assertion that
reuses the production limit can pass when both the limit and behavior are wrong.
Temporarily breaking the relevant behavior is a useful way to check whether an
important regression test can detect it. The audit did this for admission,
version output, token scope, certificate installation and transport cleanup.

Coordinate concurrent tests with observed events and barriers. Arbitrary sleeps
and extreme socket settings can accidentally test machine speed or OS behavior.
When a fixture is wrong, fix the fixture while preserving the behavioral
assertion; do not weaken the product to make the test pass.

Add regression tests for fixes and hardening. Scale testing to risk: not every
documentation edit needs a new test, and mutation testing every trivial function
would be wasteful. After security or lifecycle changes, repeat the CLI and
embedding-app paths that could have broken.

## 7. Use reviewers to challenge the evidence

Claude and Amp/Oracle were useful outside reviewers. Their value came from
focused challenges: security and correctness, transport/lifecycle behavior,
compatibility, test quality and release readiness.

Give reviewers the actual implementation and relevant context. Ask what could
fail, what a test does not establish, and how a suspected issue can be reproduced.
Treat their findings as hypotheses until code inspection or executable evidence
supports them. Accept, adapt or reject findings with reasons.

Reviewing the tests is a distinct task from reviewing the code. A correct
implementation can have a weak test; a convincing test suite can hide an
untested boundary.

Use follow-up review for consequential fixes. Keep the final result readable:
scope, accepted findings, changes, evidence and remaining limits. Raw transcripts
and credentials do not belong in public documentation.

Review effort should follow risk. Several named reviewers are useful for a
security-sensitive transport package, but not a mandatory ceremony for every
small utility or release-text edit. A reviewer approving code is also distinct
from permission to publish it.

## 8. Automate the entire distribution path

A release is an outcome someone can install, not just a tag.

Maintain a changelog in the repository. Put high-level release notes on the
GitHub release rather than committing another release-notes document. Build
only the CLI for binary distribution; consumers obtain the library through its
package ecosystem.

Trigger Homebrew updates from release publication, with manual retry available.
The explicit preference here was to avoid an hourly cron. Keep tap maintenance
automated and tell the owner exactly which secret and permissions it needs.

Attach platform binaries and SHA256 files to the release. Build the intended
immutable source commit, verify version and revision metadata, check checksums,
and execute appropriate native smoke tests before publication. Downloads should
be usable without a compiler. State platform limits rather than shipping a
binary whose main feature is unsupported.

Make retries predictable. Skip identical published assets, upload missing ones
and refuse conflicting replacements. Separate build execution from publication
credentials. Use minimal workflow permissions and pinned action revisions.

Verify the actual release assets and Homebrew installation, not only the jobs
that produce them. Checksums detect changed bytes; they are not independent
signatures or proof of the source's trustworthiness.

## 9. Keep documentation useful and evidence dated

The README should explain what the product does, how to install it, the main
working flow, and how to embed it. Put important product capabilities before
validation details. Link deeper guides from a small documentation index.

Write Go package documentation, useful exported contracts and executable
examples. Document lifetimes, errors and ownership where they matter; do not
fill comments with restatements of the code.

Use short, concrete language and copyable commands. Apply the requested
`i-have-adhd` simplification approach when available. Keep operational guides
current and archive historical reviews so they do not compete with current
instructions. Keep working plans and agent-process clutter out of the public
docs by default. MIT was an explicit choice here; future projects should confirm
their own license rather than inherit it accidentally.

Separate instructions from evidence. Record the revision/date, commands,
tested behavior and limitations of a validation run. A successful local fixture
does not prove hosted compatibility, and yesterday's provider login does not
prove every later change. Reports should distinguish reproduced failures,
confirmed fixes and unverified possibilities.

## 10. Work autonomously without wasting the owner's time

Once a task and its delivery scope are authorized, carry it through implementation,
validation, documentation and the agreed release steps. Resolve ordinary choices
with judgment. Give short progress updates about findings, decisions and what
remains, rather than narrating every command.

Do not repeatedly ask for permission already given. When an action really needs
the owner—Touch ID, a provider consent screen, missing credentials, an irreversible
change—identify the exact action and why the owner is needed. Avoid letting
routine delivery turn into repeated confirmation or watching jobs together.

Use the existing workflow when it works. Here, the owner explicitly chose `main`;
that is a project instruction, not a universal ban on branches or worktrees.
Similarly, authority to release one project does not authorize publication of
another project merely because this document is used.

Finish with a concrete result: what changed, where it is available, what passed
and any material unfinished verification. Do not claim completion from a build,
HTTP 200 or reviewer approval alone.

## Reusable brief for another project

> Build this with the approach described in this document. Start with the real
> capability and keep its core usable from other applications. Prefer Go and the
> standard library where they fit; use established dependencies when they reduce
> maintenance or interoperability risk. Give me a practical CLI over the same
> implementation, sensible saved configuration, useful inspection commands and
> honest version/revision metadata. Make lifetimes, failures and security
> boundaries explicit. Add meaningful behavioral and integration tests, including
> failure paths; use race/fuzz checks and independent code/test review where the
> risk warrants them. Verify real integrations and the installed artifacts. Keep
> docs short, accurate and copyable. Automate CI, releases, binaries/checksums and
> package-manager updates appropriate to the project. Record evidence and limits.
> Continue within my authorized scope without repeated permission questions.
> Adapt the architecture and tooling to this product instead of copying otgo's
> features or imposing a fixed ceremony.

## Scope and provenance

This reference was approved on 2026-10-12 after building go-opentunnel. It does
not claim that every preference was followed perfectly. Documentation cleanup,
stronger regression assertions and release downloads were corrections that
informed the approach. Use the principles with judgment for the next product.

## Repository evidence

- [README](https://github.com/darron/go-opentunnel/blob/127cc68cfdfa3101abce70b96a671f3e76dde6b9/README.md): product flow, embedding, profile inventory, installation.
- [Package reference](https://github.com/darron/go-opentunnel/blob/127cc68cfdfa3101abce70b96a671f3e76dde6b9/docs/DESIGN.md): compatibility, public API and ownership contracts.
- [Observability](https://github.com/darron/go-opentunnel/blob/127cc68cfdfa3101abce70b96a671f3e76dde6b9/docs/OBSERVABILITY.md): optional adapter and private administrative listener.
- [Testing](https://github.com/darron/go-opentunnel/blob/127cc68cfdfa3101abce70b96a671f3e76dde6b9/docs/TESTING.md): local, integration, race, fuzz and live-testing distinctions.
- [Security and test audit](https://github.com/darron/go-opentunnel/blob/127cc68cfdfa3101abce70b96a671f3e76dde6b9/docs/SECURITY_AUDIT.md): reproduced findings and mutation evidence.
- [Auth review](https://github.com/darron/go-opentunnel/blob/127cc68cfdfa3101abce70b96a671f3e76dde6b9/docs/AUTH_SECURITY_REVIEW.md): both auth modes, real-provider checks and limits.
- [Verification](https://github.com/darron/go-opentunnel/blob/127cc68cfdfa3101abce70b96a671f3e76dde6b9/docs/VERIFICATION.md) and [live tests](https://github.com/darron/go-opentunnel/blob/127cc68cfdfa3101abce70b96a671f3e76dde6b9/docs/LIVE_TESTING.md): dated evidence.
- [Release binaries](https://github.com/darron/go-opentunnel/blob/127cc68cfdfa3101abce70b96a671f3e76dde6b9/docs/RELEASES.md) and [Homebrew](https://github.com/darron/go-opentunnel/blob/127cc68cfdfa3101abce70b96a671f3e76dde6b9/docs/HOMEBREW.md): distribution and retries.
- [Makefile](https://github.com/darron/go-opentunnel/blob/127cc68cfdfa3101abce70b96a671f3e76dde6b9/Makefile) and [CI](https://github.com/darron/go-opentunnel/blob/127cc68cfdfa3101abce70b96a671f3e76dde6b9/.github/workflows/ci.yml): repeatable checks.
