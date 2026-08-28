#!/usr/bin/env python3
"""Guards the invariants that Claude Code will not guard for us.

A second plugin declaring the same MCP server does not error at install time — it silently opens
a duplicate connection and puts a duplicate set of tools in the model's context. A dependency
written as "name@marketplace" installs nothing, also silently, because cross-marketplace
dependencies do not resolve. Neither failure is visible in review, so they need a machine gate.

The repo's role is inferred from its root manifest rather than hardcoded: a plugin that declares
dependencies is a product (it must own no server); one that declares none owns the connection.
"""
import json
import pathlib
import sys

FORBIDDEN_KEYS = ("feature_tag", "skill_tag_ids", "entitlement")

root = pathlib.Path(__file__).resolve().parent.parent
errors: list[str] = []


def load(path: pathlib.Path):
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        errors.append(f"{path.relative_to(root)}: does not parse: {exc}")
        return None


root_manifest_path = root / ".claude-plugin" / "plugin.json"
if not root_manifest_path.is_file():
    sys.exit(f"FAIL: no {root_manifest_path.relative_to(root)}; this is not a plugin repo")

root_manifest = load(root_manifest_path)
if root_manifest is None:
    sys.exit("\n".join(errors))

manifests = sorted(
    p for p in root.rglob(".claude-plugin/plugin.json")
    if ".git" not in p.parts and "node_modules" not in p.parts
)

declaring = [p for p in manifests if isinstance((load(p) or {}).get("mcpServers"), dict)]
is_product = bool(root_manifest.get("dependencies"))

if is_product:
    if declaring:
        errors.append(
            "product plugin must declare no mcpServers, found in: "
            + ", ".join(str(p.relative_to(root)) for p in declaring)
            + "\n  Move the server into the shared connection plugin and depend on it by bare name."
        )
    for dep in root_manifest["dependencies"]:
        if "@" in dep:
            errors.append(
                f'dependency "{dep}" is marketplace-qualified; use the bare name "{dep.split("@")[0]}".'
                "\n  A qualified name does not auto-install and fails silently."
            )
else:
    if len(declaring) != 1:
        errors.append(
            f"connection plugin must declare exactly one mcpServers, found {len(declaring)}: "
            + (", ".join(str(p.relative_to(root)) for p in declaring) or "none")
        )
    elif declaring[0] != root_manifest_path:
        errors.append(
            f"mcpServers is declared in {declaring[0].relative_to(root)}, expected the repo root manifest"
        )

for path in manifests:
    text = path.read_text()
    for key in FORBIDDEN_KEYS:
        if f'"{key}"' in text:
            errors.append(
                f'{path.relative_to(root)}: declares "{key}". Entitlement is resolved server-side '
                "per account; a manifest that filters is a second source of truth."
            )

for path in sorted(root.rglob(".claude-plugin/marketplace.json")):
    if ".git" in path.parts:
        continue
    market = load(path)
    if market is None:
        continue
    names = [e.get("name") for e in market.get("plugins", [])]
    dupes = {n for n in names if names.count(n) > 1}
    if dupes:
        errors.append(f"{path.relative_to(root)}: duplicate plugin entries: {sorted(dupes)}")
    if not names:
        errors.append(f"{path.relative_to(root)}: declares no plugins")

if errors:
    print(f"FAIL: {len(errors)} problem(s) in {root.name}:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

role = "product" if is_product else "connection"
print(f"OK: {root.name} is a valid {role} plugin ({len(manifests)} manifest(s) checked)")
