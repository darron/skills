# Optional Amp reviewer

Use only when the user requests Amp. Read the installed `amp-review` skill; follow its review-only boundary, local verification, repo-inspection, Oracle, finding-triage, and quiet-process guidance. Do not modify that skill or the user's Amp configuration. If it is unavailable, report the missing adapter rather than claim it ran.

## Preserve the selected mode and routing

Check the installed `amp --help` in the host lane before using flags. Resolve the user's selected mode from explicit request or trustworthy non-secret configuration/thread metadata. An interactive thread's selection is not proof of the mode of a new `amp -x` invocation. Pass the resolved mode explicitly; do not guess `medium`, switch to a cheaper mode, reset pins, add premium features, or continue the user's existing thread. If the intended mode cannot be determined, ask that one missing question before the Amp call while continuing other authorized council work.

The mode determines model, effort, prompt, and tools. Keep its existing model routing/pins. Record requested mode, any explicitly requested features, actual reported model(s)/family, and `unknown` where runtime metadata is unavailable. Do not infer exact identity from Amp's public default-mode table or an agent's self-description. A pin can fall back when unavailable; report any observed mismatch with a specifically required model.

Preserving Amp routing is not a subscription-billing guarantee. Depending on its connections and mode, Amp can use subscriptions, Amp credits, or configured keys. The user can explicitly authorize normal Amp credit usage as an exception to the council's subscription default. Honor that authorization from this request or earlier conversation without asking again; leave saved connections and billing settings alone. If no such exception exists, establish that the requested route fits the billing boundary before running it. Do not buy credits, enable top-ups, change connections, or use BYOK as a workaround. Ancillary tools may also incur Amp charges; include that limitation when it matters to an explicit spending boundary.

## Dispatch the review

For a repo review, start in the target repo root and give Amp the relevant plan/spec paths and local verification results, as `amp-review` requires. For an answer/document review without a repo, use the private run directory and supplied artifacts. Create a new review context; never use `threads continue` or `last`.

Use the council fresh-review contract: frozen question, source packet, complete identity-masked candidate texts in a recorded order, same rubric, and ranking/critique schema. Verify actual candidate inclusion before launch. Pin review access: for a comparable artifact-only ballot, explicitly prohibit extra repo/web/tool research; for code-aware review, allow authorized inspection and report that access. If Amp gains evidence unavailable to other reviewers, retain its extra findings as a supplemental code-aware critique, outside the common-evidence tally unless comparable access was predeclared and supplied to all reviewers.

Use argument arrays or a prompt file, never interpolate the user's question into shell code. A command shape supported by the installed CLI is:

```sh
amp -x --no-ide --mode "$council_amp_mode" \
  < "$council_amp_prompt" > "$council_amp_output" 2> "$council_amp_stderr"
```

Set these task variables from verified mode and private artifact paths with proper shell quoting. `--no-ide` avoids adding unrelated open editor content. Do not add `--dangerously-allow-all`, launch a remote orb, or alter permissions/configuration for convenience. A prompt-scoped read-only instruction is not OS isolation. Respect platform approval gates. Do not kill/restart a quiet review or repeat a token-costly call without the required user direction.

Keep the installed Amp Review workflow's Oracle consultation. Treat Oracle advice as nested critique returned by Amp; do not invent availability or success. Record whether it actually ran and any extra model identities reported. The final ranking is Amp's one ballot, attributed for family weighting to the verified main model that produced it; Oracle gets no separate ballot. Record the combined workflow and its dependencies rather than claiming statistical independence. If the final ranking cannot be attributed to a known main-model family, keep the review critique-only.

Preserve final output, stderr, process status, model/routing metadata when exposed, and any thread identifier. Plain `-x` output is enough for a critique; exact model telemetry may require a documented metadata mechanism. Do not claim a model was verified merely because a mode was selected. Validate a ranking exactly like other council ballots. An unknown-family review remains useful critique but cannot establish cross-family agreement. Triaging findings does not authorize implementing them during a question council; the parent incorporates verified findings into synthesis.

## References and validation boundary

The installed CLI's help was checked on October 24, 2026. No live Amp council or billing route was tested when adding this adapter; do not describe it as proven end to end.

- [Amp Dial](https://ampcode.com/docs/the-dial): per-thread mode, configured routing, model pins, and subscription/credit differences.
- [Amp execute mode](https://ampcode.com/docs/cli/execute-mode): fresh execute calls, stdin, final output, and execution behavior.
- [Amp models and subagents](https://ampcode.com/docs/models-and-subagents): main and supporting model roles.
