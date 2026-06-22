---
name: doc-review-merge
description: Merge document review feedback into one focused final document. Use when the user asks Codex to read a doc/spec/plan/proposal containing reviewer comments, review sections, notes from another agent, or inline critique, then accept/change/merge/reject the feedback and remove the review material so the document is coherent and ready for implementation or sharing.
---

# Doc Review Merge

## Goal

Produce a single focused document that integrates useful reviewer feedback without preserving the review transcript. Do not keep a separate "review", "Claude review", "Amp review", "Oracle notes", "comments", or similar section unless the user explicitly asks to preserve it.

## Workflow

1. Read the whole document before editing. Identify the document's primary purpose, intended audience, settled direction, and any explicit user constraints.
2. Locate review material. Treat sections labeled review/comments/feedback, quoted reviewer notes, inline TODOs, and agent-specific remarks as inputs to resolve, not content to preserve.
3. Triage each substantive comment against the document and known facts:
   - Accept if it corrects an error, clarifies intent, fills a real gap, or tightens implementation guidance.
   - Change if the reviewer is directionally right but the proposed wording or scope is wrong.
   - Merge if multiple comments make the same point.
   - Reject silently if it is pedantic, stale, contradicted by the user's direction, speculative, or would make the document less focused.
4. Edit the main document in place. Prefer concise wording and remove duplicated claims. Preserve the existing structure unless reorganization materially improves readability.
5. Remove resolved review material completely. The final document should read as authored content, not a debate transcript.
6. Verify consistency after edits. Check headings, summaries, recommendations, CLI/API names, acceptance criteria, examples, and cross-references for contradictions introduced by the merge.
7. Report only high-signal outcomes to the user: what changed, what was intentionally rejected if important, and any remaining uncertainty or follow-up.

## Editing Rules

- Keep the user's chosen direction authoritative. If review feedback conflicts with explicit user intent, preserve the user's intent and optionally clarify it in the document.
- Do not blindly accept reviewer claims. Validate claims against the document, codebase, or cited sources when available.
- Prefer replacing review prose with durable requirements, decisions, acceptance criteria, or implementation notes.
- Avoid "review says", "Claude noted", "Amp suggested", or similar attribution in the final document unless attribution itself matters.
- Remove obsolete alternatives after the document has chosen a direction.
- Keep implementation docs actionable: name commands, defaults, non-goals, safety constraints, and test expectations when relevant.
- If a comment exposes a real unresolved decision, convert it into a short open question or explicit deferred item rather than leaving the original comment.

## Final Response

Keep the user-facing summary brief:

- State that the review material was resolved and removed.
- Mention the most important accepted changes.
- Mention any important rejected/deferred points only when they affect future work.
- State what validation was run, or say if no validation was applicable.
