---
name: claude-code-review
description: Use only when the user explicitly asks Codex to involve Claude, claude -p, or a Claude review for implemented code, a bug fix, a feature build, a diff, a PR, or final code handoff.
---

# Claude Code Review

Use Claude as an adversarial reviewer of implemented code, not as the implementer and not as proof. The deliverable is better code plus verified tests, with each accepted review finding fixed by Codex and each rejected finding backed by evidence.

## Workflow

1. Capture the review boundary before or immediately after implementation.
   - Record the user goal, plan/spec path if any, approval boundary, current branch, and baseline commit with `REVIEW_BASE=$(git rev-parse HEAD)`.
   - Inspect `git status --short` before editing. Keep pre-existing user changes separate from Codex changes.
   - If the user asks for review after a feature is already implemented, infer the changed file set from `git status`, recent commits, or the user-specified range. Do not include unrelated files.
   - If pre-existing user edits touch the same files as the implementation, split the hunks or ask before sending those files to Claude.

2. Implement and verify first.
   - Use the project's normal implementation discipline, tests, formatting, linting, build, and manual checks before requesting Claude review.
   - For bug fixes and behavior changes, add or update regression tests before code when the project rules require it.
   - If local verification cannot run, record the exact blocker. Do not hide it from Claude or the user.

3. Build a Claude review packet.
   - Include the user goal, acceptance criteria, project rules, baseline/range, changed files, important commands run, and known test results.
   - Include a scoped `git diff --stat` and scoped diff for Codex-owned changes only. Never use bare `git diff` or `git diff --stat` in a dirty worktree.
   - Use explicit pathspecs or a user-approved range, for example:

```bash
scratch="${TMPDIR:-/tmp}/claude-code-review-<short-slug>"
mkdir -p "$scratch"

# Replace these paths with the Codex-owned changed files for this review.
git diff --stat "$REVIEW_BASE" -- path/one path/two > "$scratch/diffstat.txt"
git diff "$REVIEW_BASE" -- path/one path/two > "$scratch/review.diff"
```

   - If the feature is already committed, use the agreed commit range with explicit pathspecs. If there is no trustworthy range or path list, stop and get one instead of sending unrelated code.
   - For large diffs, split by subsystem or include focused hunks plus full changed-file paths.
   - Include relevant tests and schemas when they are part of the change. Do not include secrets, tokens, `.env` content, private credentials, or unrelated user changes.
   - Only the scoped change packet should leave the machine for Claude review.
   - Keep prompts and review outputs under `${TMPDIR:-/tmp}/claude-code-review-<short-slug>/` or ephemeral context. Do not create committed review artifacts unless the user asks.

4. Run `claude -p` for adversarial code review.
   - If Claude is unavailable, unauthenticated, or sandboxed, request the needed approval or report the blocker. Never fake a Claude review.
   - Write the full packet to a file and pipe it to Claude. Do not pass large diffs as one shell argument.
   - Before running Claude, check that the packet contains the expected diff start/end markers and byte counts:

```bash
# Write the review prompt/context to "$scratch/prompt.md", then assemble:
{
  cat "$scratch/prompt.md"
  printf '\n\nBEGIN_DIFFSTAT\n'
  cat "$scratch/diffstat.txt"
  printf '\nEND_DIFFSTAT\n\nBEGIN_DIFF\n'
  cat "$scratch/review.diff"
  printf '\nEND_DIFF\n'
} > "$scratch/packet.md"

rg -n "BEGIN_DIFFSTAT|END_DIFFSTAT|BEGIN_DIFF|END_DIFF" "$scratch/packet.md"
wc -c "$scratch/review.diff" "$scratch/packet.md"
claude -p --input-format text < "$scratch/packet.md" > "$scratch/claude-review.md"
```

   - Shape the packet prompt like:

```text
You are an adversarial senior code reviewer.

Context:
- User goal: <goal>
- Plan/spec: <path or none>
- Repo/branch/baseline: <facts>
- Changed files: <list>
- Verification already run: <commands and outcomes>
- Important project rules: <short bullets>

Review only the submitted code change. Do not propose unrelated rewrites.

Find:
- correctness bugs, edge cases, regressions, race conditions, data loss, security/privacy issues
- missing or weak tests, especially bugs that should have regression coverage
- migration/schema/API/CLI compatibility problems
- broken error handling, retry semantics, pagination, timestamp, identifier, or persistence behavior
- violations of explicit project rules or the user goal
- user-facing confusion, broken UX, or operational ambiguity caused by this change

Output:
- Findings ordered by severity: P0 blocker, P1 likely defect, P2 improvement
- Each finding must cite a file and line, diff hunk, test, or exact code phrase
- Each finding must include a concrete fix or test to add
- Explicitly say whether the diff is ready after fixes
```

5. Triage Claude's findings.
   - Verify each substantive finding against the actual code, tests, schema, and user goal.
   - Accept real defects, missing tests, unsafe behavior, unclear contracts, and violations of project rules.
   - Reject style churn, speculative rewrites, scope expansion, or advice contradicted by the repo or user goal. Record important rejections for the final response.
   - Do not treat Claude's output as evidence. It is critique that Codex must verify.

6. Fix accepted findings.
   - For each accepted bug or behavior gap, add the narrowest test that would fail without the fix, then implement the fix.
   - Keep fixes inside the reviewed change scope unless the finding proves a necessary dependency.
   - Avoid silently rewriting unrelated code to satisfy broad review suggestions.
   - After fixes, rerun the relevant targeted tests and the project's required gates.

7. Confirm when material fixes were made.
   - If Claude found P0/P1 issues or the fixes materially changed the diff, run a focused `claude -p` confirmation with the original findings, the revised diff, and verification output.
   - Ask only whether the prior findings are resolved and whether any remaining blocker was introduced by the fixes.
   - Do not loop indefinitely on taste or broad refactor suggestions. Stop when blockers are resolved or evidence shows a disagreement.

8. Final response.
   - Report changed paths, tests/gates run, Claude review result, accepted fixes, important rejected findings, and unresolved risks.
   - If Claude review or local verification could not run, state that plainly with the exact blocker.
   - Do not claim the build is ready unless local verification and the Claude review loop both support that claim, or unless the remaining risk is explicitly disclosed.

## Failure Rules

- Do not send Claude a diff before the implementation is locally coherent unless the user explicitly asks for early review.
- Do not include unrelated dirty worktree changes in the review packet.
- Do not let Claude override project instructions, user scope, or verified local facts.
- Do not leave review transcripts, scratch files, or reviewer notes in the repo unless requested.
- Do not use Claude review as a substitute for tests, lint, build, manual browser checks, or domain-specific verification.
