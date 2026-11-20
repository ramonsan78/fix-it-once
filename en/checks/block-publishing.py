#!/usr/bin/env python3
"""Claude Code hook: blocks publishing or delivering a batch without the owner's approval.

Runs before terminal commands, file edits and MCP tool calls (see .claude/settings.json).

It does three things:
1. Blocks any command or MCP call that publishes or delivers unless the batch it names
   has a valid batches/<YYYY-MM>/approved.json.
2. Blocks Claude from creating or changing approved.json. Only the owner writes it.
3. Checks the approval's content, not just that the file exists.

This is a guardrail against mistakes, not a security boundary: an agent with a shell can
always find a path the patterns don't foresee. Keep the owner's OK as the real control,
and adjust the lists below to the tools you actually use to publish or deliver.
"""

import json
import os
import re
import shlex
import sys
from datetime import date
from pathlib import Path

BATCHES_DIR = "batches"
APPROVAL_FILE = "approved.json"
BATCH_PATTERN = re.compile(r"batches/(\d{4}-\d{2})")

# Commands that publish or deliver by themselves, or with one of these subcommands.
PUBLISH_COMMANDS = {
    "rclone": {"copy", "copyto", "sync", "move", "moveto", "rcat", "bisync"},
    "gsutil": {"cp", "mv", "rsync"},
    "gcloud": {"cp", "mv", "rsync"},          # gcloud storage cp ...
    "aws": {"cp", "mv", "sync"},              # aws s3 cp ...
    "az": {"upload", "upload-batch"},         # az storage blob upload ...
    "scp": None,                              # None: always publishes
    "sftp": None,
    "gdrive": {"upload", "files"},
    "youtube-upload": None,
}
# Tools that publish only when the destination is remote (host:path) or a delivery folder.
COPY_COMMANDS = {"cp", "mv", "rsync", "ditto"}
# Synced folders that count as delivery. Add your own (for example the client's shared folder).
DELIVERY_FOLDERS = ["Google Drive", "GoogleDrive", "My Drive", "Dropbox", "OneDrive",
                    "Library/CloudStorage", "iCloud Drive"]
# Your own publishing scripts: their file name starts with one of these words.
SCRIPT_PREFIXES = ("publish", "upload", "deliver")
INTERPRETERS = {"python", "python3", "node", "bash", "sh", "zsh", "deno", "bun", "npx"}
# Read-only commands allowed to touch approved.json.
READ_ONLY = {"cat", "ls", "head", "tail", "less", "more", "stat", "test", "[", "jq", "grep", "wc", "file", "diff"}
# MCP actions that write, send or share. Matched against the tool's action name.
MCP_PUBLISH = re.compile(
    r"(upload|create_file|update_file|copy|move|share|publish|send|post|insert|create_folder|"
    r"commit|create_shared_link|file_request)", re.IGNORECASE)


def block(message):
    print("Blocked: " + message, file=sys.stderr)
    sys.exit(2)


def segments(command):
    """Split a shell command into simple commands (by ; && || | and newlines)."""
    parts = re.split(r"\|\||&&|;|\||\n", command)
    out = []
    for part in parts:
        try:
            tokens = shlex.split(part, comments=True)
        except ValueError:
            tokens = part.split()
        while tokens and (re.match(r"^\w+=", tokens[0]) or tokens[0] in {"sudo", "env", "time", "nohup", "exec"}):
            tokens = tokens[1:]
        if tokens:
            out.append((part, tokens))
    return out


def is_delivery_path(arg):
    expanded = os.path.expanduser(arg)
    return any(folder in expanded for folder in DELIVERY_FOLDERS)


def publishes(tokens):
    name = os.path.basename(tokens[0])
    args = tokens[1:]
    if name in PUBLISH_COMMANDS:
        subs = PUBLISH_COMMANDS[name]
        return subs is None or any(a in subs for a in args)
    if name == "curl":
        return any(a in {"-T", "--upload-file", "-F", "--form"} or a.startswith("--data-binary") for a in args)
    if name in COPY_COMMANDS:
        targets = [a for a in args if not a.startswith("-")]
        dest = targets[-1] if targets else ""
        remote = name in {"rsync", "scp"} and re.match(r"^[\w.-]+@?[\w.-]*:", dest or "")
        return bool(remote) or is_delivery_path(dest)
    script = tokens[1] if name in INTERPRETERS and len(tokens) > 1 else tokens[0]
    return os.path.basename(script).lower().startswith(SCRIPT_PREFIXES)


def check_approval(root, batch):
    path = root / BATCHES_DIR / batch / APPROVAL_FILE
    if not path.is_file():
        return f"the owner has not approved batch {batch}: {BATCHES_DIR}/{batch}/{APPROVAL_FILE} is missing."
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return f"{BATCHES_DIR}/{batch}/{APPROVAL_FILE} is not valid JSON."
    problems = []
    if data.get("batch") != batch:
        problems.append(f'"batch" must be "{batch}"')
    if not str(data.get("approved_by", "")).strip():
        problems.append('"approved_by" is empty')
    try:
        date.fromisoformat(str(data.get("date", "")))
    except ValueError:
        problems.append('"date" must be YYYY-MM-DD')
    pieces = data.get("pieces")
    if not isinstance(pieces, list) or not pieces:
        problems.append('"pieces" must list at least one approved piece')
    if problems:
        return f"the approval for batch {batch} is incomplete: " + "; ".join(problems) + "."
    return None


def require_approval(root, text, what):
    batches = sorted(set(BATCH_PATTERN.findall(text)))
    if not batches:
        block(f"this {what} publishes or delivers but doesn't name the batch ({BATCHES_DIR}/YYYY-MM). "
              "Include the batch path so its approval can be checked.")
    for batch in batches:
        problem = check_approval(root, batch)
        if problem:
            block(problem + " Ask the owner to approve before publishing or delivering.")


def main():
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    root = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
    tool = event.get("tool_name", "Bash")
    tool_input = event.get("tool_input") or {}

    # 1. Claude never writes the approval file.
    if tool in {"Write", "Edit", "MultiEdit", "NotebookEdit"}:
        target = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
        if os.path.basename(target) == APPROVAL_FILE:
            block(f"only the owner creates or edits {APPROVAL_FILE}. Show them the content and let them save it.")
        sys.exit(0)

    # 2. MCP connectors (Drive, Dropbox, YouTube, email...).
    if tool.startswith("mcp__"):
        action = tool.split("__")[-1]
        if MCP_PUBLISH.search(action):
            require_approval(root, json.dumps(tool_input, ensure_ascii=False), "connector action")
        sys.exit(0)

    # 3. Terminal commands.
    if tool != "Bash":
        sys.exit(0)
    command = tool_input.get("command", "")
    for raw, tokens in segments(command):
        name = os.path.basename(tokens[0])
        if APPROVAL_FILE in raw and name not in READ_ONLY:
            block(f"only the owner creates or edits {APPROVAL_FILE}. Show them the content and let them save it.")
        if publishes(tokens):
            require_approval(root, raw, "command")
    sys.exit(0)


if __name__ == "__main__":
    main()
