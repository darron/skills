---
name: pi-ollama-qwen
description: Use when the user explicitly asks Codex to involve Pi, pi, Ollama, local Qwen, local models, or a local-only code review lane for code, branches, diffs, documents, plans, or reviewer bakeoffs. Also use when Claude tokens are exhausted and the user wants a no-cloud comparison reviewer.
---

# Pi Ollama Qwen

Use Pi as a local-only review harness backed by Ollama/Qwen. Treat it as a cheap secondary reviewer, not an authority and not an implementer. Pi has no built-in sandbox, so run it read-only by default.

## Default Model

Prefer the local coding tag when available:

```text
qwen3.6:35b-a3b-coding-nvfp4
```

Pi may warn that this exact model is not in its registry and then continue with a custom model id. That is acceptable if the command completes. If `pi --provider ollama --list-models qwen3.6` shows only the registry-visible model, use that fallback directly instead of spending time on a missing coding tag:

```text
qwen3.6:latest
```

## Preflight

Verify the local boundary before a review:

```bash
command -v pi
ollama ps
pi --provider ollama --list-models qwen3.6
git status --short --untracked-files=all
```

If `pi` cannot see Ollama, ask the user to run `ollama launch pi --model qwen3.6:35b-a3b-coding-nvfp4` once, then retry. `ollama ps` only shows currently loaded models; trust Pi's model listing for whether a tag is usable. Never fake a Pi review.

## Read-Only Review

Run Pi from the repo root with only read-only tools:

```bash
pi --provider ollama \
  --model qwen3.6:35b-a3b-coding-nvfp4 \
  --offline --no-session \
  --no-context-files --no-skills --no-extensions --no-prompt-templates \
  --tools read,grep,find,ls \
  -p "<review prompt>"
```

Use `--no-context-files` by default so project-local instructions do not steer the independent reviewer. If project rules are essential, inspect them yourself and summarize the relevant constraints in the prompt instead.

Pi can run silently for several minutes while the local model works. Keep waiting while the process is alive; do not restart or launch a duplicate review just because there is no streaming output.

## Prompt Template

```text
You are a strict read-only code reviewer. Do not edit files. Use only read, grep, find, and ls.

User goal: <goal>
Repo/branch/baseline: <facts>
Changed files: <list>
Diff or plan/spec context: <inline summary or @temp-diff-file if supplied>
Verification already run: <commands and outcomes, or blocker>
Known constraints: <scope, project rules, launch boundary, risk areas>

Review only this change. Focus on correctness bugs, regressions, security/privacy issues,
missing tests, stale docs, confusing user-facing behavior, and launch risk.

Return findings first, ordered by severity:
- P0 blocker
- P1 likely defect
- P2 improvement

Each finding must cite a file and line, diff hunk, test, or exact code phrase.
If there are no actionable findings, say that explicitly.
End with a ready/not-ready recommendation.
```

For diff-heavy reviews, gather the diff outside Pi and either paste the relevant hunks into the prompt or pass a temporary diff file as an `@file` argument. Pi cannot run `git diff` when restricted to `read,grep,find,ls`. If generated assets would dominate the diff, exclude them from the temp diff and mention that exclusion explicitly in the prompt.

## Bakeoff Use

Use this lane when comparing local Qwen against Claude, Amp, or OpenCode/GLM:

- Keep the same review boundary for every reviewer.
- Keep prompts equivalent so output differences reflect reviewer quality.
- Score true positives, false positives, hallucinated paths, missed defects, citation quality, and fix usefulness.
- Expect useful broad risk hints and some exact-code misses. Verify database driver behavior, locking/concurrency claims, nullable/empty-string handling, and framework-specific assumptions directly against the repo before accepting them.
- If the branch changes while Pi is running, mark the result stale for readiness and rerun only if the local lane still matters.
- Do not claim Qwen is good or bad from one run. Judge it across comparable tasks.

## Failure Rules

- Do not enable `bash`, `edit`, or `write` for routine review.
- Do not use Pi to modify files unless the user explicitly asks and you have a separate sandbox plan.
- Do not include secrets, `.env` contents, unrelated private context, or unrelated dirty worktree changes in the prompt.
- Do not trust a finding until it is checked against the actual repo.
- Do not count a Pi run as completed unless it returns findings or an explicit no-findings recommendation.
- Do not let a stale Pi run block completion after fixes land unless the user specifically wants another local-only pass.
