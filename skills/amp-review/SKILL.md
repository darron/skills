---
name: amp-review
description: Use when the user explicitly asks Codex to involve Amp, amp, amp -x, Amp Code, or Oracle for an adversarial review of code, a branch, a PR, a diff, a document, a plan, or launch readiness.
---

# Amp Review

Use Amp as an independent reviewer with repo-local context, not as an authority and not as an implementer. The useful pattern is to let Amp inspect the same workspace instead of pasting large diffs into the prompt.

## Workflow

1. Pin the review boundary.
   - Identify the user goal, current repo, branch, dirty worktree state, approval boundary, and whether there is a plan/spec document.
   - If a plan/spec exists, include its path in the Amp prompt and tell Amp to read it. For code reviews, this gives Amp the intended behavior, not just the diff.
   - Do not include secrets, tokens, `.env` content, unrelated private context, or unrelated user changes in the prompt.

2. Verify locally before review when the work is implemented.
   - Run the project-required tests, lint, build, and manual checks that are practical before asking Amp.
   - If verification cannot run, record the exact blocker and include it in the prompt.
   - Do not use Amp as a substitute for local verification.

3. Run Amp from the repo root.
   - Prefer `amp -x` / `amp --execute` so the CLI waits for final output.
   - If the sandbox blocks Amp, rerun with escalation and request a persistent prefix rule for `["amp", "-x"]` when appropriate.
   - Do not kill and restart a long-running Amp review just because output is quiet; Amp may be inspecting files, running tests, or waiting on Oracle.
   - Do not start duplicate Amp runs unless the user explicitly asks; Amp usage costs tokens.

4. Use a repo-inspection prompt.

```text
Review the current branch for PR readiness. Do not edit files. Do not ask me questions. Inspect the repo, git status, diff, untracked files, tests, docs, and plan/spec yourself; do not require a pasted diff.

User goal: <goal>
Plan/spec document: <path or none>
Verification already run: <commands and outcomes, or blocker>
Known constraints: <project rules, launch boundary, relevant risk areas>

Focus on correctness bugs, schema/API/CLI compatibility, migrations, auth/security/privacy, pagination/cursor behavior, timestamp/identifier semantics, tests, docs/skill accuracy, user-facing confusion, and launch risk.

Please ask the Oracle for an adversarial second opinion on the riskiest parts before finalizing.

Return findings first, ordered by severity with file/line references where possible. Include explicit pass/fail recommendation for launch.
```

For document-only review, replace the focus list with build-readiness, stale assumptions, ambiguity, missing acceptance criteria, missing files/tests/migrations/commands, and named-agent assumptions that should be generic.

5. Triage Amp's findings.
   - Use the code-review receiving discipline when the output is about code. Verify each substantive finding against the actual repo before accepting it.
   - Accept real defects, missing tests, unsafe behavior, unclear contracts, and project-rule violations.
   - Reject style churn, broad rewrites, and speculation contradicted by local evidence.
   - Treat Oracle output as critique surfaced through Amp, not as proof.

6. Fix and verify.
   - For accepted code findings, add the narrowest regression test when appropriate, implement the fix, then rerun targeted tests and project gates.
   - For docs/plans, merge accepted feedback into the document and remove review debris.
   - If fixes materially change the branch or Amp found P0/P1 issues, consider one focused confirmation pass; do not loop on taste.

7. Final response.
   - Report Amp/Oracle result, accepted fixes, important rejected findings, verification commands, and unresolved risk.
   - If Amp could not run, state the exact blocker. Never fake an Amp review.

## Failure Rules

- Do not paste massive diffs by default; let Amp inspect the checkout.
- Do not ask Amp to edit files unless the user explicitly wants Amp to implement.
- Do not send secrets or unrelated dirty worktree changes.
- Do not claim readiness from Amp alone; local verification still matters.
- Do not restart token-costly runs without user direction.
