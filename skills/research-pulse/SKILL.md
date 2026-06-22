---
name: research-pulse
description: Manage advisor-aware Converge Research Pulse workflows through the supported `converge` CLI path, wait for completion, manage share feeds, and write Markdown or JSON artifacts into the workspace. Use when Codex needs to manage Advisors, run a Research Pulse for a user, export results to files, inspect or fetch account share feeds, reuse config profiles, or drive Research Pulse from an agent workflow without calling internal Go packages directly.
---

# Research Pulse

Use this skill to run Research Pulses through the external CLI and API contract instead of reaching into internal Go packages or HTML endpoints.

## Workflow

1. Ensure the CLI path exists.

- In this repo, prefer `./bin/converge`.
- If the binary is missing, run `make build-cli`.
- Outside this repo, prefer a `converge` binary already on `PATH`.

2. Resolve auth, base URL, and defaults before submitting a run.

- Prefer `--config` and `--profile` when a reusable config exists.
- Otherwise use `--base-url` and `--api-key`, or the `CONVERGE_BASE_URL` and `CONVERGE_API_KEY` env vars.
- If selectors are not already known, run `converge pulse models` first.
- Prefer selectors with stronger recent reliability and lower average latency when the task benefits from fast turn time.
- Use `converge pulse models --json` when an agent needs machine-readable selector stats; each item includes recent `reliability_percent`, `avg_latency_ms`, `p50_latency_ms`, `p95_latency_ms`, and grouped/daily breakdowns from the same 7-day stats shown in the Providers UI.
- Read [references/config.md](references/config.md) for config discovery, precedence, and example profiles.

3. Inspect or manage Advisors when the task needs perspective control.

- In advisor-capable Converge builds, prefer the top-level `converge advisors` command family for reusable council lenses.
- Start with `converge advisors templates` or `converge advisors list` when you need to see available options.
- Use `converge advisors create` or `converge advisors update` with `--instructions-file` when the instructions are more than a short line.
- Reuse stored advisors or templates in run commands instead of inlining large instruction blocks into shell arguments.
- If the connected build does not expose advisor CLI support yet, say so plainly and continue with plain Research Pulse commands or existing web-managed advisors.

4. Stage the question in the workspace.

- If the user already has a question file, use it with `--question-file`.
- Otherwise write the question into a workspace file such as `.codex/tmp/research-pulse-question.md` and point the CLI at that file.
- Keep secrets out of workspace files.

5. Run the pulse through the CLI.

- For a new run that should finish in this turn, use `converge pulse run --wait`.
- Pass `--output` for Markdown, `--json-output` for full JSON, or both.
- Add `--model` and `--synth-model` only when overriding config defaults.
- In advisor-capable builds, use `--advisor '<selector>=advisor:<id>'` or `--advisor '<selector>=template:<key>'` for explicit assignments.
- In advisor-capable builds, `--use-saved-advisors` is the explicit opt-in path for reusing saved advisor defaults on a direct CLI run.
- When advisors are applied, verify that the CLI echoes the resolved advisor mapping before treating the run input as final.
- Leave progress enabled unless the user explicitly wants quiet output.

6. Reuse existing runs when appropriate.

- Use `converge pulse watch <run-id>` to wait on an existing run.
- Use `converge pulse export <run-id>` to fetch artifacts after completion.

7. Report the outcome precisely.

- If Markdown or JSON files were written, report the exact paths.
- Exit code `2` means partial failure with a usable result; explain that clearly instead of treating it like a hard failure.
- Exit code `1` means request, auth, config, or terminal failure without a usable final result.

8. Use supported share-feed commands for published shares.

- Use `converge feed status` to inspect whether the account feed exists, is enabled, and has password protection.
- Use `converge feed enable`, `converge feed disable`, `converge feed set-password`, `converge feed clear-password`, and `converge feed rotate` for management.
- Use `converge feed urls` to print Atom/RSS/JSON URLs. URL discovery requires `api.full` or a browser session; a `shares.feed`-only key can read an already-known URL but cannot discover it.
- Use `converge feed fetch --format atom|rss|json` to fetch or validate the feed. Add `--url` when operating with a least-privilege `shares.feed` key.
- Use `converge share markdown <slug>` to fetch a public share as Markdown. Do not scrape the HTML page.
- Feed entries are intentionally link-only. Fetch the linked share page, or `converge share markdown <slug>`, for the complete public artifact.
- If the connected CLI build does not expose `feed` or `share markdown`, say so plainly and fall back only to existing public share URLs.

## Command Patterns

Discover selectors:

```bash
./bin/converge pulse models --config <path> --profile <name>
```

Discover selectors plus machine-readable recent stats:

```bash
./bin/converge pulse models --config <path> --profile <name> --json
```

Submit a run and wait for Markdown plus JSON:

```bash
./bin/converge pulse run \
  --wait \
  --question-file <workspace-question-path> \
  --output <workspace-result-path>.md \
  --json-output <workspace-result-path>.json \
  --config <path> \
  --profile <name>
```

Override models for a one-off run:

```bash
./bin/converge pulse run \
  --wait \
  --question-file <workspace-question-path> \
  --model gpt-5-mini \
  --model claude-sonnet-4 \
  --synth-model gpt-5-mini \
  --output <workspace-result-path>.md
```

Advisor-aware commands, when supported by the connected Converge build:

```bash
./bin/converge advisors templates
```

```bash
./bin/converge advisors create \
  --name "Contrarian" \
  --description "Looks for likely failure modes." \
  --instructions-file <workspace-advisor-path>.md
```

```bash
./bin/converge pulse run \
  --wait \
  --question-file <workspace-question-path> \
  --council \
  --model gpt-5 \
  --model claude-sonnet-4 \
  --advisor 'gpt-5=template:contrarian' \
  --advisor 'claude-sonnet-4=advisor:adv_123' \
  --output <workspace-result-path>.md
```

```bash
./bin/converge pulse run \
  --wait \
  --question-file <workspace-question-path> \
  --council \
  --model gpt-5 \
  --model claude-sonnet-4 \
  --use-saved-advisors \
  --output <workspace-result-path>.md
```

```bash
./bin/converge pulse helper start \
  --message "Help me refine this question." \
  --model gpt-5 \
  --model claude-sonnet-4 \
  --council
```

Wait on an existing run:

```bash
./bin/converge pulse watch <run-id> \
  --output <workspace-result-path>.md \
  --json-output <workspace-result-path>.json
```

Export artifacts for a completed run:

```bash
./bin/converge pulse export <run-id> \
  --output <workspace-result-path>.md \
  --json-output <workspace-result-path>.json
```

Inspect account share-feed status:

```bash
./bin/converge feed status --config <path> --profile <name>
```

Enable the share feed:

```bash
./bin/converge feed enable \
  --title "Research Pulse Shares" \
  --description "Published Converge Research Pulse outputs." \
  --config <path> \
  --profile <name>
```

Print feed URLs:

```bash
./bin/converge feed urls --config <path> --profile <name>
```

Fetch a feed with URL discovery:

```bash
./bin/converge feed fetch --format atom --config <path> --profile <name>
```

Fetch a known feed URL with a least-privilege key:

```bash
./bin/converge feed fetch \
  --format json \
  --url <feed-url> \
  --base-url <converge-base-url> \
  --api-key <shares.feed-token>
```

Rotate the feed URL only after explicit confirmation:

```bash
./bin/converge feed rotate --confirm --config <path> --profile <name>
```

Fetch a public share as Markdown:

```bash
./bin/converge share markdown <share-slug> --output <workspace-share-path>.md
```
