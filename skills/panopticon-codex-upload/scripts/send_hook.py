#!/usr/bin/env python3
import argparse
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path
from urllib import request


def run_git(args, cwd):
    try:
        out = subprocess.check_output(["git"] + args, cwd=cwd, stderr=subprocess.DEVNULL)
        return out.decode().strip()
    except Exception:
        return ""


def now_iso():
    now = datetime.datetime.now(datetime.UTC).replace(microsecond=0)
    return now.isoformat().replace("+00:00", "Z")


def timestamp_id():
    return datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")


def count_messages(text):
    count = 0
    for line in text.splitlines():
        if line.startswith("User:") or line.startswith("Assistant:"):
            count += 1
    return count


def normalize_source(value):
    value = (value or "").strip().lower()
    if not value:
        return ""
    value = value.replace("_", "-").replace(" ", "-")
    if not value.endswith("-session"):
        value = f"{value}-session"
    return value


def source_to_client(source):
    if source.endswith("-session"):
        return source[: -len("-session")]
    return source


def detect_source(cli_source):
    direct = normalize_source(cli_source)
    if direct:
        return direct

    env_source = normalize_source(os.getenv("PANOPTICON_SOURCE", ""))
    if env_source:
        return env_source

    env_client = normalize_source(os.getenv("PANOPTICON_CLIENT", ""))
    if env_client:
        return env_client

    env = os.environ
    if any(key.startswith("OPENCODE") for key in env):
        return "opencode-session"
    if any(key.startswith("CLAUDECODE") for key in env) or any(key.startswith("CLAUDE_CODE") for key in env):
        return "claudecode-session"
    if "AMP" in env:
        return "amp-session"

    path_hint = str(Path(__file__)).lower()
    if "opencode" in path_hint:
        return "opencode-session"
    if "claudecode" in path_hint or "claude-code" in path_hint:
        return "claudecode-session"
    if "/amp" in path_hint or " amp " in path_hint:
        return "amp-session"

    return "codex-session"


def default_out_dir(client):
    return os.path.expanduser(f"~/.{client}/panopticon")


def latest_log(out_dir, prefix):
    try:
        out_dir = Path(os.path.expanduser(out_dir))
        files = sorted(out_dir.glob(f"{prefix}-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not files:
            return None
        with files[0].open() as f:
            return json.load(f)
    except Exception:
        return None


def title_for_client(client):
    if client.lower() == "amp":
        return "AMP"
    parts = client.replace("_", "-").split("-")
    return " ".join(part.capitalize() for part in parts if part)


def infer_title(client, repo_root, remote):
    label = ""
    if remote:
        label = remote.rstrip("/").split("/")[-1].replace(".git", "")
    elif repo_root:
        label = Path(repo_root).name
    else:
        label = Path(os.getcwd()).name
    title_prefix = title_for_client(client) or "Codex"
    if label:
        return f"{title_prefix} Session: {label}"
    return f"{title_prefix} Session"


def build_metadata(repo, remote, branch, commit, cwd, changed_files):
    lines = []
    lines.append(f"repo: {repo or cwd}")
    if remote:
        lines.append(f"remote: {remote}")
    if branch:
        lines.append(f"branch: {branch}")
    if commit:
        lines.append(f"commit: {commit}")
    lines.append(f"working_dir: {cwd}")
    if changed_files:
        lines.append(f"changed_files: {len(changed_files)}")
        for path in changed_files[:50]:
            lines.append(f"- {path}")
        if len(changed_files) > 50:
            lines.append(f"- ... {len(changed_files) - 50} more")
    else:
        lines.append("changed_files: 0")
    return "\n".join(lines)


def strip_metadata_block(text, tag):
    open_tag = f"[{tag}-metadata]"
    close_tag = f"[/{tag}-metadata]"
    if text.startswith(open_tag):
        end = text.find(close_tag)
        if end != -1:
            return text[end + len(close_tag) :].lstrip("\n")
    return text


def compute_delta(transcript_text, last_log, tag):
    if not isinstance(last_log, dict):
        return transcript_text, False

    prev_full = last_log.get("full_transcript")
    if not prev_full:
        prev_full = strip_metadata_block(last_log.get("transcript", ""), tag)

    if not prev_full:
        return transcript_text, False

    if transcript_text.startswith(prev_full):
        remainder = transcript_text[len(prev_full) :].lstrip("\n")
        return remainder, True

    return transcript_text, False


def main():
    parser = argparse.ArgumentParser(description="Create Panopticon webhook payload and send it.")
    parser.add_argument("--transcript-file", required=True)
    parser.add_argument("--message-count", type=int, default=0)
    parser.add_argument("--title", default="")
    parser.add_argument("--source", default="")
    parser.add_argument("--webhook-url", default="")
    parser.add_argument("--out-dir", default="")
    parser.add_argument("--no-send", action="store_true")
    parser.add_argument("--no-delta", action="store_true")
    args = parser.parse_args()

    source = detect_source(args.source)
    client = source_to_client(source)
    env_out_dir = os.getenv("PANOPTICON_OUT_DIR", "").strip()
    out_dir = args.out_dir or env_out_dir or default_out_dir(client)

    transcript_path = Path(args.transcript_file)
    transcript_text = transcript_path.read_text()

    last_log = latest_log(out_dir, client)
    delta_text, matched = compute_delta(transcript_text, last_log, client)

    if not args.no_delta and matched and not delta_text.strip():
        print("No new content since last upload; skipping.")
        return 0

    if args.no_delta:
        delta_text = transcript_text

    cwd = os.getcwd()
    repo_root = run_git(["rev-parse", "--show-toplevel"], cwd)
    repo_cwd = repo_root or cwd
    remote = run_git(["remote", "get-url", "origin"], repo_cwd)
    branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo_cwd)
    commit = run_git(["rev-parse", "--short", "HEAD"], repo_cwd)
    status = run_git(["status", "--porcelain"], repo_cwd)

    changed_files = []
    for line in status.splitlines():
        line = line.strip()
        if not line:
            continue
        if len(line) > 3:
            changed_files.append(line[3:])
        else:
            changed_files.append(line)

    message_count = args.message_count or count_messages(delta_text)

    started_at = last_log.get("ended_at") if isinstance(last_log, dict) and last_log.get("ended_at") else now_iso()
    ended_at = now_iso()

    meta_block = build_metadata(repo_root, remote, branch, commit, cwd, changed_files)
    full_transcript = (
        f"[{client}-metadata]\n" + meta_block + f"\n[/{client}-metadata]\n\n" + delta_text
    )

    thread_id = f"{client}-{timestamp_id()}"
    payload = {
        "thread_id": thread_id,
        "thread_url": f"{client}://{thread_id}",
        "title": args.title or infer_title(client, repo_root, remote),
        "transcript": full_transcript,
        "repository": remote or repo_root or "",
        "branch": branch,
        "working_dir": cwd,
        "started_at": started_at,
        "ended_at": ended_at,
        "message_count": message_count,
    }

    log_payload = dict(payload)
    log_payload["full_transcript"] = transcript_text
    log_payload["delta_applied"] = (not args.no_delta) and matched

    out_dir = Path(os.path.expanduser(out_dir))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{thread_id}.json"
    out_path.write_text(json.dumps(log_payload, indent=2))

    print(f"Wrote {out_path}")

    if args.no_send:
        return 0

    webhook_url = args.webhook_url or os.getenv("PANOPTICON_WEBHOOK_URL", "")
    if not webhook_url:
        base = os.getenv("PANOPTICON_WEBHOOK_BASE", "https://panopticon-app.fly.dev/webhooks").rstrip("/")
        webhook_url = f"{base}/{source}"

    secret = os.getenv("PANOPTICON_WEBHOOK_SECRET", "").strip()
    if not secret:
        print("PANOPTICON_WEBHOOK_SECRET is required to send webhook.", file=sys.stderr)
        return 1

    data = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json", "X-Panopticon-Webhook-Secret": secret}
    req = request.Request(webhook_url, data=data, headers=headers)
    try:
        with request.urlopen(req) as resp:
            body = resp.read().decode()
            print(f"Webhook status: {resp.status}")
            if body:
                print(body)
    except Exception as exc:
        print(f"Webhook error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
