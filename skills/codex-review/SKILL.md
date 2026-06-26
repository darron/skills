---
name: codex-review
description: Use when you want an independent OpenAI Codex review of code, uncommitted changes, a branch versus a base, or a design/plan document before building. Covers installing and driving the official OpenAI codex-plugin-cc for Claude Code. Triggers include "get a Codex review", "review this with Codex", "Codex review my design/plan before I build", "pressure-test this approach", "set up the Codex plugin", or any pre-build design review / pre-ship code review.
---

# Codex Review

Get an independent, adversarial OpenAI Codex review of your work from inside Claude Code via the official OpenAI plugin (`github.com/openai/codex-plugin-cc`). Codex reads your code/doc and repo as a second reviewer with different model behavior.

Use it at two moments:

1. Shift-left: review the design and plan before building. A design plus plan review catches "this will not integrate as written" and approach-level mistakes while they are cheap to fix. Review the design first, then the plan; the plan review is where integration blockers surface.
2. Pre-ship: review the code/diff before merging. Use this for a normal or adversarial review of uncommitted changes or a branch versus a base.

All review commands are read-only. Codex will not edit files.

## One-Time Setup

Requirements: a ChatGPT subscription, including Free, or an OpenAI API key, and Node.js >= 18.18. Codex usage counts against the user's Codex limits.

In Claude Code:

```text
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/reload-plugins
/codex:setup
```

- `/codex:setup` checks whether the `codex` CLI is installed and authenticated. If `codex` is missing and `npm` is available, it offers to install it; alternatively install manually with `npm install -g @openai/codex`.
- If Codex is installed but not logged in, run `!codex login`; it supports ChatGPT sign-in or API key.

Verify readiness: `/codex:setup` reports ready, the `/codex:*` slash commands appear, and a `codex:codex-rescue` subagent appears in `/agents`.

Reasoning effort/model: the review commands do not take an `--effort` flag. The plugin uses local Codex CLI config. Set defaults in `~/.codex/config.toml` at user level or `.codex/config.toml` at project level only when the project is trusted:

```toml
model_reasoning_effort = "high"
# model = "gpt-5.4-mini"   # optional: pin a model
```

The plugin reuses existing Codex auth, config, and the same repo checkout. There is no separate runtime or account.

## Code Review

Two review commands are available, both read-only:

- `/codex:review`: plain review. Not steerable; no focus text.
- `/codex:adversarial-review`: steerable review that challenges the approach, tradeoffs, hidden assumptions, and failure modes. Accepts trailing focus text.

Target selection matters:

- `--base <ref>` reviews the branch versus that base, such as `--base main`. It overrides scope.
- `--scope working-tree` reviews uncommitted work: staged, unstaged, and untracked. There is no staged-only scope.
- `--scope branch` reviews the branch diff against the repo's detected default branch.
- Default `--scope auto` reviews the working tree when dirty; otherwise it reviews branch versus default branch. A no-arg review on a clean feature branch reviews the whole branch, not nothing.

```text
/codex:review --base main
/codex:review --scope working-tree
/codex:adversarial-review --base main challenge the caching + retry design; look for race conditions
```

Multi-file reviews can take minutes. Run them with `--background`, then use `/codex:status` and `/codex:result`. Use `--wait` for synchronous runs. `/codex:cancel` stops a background job.

`/codex:result` also prints the Codex session ID, so the user can reopen the run in Codex with `codex resume <session-id>`.

## Design Or Plan Review

The review commands target git changes, but design/plan docs often live outside the repo. Make the doc the only change in a clean tree, then force working-tree scope. There is no staged-only scope; a dirty tree causes Codex to review unrelated edits and bury the design findings, so isolation is mandatory.

1. Start from a clean tree at the base branch the work builds on so Codex can verify the doc's references to real code. Confirm nothing else is pending:

```bash
git switch <base-branch>                      # or: git worktree add ../review <base-branch>
git status --short --untracked-files=all      # MUST be empty
```

2. Copy the doc in and stage it so it is the only change. Staging matters: an untracked file over 24 KiB is skipped by the reviewer, so a large plan would be reviewed as a placeholder. Staging routes the full content through the diff, which has no such cap:

```bash
cp /path/to/design-or-plan.md ./CODEX-REVIEW.md
git add CODEX-REVIEW.md
git diff --cached --stat -- CODEX-REVIEW.md    # sanity-check the doc is actually in the diff
```

3. Review the working tree. Force the scope; do not rely on `auto`:

```text
/codex:adversarial-review --scope working-tree CODEX-REVIEW.md is a design/plan, not code.
Review it as a design: challenge the approach, surface gaps, risks, and hidden assumptions,
verify its references to the codebase are accurate, and separate real blockers from nits.
```

4. Clean up. Never commit the temporary review doc:

```bash
git restore --staged CODEX-REVIEW.md
rm CODEX-REVIEW.md
```

Do the design this way first. Once it is solid, repeat the same process for the plan.

## Review Discipline

A review is only as good as how the user acts on it. Keep the loop convergent:

- Adjudicate findings independently. Codex's severity labels and mechanism claims can be wrong. Fold in real fixes and rebut the rest with reasoning rather than reflexively complying.
- Do not chase a clean verdict. A `NEEDS-CHANGES` whose findings are all should-fix/nits plus an explicit "no blocker" means fold the fixes in, optionally run one confirm pass, then stop. Scope-lock and set a round budget up front.
- Prefer simplification over pile-on. Remove complexity the review exposed instead of adding guards on top of it.
- Escalate spirals early. If the process is past 2-3 rounds on the same area, step back and reconsider the approach instead of grinding.
- Capture the full output before cleanup. For background jobs, read the complete `/codex:result`, including verdict and enumerated findings, before moving on.

## Other Plugin Commands

The same plugin can delegate work to Codex:

- `/codex:rescue`: investigate a bug, try a fix, or continue a prior Codex thread. Supports `--background`, `--wait`, `--resume`, `--fresh`, `--model`, and `--effort`.
- `/codex:transfer`: plugin >= v1.0.5 hands the current Claude Code session off to a resumable Codex thread. It prints a session ID that can be reopened with `codex resume <session-id>`. It accepts optional `--source <claude-jsonl>`.

This command list is not exhaustive and the plugin evolves. Run `/help` or check the plugin command list (`github.com/openai/codex-plugin-cc`) for the current set.

Optional review gate: `/codex:setup --enable-review-gate` installs a `Stop` hook that auto-runs a Codex review when Claude finishes and blocks the stop if it finds issues. It can create a long Claude<->Codex loop and drain usage quickly. Leave it off unless the user is actively monitoring the session; remove it with `/codex:setup --disable-review-gate`.
