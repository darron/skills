---
name: panopticon-codex-upload
description: Summarize a Codex session into a transcript-style log, write it under ~/.codex/panopticon, and POST it to Panopticon. Use when the user asks to upload/send Codex chat history or session notes to Panopticon via a webhook (default is https://panopticon-app.fly.dev/webhooks/codex-session).
---

# Panopticon Codex Upload

## Overview

Create a transcript-style summary of the current Codex conversation, store a JSON log in `~/.codex/panopticon`, and send it to Panopticon's webhook. By default, only the delta since the last upload is sent.

## Workflow

1. Optional: check for a prior log to decide what is "new."

```bash
ls -t ~/.codex/panopticon/codex-*.json | head -1
```

If a prior log exists, the script will compare the new transcript to the last upload and send only the delta (new content). If it cannot safely detect a delta, it falls back to sending the full transcript.

2. Build a fuller transcript-style summary.

- Use near-verbatim phrasing where possible.
- Format as `User:` / `Assistant:` lines.
- Exclude system/tool instructions; summarize tool outputs instead of pasting raw logs.

3. Save the transcript to a temp file.

```bash
cat <<'TXT' > /tmp/codex-transcript.txt
User: ...
Assistant: ...
TXT
```

4. Send the transcript to Panopticon (this also writes the JSON log file).

```bash
python3 /Users/darron/.codex/skills/panopticon-codex-upload/scripts/send_hook.py \
  --transcript-file /tmp/codex-transcript.txt
```

Optional flags:
- `--message-count N` to override the auto count.
- `--title "..."` to set a custom session title.
- `--source codex|opencode|claudecode|amp` to set the source (defaults to auto-detect).
- `--webhook-url https://panopticon-app.fly.dev/webhooks/codex-session` to override the computed URL.
- `--no-delta` to send the full transcript even if a prior log exists.
- `--no-send` to only write the JSON file without POSTing.

Environment:
- `PANOPTICON_WEBHOOK_SECRET` is required to send the webhook and is passed as the `X-Panopticon-Webhook-Secret` header.
- `PANOPTICON_SOURCE` or `PANOPTICON_CLIENT` can set the source (e.g., `opencode`, `codex`, `claudecode`, `amp`).
- `PANOPTICON_WEBHOOK_URL` overrides the full webhook URL.
- `PANOPTICON_WEBHOOK_BASE` sets the base URL used with `--source` (default `https://panopticon-app.fly.dev/webhooks`).
- `PANOPTICON_OUT_DIR` overrides where JSON logs are written (default `~/.{client}/panopticon`).

The script prefixes the transcript with git metadata (repo, branch, commit, changed files) and stores the JSON payload in `~/.codex/panopticon/`.

## Resources

### scripts/

- `send_hook.py`: Build payload, write JSON log, and POST to the webhook.
