---
name: opencode-review
description: Use when the user explicitly asks Codex to involve OpenCode, opencode, GLM, Z.AI, ZAI Coding Plan, or "Oh My OpenCode" for an adversarial review of code, a branch, a PR, a diff, a document, a plan, or launch readiness. Also use when Claude review is unavailable, Claude tokens are exhausted, the user wants a lower-cost routine reviewer, or the user wants to compare OpenCode/GLM against Claude and Amp.
---

# OpenCode Review

Use OpenCode as an independent reviewer with repo-local context, not as an authority and not as an implementer. This is the default low-cost review lane when Claude tokens are exhausted or when the user wants to test whether GLM is good enough for routine review. Keep Amp for expensive high-leverage cases such as docs, launch readiness, subtle architecture risk, or when the work is stuck.

The preferred local setup is OpenCode `1.17.10` using `zai-coding-plan/glm-5.2` at `high` variant through the direct `opencode run` path. Do not use the Oh My OpenCode `--command code-review` wrapper as the default path; it has repeatedly exited after dispatching background review IDs without returning findings that Codex can collect.

## Local Setup

- Preferred model: `zai-coding-plan/glm-5.2`
- Preferred variant: `high`
- Preferred invocation: direct GLM review without `--command`
- Optional diagnostic command: `code-review`, only when the user explicitly wants the wrapper tested or direct review is unavailable
- Optional orchestration: Oh My OpenCode's command attempts to invoke three `@code-review` subagents and correlate findings, but this is not reliable enough to be the default.
- Known active worker agent: `Sisyphus - ultraworker`. Do not rely on it for review unless the `code-review` command is unavailable or the command wrapper fails to return findings; it is more permissive than a reviewer should be.
- Known wrapper failure: `--command code-review` may try an OpenAI plan subagent, then exit after dispatching background `@code-review` sessions that are cancelled, produce zero tokens, or are left as background IDs that Codex cannot collect. A dispatch log without a severity-ranked findings section is not a completed review.
- Direct review behavior observed in practice: direct `opencode run --dir <repo-root> --model zai-coding-plan/glm-5.2 --variant high "<review guidance>"` is more likely to return actionable findings than the wrapper. It can still hang or emit investigation logs without a final verdict. Count it complete only when it prints severity-ranked findings or an explicit no-findings recommendation.

Verify the local boundary when behavior is unclear:

```bash
opencode --version
opencode models zai-coding-plan
opencode agent list
test -f ~/.config/opencode/command/code-review.md
test -f ~/.config/opencode/agent/code-review.md
```

If Codex sandboxing blocks OpenCode because it writes logs or state under `~/.local/share/opencode`, rerun with escalation. Never fake an OpenCode review.

## Workflow

1. Pin the review boundary.
   - Identify the user goal, repo root, branch, dirty worktree state, baseline/range, approval boundary, and whether there is a plan/spec document.
   - Inspect `git status --short --untracked-files=all` before the review. Keep unrelated user changes out of the review scope.
   - If a plan/spec exists, include its path and tell OpenCode to read it. For implementation review, this gives intent, not just diff shape.
   - Do not include secrets, tokens, `.env` content, unrelated private context, or unrelated user changes in the prompt.

2. Verify locally before review when work is implemented.
   - Run practical project tests, lint, build, and manual checks before asking OpenCode.
   - If verification cannot run, record the exact blocker and include it in the prompt.
   - Do not use OpenCode as a substitute for local verification.

3. Run OpenCode from the repo root.
   - Use the direct GLM review path by default:

```bash
opencode run \
  --dir <repo-root> \
  --model zai-coding-plan/glm-5.2 \
  --variant high \
  "<review guidance>"
```

   - Do not pass `--dangerously-skip-permissions` for review.
   - Do not ask OpenCode to edit files unless the user explicitly asks for OpenCode implementation.
   - A successful run must return actual findings or an explicit no-findings recommendation. If it only prints setup, diff excerpts, background IDs, or "waiting for completion" text and exits, treat the review as failed.
   - If a direct run is long and output is quiet, wait. When the user says reviews may take 10 minutes or more, allow that much time before judging the run. If the process is alive but only emits tool chatter, diff excerpts, or partial investigation and never reaches a findings/recommendation section, treat it as unavailable rather than as a completed review.
   - Do not start duplicate OpenCode runs unless the previous run has exited, clearly failed, or the user explicitly wants a comparison or retry.
   - If code changes while a review is running, mark that output stale for readiness. Re-run against the refreshed diff before treating the review as final.

   Optional wrapper diagnostic, not the default:

```bash
opencode run \
  --dir <repo-root> \
  --model zai-coding-plan/glm-5.2 \
  --variant high \
  --command code-review \
  "<same review guidance>"
```

   Use this only when the user explicitly asks to test the wrapper or when diagnosing OpenCode setup. If the wrapper only returns background IDs, dispatch logs, or "waiting" text, do not count it as a review and do not wait for background notifications Codex cannot collect.

4. Use a repo-inspection prompt.

```text
Review the current branch for PR readiness. Do not edit files. Do not ask me questions.
Inspect the repo, git status, diffs, untracked files, tests, docs, and plan/spec yourself;
do not require a pasted diff. Review only this change and do not propose unrelated rewrites.

User goal: <goal>
Plan/spec document: <path or none; read it if present>
Repo/branch/baseline: <facts>
Changed-file hints: <list, if known>
Verification already run: <commands and outcomes, or blocker>
Known constraints: <project rules, launch boundary, risk areas>

Focus on correctness bugs, schema/API/CLI compatibility, migrations, auth/security/privacy,
pagination/cursor behavior, timestamp/identifier semantics, tests, docs/skill accuracy,
user-facing confusion, and launch risk.

Return findings first, ordered by severity:
- P0 blocker
- P1 likely defect
- P2 improvement

Each finding must cite a file and line, diff hunk, test, or exact code phrase.
Each finding must include a concrete fix or test to add.
End with an explicit ready/not-ready recommendation.
```

5. Triage OpenCode's findings.
   - Verify each substantive finding against the actual code, tests, schema, docs, and user goal.
   - Accept real defects, missing tests, unsafe behavior, unclear contracts, and project-rule violations.
   - Reject style churn, broad rewrites, hallucinated files, scope expansion, and speculation contradicted by local evidence.
   - Treat OpenCode/GLM output as critique, not proof.

6. Fix and verify.
   - For accepted code findings, add the narrowest regression test when appropriate, implement the fix, then rerun targeted tests and required project gates.
   - For docs/plans, merge accepted feedback into the document and remove review debris.
   - If fixes materially change the branch or OpenCode found P0/P1 issues, consider one focused confirmation pass. Do not loop on taste.
   - If the optional command wrapper was tried, compare the wrapper failure and direct-review quality in the final response. If the direct review hung or produced no final findings, state that OpenCode was unavailable for this pass.

7. Final response.
   - Report the OpenCode command shape, accepted fixes, important rejected findings, verification commands, and unresolved risk.
   - If OpenCode could not run, state the exact blocker.
   - Do not claim readiness from OpenCode alone; local verification still matters.

## Parallel Reviewer Bakeoff

Use this mode when the user wants to compare GLM against Claude and Amp, or when deciding whether OpenCode/GLM is good enough to use when Claude tokens are exhausted.

Default reviewer roles:

- OpenCode/GLM: routine review, Claude-token fallback, and cheap repeated passes.
- Claude: normal high-quality reviewer when tokens are available.
- Amp: expensive reviewer for docs, plan quality, launch risk, hard debugging, or when Claude/OpenCode disagree on a consequential issue.

1. Use the same pinned review boundary for every reviewer.
   - Same repo root, baseline/range, changed-file hints, plan/spec path, verification results, and known constraints.
   - Keep reviewer prompts equivalent so output differences reflect model/reviewer behavior rather than different instructions.

2. Run independent reviewers in parallel when the environment permits.
   - Claude lane: follow `claude-code-review` or `claude-doc-review`.
   - Amp lane: follow `amp-review`.
   - OpenCode lane: run the direct OpenCode command in this skill.
   - Store scratch prompts and outputs under separate temporary paths such as `${TMPDIR:-/tmp}/review-bakeoff-<slug>/claude`, `/amp`, and `/opencode`; do not commit review artifacts unless requested.

3. Compare reviewer quality, not just verdicts.
   - Track which findings are true positives, false positives, duplicates, style-only suggestions, or unverifiable claims.
   - Give extra weight to findings with accurate file/line citations, reproducible failure modes, and concrete tests.
   - Record wrapper behavior separately from direct-review quality. Background session IDs are orchestration telemetry, not findings.
   - Record whether GLM found issues the others missed, whether it hallucinated, and whether its fixes fit the codebase.

4. Converge on code, not on reviewer agreement.
   - Fix verified defects even if only one reviewer found them.
   - Reject findings contradicted by local evidence even if multiple reviewers repeat them.
   - Do not keep asking reviewers until one gives the desired answer.

## Failure Rules

- Do not paste massive diffs by default; let OpenCode inspect the checkout.
- Do not include unrelated dirty worktree changes in the review packet.
- Do not pass secrets or `.env` contents.
- Do not use `--dangerously-skip-permissions` for review.
- Do not start with the `--command code-review` wrapper unless the user explicitly asks to test wrapper behavior.
- Do not let OpenCode edit files unless explicitly requested.
- Do not claim GLM is good or bad from one run. Judge it by verified true/false findings across comparable review tasks.
- Do not count an OpenCode review as completed unless the final output contains findings/recommendation text. Background-session dispatch alone is not evidence of review.
- Do not treat stale output as a final gate after local fixes land; refresh the diff and rerun the review if the OpenCode lane is part of the completion criteria.
