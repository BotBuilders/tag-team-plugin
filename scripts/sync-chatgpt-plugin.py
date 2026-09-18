#!/usr/bin/env python3
"""Keeps the ChatGPT copy of the skills identical to the Claude originals.

ChatGPT reads skills from inside its own plugin folder, so the same SKILL.md has to exist twice.
Two hand-maintained copies drift the first time someone edits one, and the drift is invisible --
both halves still install, they just say different things. So the root `skills/` tree is the only
thing anyone edits, and this script reproduces it under `plugins/<name>/skills/`.

`agents/openai.yaml` is the exception: it exists only on the ChatGPT side and has no original to
copy from, so anything under an `agents/` directory is left alone.
"""
import filecmp
import json
import pathlib
import shutil
import sys

root = pathlib.Path(__file__).resolve().parent.parent
check_only = "--check" in sys.argv[1:]

name = json.loads((root / ".claude-plugin" / "plugin.json").read_text())["name"]
source_root = root / "skills"
dest_root = root / "plugins" / name / "skills"

if not source_root.is_dir():
    sys.exit(f"FAIL: no {source_root.relative_to(root)} to sync from")

# Only files the ChatGPT side owns outright are exempt from mirroring.
def is_chatgpt_only(relative: pathlib.PurePath) -> bool:
    return "agents" in relative.parts

drift: list[str] = []

for source in sorted(p for p in source_root.rglob("*") if p.is_file()):
    relative = source.relative_to(source_root)
    dest = dest_root / relative
    if dest.is_file() and filecmp.cmp(source, dest, shallow=False):
        continue
    drift.append(f"{'missing' if not dest.is_file() else 'differs'}: {dest.relative_to(root)}")
    if not check_only:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)

for dest in sorted(p for p in dest_root.rglob("*") if p.is_file()):
    relative = dest.relative_to(dest_root)
    if is_chatgpt_only(relative) or (source_root / relative).is_file():
        continue
    drift.append(f"stale: {dest.relative_to(root)}")
    if not check_only:
        dest.unlink()

if check_only:
    if drift:
        print(f"FAIL: ChatGPT skills are out of sync with {source_root.relative_to(root)}:")
        for d in drift:
            print(f"  - {d}")
        print("  Run scripts/sync-chatgpt-plugin.py to fix.")
        sys.exit(1)
    print(f"OK: ChatGPT skills match {source_root.relative_to(root)}")
else:
    for d in drift:
        print(f"  {d}")
    print(f"OK: synced {source_root.relative_to(root)} -> {dest_root.relative_to(root)}")
