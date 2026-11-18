#!/usr/bin/env python3
"""Claude Code hook: blocks publishing or delivering a batch without approval.

Runs before every terminal command (see .claude/settings.json).
If the command publishes or delivers (uploads, rclone, publishing scripts),
it requires batches/<YYYY-MM>/approved.json for the batch named in the command.
If it's missing, it blocks the command and tells Claude why.

Adjust PUBLISH_PATTERN to the tools you use to publish or deliver.
"""

import json
import os
import re
import sys
from pathlib import Path

PUBLISH_PATTERN = re.compile(r"(publish|rclone\s+(copy|sync|move)|youtube|upload)", re.IGNORECASE)
BATCH_PATTERN = re.compile(r"batches/(\d{4}-\d{2})")


def main():
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    command = (event.get("tool_input") or {}).get("command", "")
    if not PUBLISH_PATTERN.search(command):
        sys.exit(0)

    root = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
    batches = BATCH_PATTERN.findall(command)
    if not batches:
        print(
            "Blocked: this command publishes or delivers, but it doesn't name the batch (batches/YYYY-MM). "
            "Include the batch path so its approval can be checked.",
            file=sys.stderr,
        )
        sys.exit(2)

    missing = [b for b in sorted(set(batches)) if not (root / "batches" / b / "approved.json").is_file()]
    if missing:
        print(
            "Blocked: the owner has not approved batch " + ", ".join(missing) +
            ". batches/<batch>/approved.json is missing. Get approval before publishing or delivering.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
