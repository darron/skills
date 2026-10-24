# Optional Amp reviewer

Use only when the user requests Amp. Read the installed `amp-review` skill; follow its review-only boundary, local verification, repo-inspection, Oracle, finding-triage, and quiet-process guidance. Do not modify that skill or the user's Amp configuration. If it is unavailable, report the missing adapter rather than claim it ran.

## Preserve the selected mode and routing

Check the installed `amp --help` in the host lane before using flags. Resolve the user's selected mode from explicit request or trustworthy non-secret configuration/thread metadata. An interactive thread's selection is not proof of the mode of a new `amp -x` invocation. Pass the resolved mode explicitly; do not guess `medium`, switch to a cheaper mode, reset pins, add premium features, or continue the user's existing thread. If the intended mode cannot be determined, ask that one missing question before the Amp call while continuing other authorized council work.

The mode determines model, effort, prompt, and tools. Keep its existing model routing/pins. Record requested mode, any explicitly requested features, actual reported model(s)/family, and `unknown` where runtime metadata is unavailable. Do not infer exact identity from Amp's public default-mode table or an agent's self-description. A pin can fall back when unavailable; report any observed mismatch with a specifically required model.

For a user-selected custom mode, `amp threads export <known-thread-id>` can expose the mode key under `meta.threadAgent.pluginAgentModeKey`, configured model/effort under its definition, and actual main-model identity under assistant-message `usage.model`. Inspect only needed metadata from an authorized relevant thread, not unrelated message content. Use the resolved mode for a new invocation; never reuse that thread as the reviewer. Verify the new run's identity again. `amp tools list` returned zero tools during the trial while actual execution exposed tools, so that empty listing alone does not establish Oracle unavailability.

Preserving Amp routing is not a subscription-billing guarantee. Depending on its connections and mode, Amp can use subscriptions, Amp credits, or configured keys. The user can explicitly authorize normal Amp credit usage as an exception to the council's subscription default. Honor that authorization from this request or earlier conversation without asking again; leave saved connections and billing settings alone. If no such exception exists, establish that the requested route fits the billing boundary before running it. Do not buy credits, enable top-ups, change connections, or use BYOK as a workaround. Ancillary tools may also incur Amp charges; include that limitation when it matters to an explicit spending boundary.

## Dispatch the review

For a repo review, start in the target repo root and give Amp the relevant plan/spec paths and local verification results, as `amp-review` requires. For an answer/document review without a repo, use the private run directory and supplied artifacts. Create a new review context; never use `threads continue` or `last`.

Use the council fresh-review contract: frozen question, source packet, complete identity-masked candidate texts in a recorded order, same rubric, and ranking/critique schema. Verify actual candidate inclusion before launch. Pin review access: for a comparable artifact-only ballot, explicitly prohibit extra repo/web/tool research; for code-aware review, allow authorized inspection and report that access. If Amp gains evidence unavailable to other reviewers, retain its extra findings as a supplemental code-aware critique, outside the common-evidence tally unless comparable access was predeclared and supplied to all reviewers.

Use argument arrays or a prompt file, never interpolate the user's question into shell code. A command shape supported by the installed CLI is:

```sh
amp -x --no-ide --mode "$council_amp_mode" --visibility private \
  --plugin-ready-timeout 10 --stream-json \
  < "$council_amp_prompt" > "$council_amp_output" 2> "$council_amp_stderr"
```

Set these task variables from verified mode and private artifact paths with proper shell quoting. `--no-ide` avoids adding unrelated open editor content. Do not add `--dangerously-allow-all`, launch a remote orb, or alter permissions/configuration for convenience. A prompt-scoped read-only instruction is not OS isolation. Respect platform approval gates. Do not kill/restart a quiet review or repeat a token-costly call without the required user direction.

Keep the installed Amp Review workflow's Oracle consultation. Current Amp can implement "ask Oracle" as a Task reviewing subagent using the thread's same model/effort; do not promise a separate model merely from the Oracle name. Permit that bounded review delegation and its necessary discovery, require the same complete evidence/candidates, and prohibit extra research or recursive delegation. Treat its advice as nested critique returned by Amp; do not invent availability or success. Record the actual mechanism, whether it ran, and any extra model identities reported. Inspect actual nested tool input for complete packet inclusion when available. The final ranking is Amp's one ballot, attributed for family weighting to the verified main model that produced it; Oracle gets no separate ballot. Record the combined workflow and its dependencies rather than claiming statistical independence. If the final ranking cannot be attributed to a known main-model family, keep the review critique-only.

Preserve the JSONL stream, stderr, process status, model/routing metadata when exposed, and any thread identifier. Extract the final assistant text or successful result's text, then parse its review JSON; do not confuse the event envelope with the ballot. Check process exit and result error status. The stream also exposes tool calls for access/Oracle checks. Plain `-x` output is enough for a critique, but use documented metadata to verify models. `amp threads usage <thread-id> --details` reports Agent/Task model routing and displayed credit cost; a list-price estimate is not a charge. Do not claim a model was verified merely because a mode was selected. Validate a ranking exactly like other council ballots. An unknown-family review remains useful critique but cannot establish cross-family agreement. Triaging findings does not authorize implementing them during a question council; the parent incorporates verified findings into synthesis.

## References and validation boundary

An end-to-end synthetic artifact-only trial passed on October 24, 2026: two inexpensive native authors and one Claude Haiku author, then fresh native/Haiku/Amp reviewers and parent synthesis. All three ballots were valid, with different rankings. Amp's main review and nested Task reviewing subagent both reported GPT-6.1 Sol; the parent verified complete evidence/candidate inclusion in the actual nested prompt. The usage report showed subscription routing and $0 Amp credit cost for that run. This validates one run's integration, not future billing, a separate-model Oracle route, statistical independence, or general answer quality.

- [Amp Dial](https://ampcode.com/docs/the-dial): per-thread mode, configured routing, model pins, and subscription/credit differences.
- [Amp execute mode](https://ampcode.com/docs/cli/execute-mode): fresh execute calls, stdin, final output, and execution behavior.
- [Amp models and subagents](https://ampcode.com/docs/models-and-subagents): main and supporting model roles.
- [Amp tools](https://ampcode.com/docs/tools): current Task-based reviewing/Oracle mechanism and same-model behavior.
