---
name: claude-doc-review
description: Use when the user explicitly asks Codex to involve Claude, claude -p, or a Claude review as an adversarial or second-agent reviewer for a document, plan, spec, proposal, PRD, or implementation plan, or to merge feedback from a Claude review into a final document.
---

# Claude Doc Review

Use Claude as an adversarial reviewer, not as an authority. The deliverable is a clean, buildable document whose accepted review feedback has been merged and whose rejected feedback has evidence behind the rejection.

## Skill Dependencies

- If `doc-review-merge` is available, use it before integrating reviewer feedback. If it is unavailable, follow the merge rules in this skill directly.
- If a planning or verification skill is available and its trigger matches the task, use it. If not, follow the project instructions and the verification checklist here.
- Never stall or silently skip this skill because a helper skill is absent; degrade to the explicit workflow below and tell the user what was unavailable.

## Workflow

1. Pin the target and current reality.
   - Identify the document path, user goal, approval boundary, and whether the user wants implementation to wait.
   - Read applicable project instructions, including `AGENTS.md` or repo-local equivalents.
   - If updating an existing plan, inspect the current branch enough to replace stale assumptions. Check `git status`, current branch/commit, changelog or recent commits, relevant code paths, schemas, tests, and docs.
   - Prefer generic terms such as "agent" when the design should work for any agent. Keep "Claude" only for the review tool itself or when the feature intentionally targets Claude.

2. Make the document reviewable first.
   - Bring the draft to the best state you can from local evidence before external review.
   - Make implementation plans actionable: files to edit, data contracts, command/API examples, tests, migrations, acceptance criteria, rollout/deferred work, and verification gates.
   - Do not send Claude a stale or obviously incomplete document and call the response the review.

3. Build a Claude review packet.
   - Include the full document content with line numbers when feasible. Use `nl -ba <doc>` or equivalent.
   - Include only task-relevant branch facts, known constraints, and project rules. Avoid unrelated secrets or private context.
   - For branch-aware plans/specs, include the document path and tell Claude to inspect the repo, git status, relevant diffs, untracked files, schemas, tests, and docs itself. Do not paste massive code diffs when Claude can read the checkout.
   - If the document is too large, include a table of contents plus the sections under review, but prefer full content for plans/specs.
   - Keep temporary prompts and review outputs under `${TMPDIR:-/tmp}/claude-doc-review-<short-slug>/` or in ephemeral conversation context. Do not create committed review artifacts unless the user asks.

4. Run the adversarial review with `claude -p`.
   - If Claude is not logged in or otherwise unavailable, report the blocker. If sandboxing blocks execution, rerun with escalation and request a scoped persistent prefix rule for `["claude", "-p"]` when appropriate. Never fake a Claude review.
   - Store review output in working notes or temporary context, not as a permanent review section inside the final document.
   - Use a prompt shaped like:

```text
You are an adversarial technical document reviewer.

Context:
- Document: <path>
- Full document content with line numbers: <included when feasible>
- Repo/branch/commit: <repo facts>
- User goal: <goal>
- Approval boundary: <whether implementation must wait>
- Important project rules: <short bullets>

Review only the document and its build-readiness. Do not rewrite it. Inspect the repo, git status, relevant diffs, untracked files, schemas, tests, and docs yourself when needed to check whether this plan matches the current branch. Do not require a pasted code diff.

Find:
- stale assumptions compared with the current branch
- contradictions, ambiguous contracts, or missing data semantics
- missing files, tests, migrations, commands, or acceptance criteria
- unsafe operational, security, privacy, or product behavior
- places where a named-agent assumption should be generic
- places where pagination, timestamps, identifiers, retries, error states, or persistence semantics are underspecified

Output:
- Findings ordered by severity: P0 build blocker, P1 likely defect, P2 improvement
- Each finding must cite a line, section, or exact phrase
- Each finding must state the concrete required document change
- End with: Ready to build? yes/no, with blockers if no
```

5. Merge the review.
   - Use `doc-review-merge` if available; otherwise apply these rules inline.
   - Accept comments that expose real correctness, buildability, ambiguity, or test-coverage issues.
   - Reject comments only with evidence from the repo, source document, project rules, or user goal.
   - If a comment depends on current code behavior, verify the real file/schema/output before editing.
   - Remove review scaffolding, reviewer names, "Claude said" prose, unresolved comment blocks, and raw review transcript text from the final document.

6. Confirm the merge with Claude.
   - Send Claude the original findings plus the revised document or focused diff.
   - Ask it to verify each prior finding is addressed or explicitly rejected with evidence.
   - Ask for remaining build blockers only; do not invite broad style churn unless the previous review was shallow.
   - If Claude finds a real blocker, fix it and run one more focused confirmation pass. If disagreement remains, preserve the evidence and ask the user only when it changes the build decision.

7. Verify locally before final response.
   - Search for stale agent-specific names when generic behavior was requested; replace `Hermes` in this example with the name the user called out: `rg -n "Hermes" <doc>`.
   - Search for review debris and placeholders, for example `rg -n "Claude said|adversarial review|review comment|TODO|TBD|placeholder" <doc>`.
   - Prefer `rg`; if unavailable, use the closest local equivalent such as `grep -R`.
   - Check `git diff -- <doc>` and `git status --short`.
   - For doc-only edits, do not run code gates unless the project requires them. If code, schemas, commands, generated assets, or examples changed, run the project-required gates.

8. Report and stop at the requested boundary.
   - Summarize changed paths, the strongest review findings that were merged, Claude's confirmation result, and local verification commands.
   - State any skipped gates and why.
   - If the user asked to approve before implementation, explicitly wait for approval. Do not start building.

## Failure Rules

- Do not treat Claude's output as evidence. Treat it as critique to verify.
- Do not paste massive code diffs into a branch-aware doc review when Claude can inspect the checkout.
- Do not accept broad rewrite suggestions that reduce specificity, remove tests, or hide operational semantics.
- Do not leave unrelated working-tree changes mixed into the document update.
- Do not claim "ready" until Claude confirmation and local verification both support that claim, or until you clearly state the remaining unresolved risk.
