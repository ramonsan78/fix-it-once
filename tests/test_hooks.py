#!/usr/bin/env python3
"""Tests for the publishing hook, in both languages.
Pruebas del hook de publicación, en los dos idiomas.

Each case says what the hook must do: 2 = block, 0 = allow.
Blocking cases are the positive controls; allowing cases are the negative controls,
so the hook is also tested against blocking normal work.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LANGS = {
    "en": {
        "hook": ROOT / "en/checks/block-publishing.py",
        "dir": "batches",
        "file": "approved.json",
        "valid": {"batch": "2026-12", "approved_by": "Owner", "date": "2026-12-18", "pieces": ["2026-12-morning-light"]},
        "wrong_batch": {"batch": "2026-11", "approved_by": "Owner", "date": "2026-12-18", "pieces": ["x"]},
        "script": "scripts/publish.py",
    },
    "es": {
        "hook": ROOT / "es/control/bloquear-publicacion.py",
        "dir": "lotes",
        "file": "aprobado.json",
        "valid": {"lote": "2026-12", "aprobado_por": "Responsable", "fecha": "2026-12-18", "piezas": ["2026-12-luz-de-la-manana"]},
        "wrong_batch": {"lote": "2026-11", "aprobado_por": "Responsable", "fecha": "2026-12-18", "piezas": ["x"]},
        "script": "scripts/publicar.py",
    },
}


def run(hook, project, tool, tool_input):
    event = {"tool_name": tool, "tool_input": tool_input}
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(project))
    p = subprocess.run([sys.executable, str(hook)], input=json.dumps(event), text=True,
                       capture_output=True, env=env)
    return p.returncode


def cases(c):
    d, f = c["dir"], c["file"]
    out = f"{d}/2026-12/output"
    bash = lambda cmd: ("Bash", {"command": cmd})
    return {
        # no approval yet
        "none": [
            (2, "rclone without approval", bash(f"rclone copy {out} drive:")),
            (2, "rclone without batch", bash("rclone copy output drive:")),
            (2, "gsutil", bash(f"gsutil cp -r {out} gs://bucket")),
            (2, "aws s3", bash(f"aws s3 cp {out} s3://bucket --recursive")),
            (2, "scp", bash(f"scp -r {out} user@host:/srv")),
            (2, "rsync to host", bash(f"rsync -av {out}/ user@host:/srv/")),
            (2, "curl upload", bash(f"curl -T {out}/a.mp4 https://example.com/up")),
            (2, "cp to synced Drive", bash(f"cp -r {out} ~/Library/CloudStorage/GoogleDrive-x/Delivery")),
            (2, "own publish script", bash(f"python3 {c['script']} {out}")),
            (2, "publish inside a chain", bash(f"ls {out} && rclone copy {out} drive:")),
            (2, "self-approval via echo", bash(f"echo '{{}}' > {d}/2026-12/{f}")),
            (2, "self-approval via cp", bash(f"cp /tmp/x.json {d}/2026-12/{f}")),
            (2, "self-approval via python", bash(f"python3 -c \"open('{d}/2026-12/{f}','w').write('{{}}')\"")),
            (2, "Write tool on approval", ("Write", {"file_path": f"{d}/2026-12/{f}", "content": "{}"})),
            (2, "Edit tool on approval", ("Edit", {"file_path": f"{d}/2026-12/{f}", "old_string": "a", "new_string": "b"})),
            (2, "MCP upload without batch", ("mcp__Google_Drive__create_file", {"title": "video.mp4"})),
            (2, "MCP upload without approval", ("mcp__Dropbox__upload_file", {"path": f"{out}/a.mp4"})),
            (0, "ls", bash("ls -la")),
            (0, "grep mentions youtube", bash("grep -ri youtube bible/")),
            (0, "run the checks", bash(f"python3 checks/checks.py {out}")),
            (0, "local copy", bash(f"cp -r {out} /tmp/preview")),
            (0, "read approval", bash(f"cat {d}/2026-12/{f}")),
            (0, "Write another file", ("Write", {"file_path": f"{d}/2026-12/notes.md", "content": "x"})),
            (0, "MCP read", ("mcp__Google_Drive__search_files", {"query": "x"})),
            (0, "MCP email draft", ("mcp__Gmail__create_draft", {"to": "a@b.c"})),
        ],
        # approval file exists but is incomplete
        "empty": [
            (2, "empty approval", bash(f"rclone copy {out} drive:")),
        ],
        "wrong": [
            (2, "approval for another batch", bash(f"rclone copy {out} drive:")),
        ],
        # valid approval
        "valid": [
            (0, "rclone with approval", bash(f"rclone copy {out} drive:")),
            (0, "MCP upload with approval", ("mcp__Dropbox__upload_file", {"path": f"{out}/a.mp4"})),
            (2, "other batch still blocked", bash(f"rclone copy {d}/2027-01/output drive:")),
            (2, "approval still read-only", ("Write", {"file_path": f"{d}/2026-12/{f}", "content": "{}"})),
        ],
    }


def main():
    failures = 0
    total = 0
    for lang, c in LANGS.items():
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            approval = project / c["dir"] / "2026-12" / c["file"]
            approval.parent.mkdir(parents=True)
            states = {"none": None, "empty": {}, "wrong": c["wrong_batch"], "valid": c["valid"]}
            for state, content in states.items():
                if content is None:
                    approval.unlink(missing_ok=True)
                else:
                    approval.write_text(json.dumps(content), encoding="utf-8")
                for want, label, (tool, tool_input) in cases(c)[state]:
                    total += 1
                    got = run(c["hook"], project, tool, tool_input)
                    if got != want:
                        failures += 1
                        print(f"[{lang}] FAIL {state}: {label}: got {got}, want {want}")
        print(f"[{lang}] hook: cases run")
    print(f"hooks: {total - failures} of {total} cases as expected")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
