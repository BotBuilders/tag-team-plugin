#!/usr/bin/env python3
"""Guards the ChatGPT packaging, which no CI anywhere was checking.

ChatGPT reads a different set of files than Claude Code does, under different names, with
different spelling conventions -- camelCase in plugin.json, snake_case in the skill's
agents/openai.yaml. None of it is exercised until someone installs the plugin, so a wrapper can
sit broken in a repo indefinitely and look fine in review. That is exactly what happened to the
AI CMO wrapper: its openai.yaml was missing the required `interface` block and nobody knew.

These rules mirror the checks in OpenAI's own validator, which ships inside the Codex CLI at
~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py. That file is tied to whichever
CLI version a machine happens to have and is not ours to ship, so the invariants we depend on are
restated here where CI can reach them. Run the real validator too when a machine has Codex.

Skill bodies are not compared here -- scripts/sync-chatgpt-plugin.py --check owns that.
"""
import json
import pathlib
import re
import sys

import yaml

HEX_COLOR = re.compile(r"#[0-9A-Fa-f]{6}\Z")
REQUIRED_INTERFACE = ("displayName", "shortDescription", "longDescription", "developerName", "category")
HTTPS_FIELDS = ("websiteURL", "privacyPolicyURL", "termsOfServiceURL")
MAX_PROMPTS = 3          # entries past the third are dropped by ChatGPT without an error
MAX_PROMPT_CHARS = 128   # longer prompts are truncated, also without an error
AGENT_TOP_LEVEL = {"interface", "policy", "dependencies"}
INSTALLATION_POLICIES = {"NOT_AVAILABLE", "AVAILABLE", "INSTALLED_BY_DEFAULT"}
AUTHENTICATION_POLICIES = {"ON_INSTALL", "ON_USE"}

root = pathlib.Path(__file__).resolve().parent.parent
errors: list[str] = []


def load(path: pathlib.Path, loader=json.loads):
    try:
        return loader(path.read_text())
    except (OSError, ValueError, yaml.YAMLError) as exc:
        errors.append(f"{path.relative_to(root)}: does not parse: {exc}")
        return None


claude_manifest = load(root / ".claude-plugin" / "plugin.json")
if claude_manifest is None:
    sys.exit("FAIL: no readable .claude-plugin/plugin.json; this is not a plugin repo")

name = claude_manifest["name"]
plugin_root = root / "plugins" / name
marketplace_path = root / ".agents" / "plugins" / "marketplace.json"

if not plugin_root.exists() and not marketplace_path.exists():
    print(f"OK: {root.name} ships no ChatGPT packaging; nothing to check")
    sys.exit(0)


def check_manifest() -> None:
    path = plugin_root / ".codex-plugin" / "plugin.json"
    if not path.is_file():
        errors.append(f"missing {path.relative_to(root)}; the ChatGPT manifest lives there, not in .claude-plugin")
        return
    manifest = load(path)
    if manifest is None:
        return
    if manifest.get("name") != name:
        errors.append(
            f'{path.relative_to(root)}: name is "{manifest.get("name")}", expected "{name}" '
            "to match the folder and the Claude manifest"
        )
    if manifest.get("version") != claude_manifest.get("version"):
        errors.append(
            f'version drift: Claude says {claude_manifest.get("version")}, ChatGPT says '
            f'{manifest.get("version")}. One plugin, one version.'
        )
    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        errors.append(f"{path.relative_to(root)}: interface must be an object; the plugin card is built from it")
        return
    for field in REQUIRED_INTERFACE:
        if not isinstance(interface.get(field), str) or not interface[field].strip():
            errors.append(f"{path.relative_to(root)}: interface.{field} must be a non-empty string")
    for field in HTTPS_FIELDS:
        value = interface.get(field)
        if value is not None and not (isinstance(value, str) and value.startswith("https://")):
            errors.append(f"{path.relative_to(root)}: interface.{field} must be an absolute https:// URL")
    brand_color = interface.get("brandColor")
    if brand_color is not None and not (isinstance(brand_color, str) and HEX_COLOR.fullmatch(brand_color)):
        errors.append(f"{path.relative_to(root)}: interface.brandColor must be #RRGGBB")
    prompts = interface.get("defaultPrompt", [])
    if not isinstance(prompts, list):
        errors.append(f"{path.relative_to(root)}: interface.defaultPrompt must be a list")
    else:
        if len(prompts) > MAX_PROMPTS:
            errors.append(
                f"{path.relative_to(root)}: interface.defaultPrompt has {len(prompts)} entries; "
                f"ChatGPT shows the first {MAX_PROMPTS} and silently drops the rest"
            )
        for prompt in prompts:
            if not isinstance(prompt, str) or len(prompt) > MAX_PROMPT_CHARS:
                errors.append(
                    f"{path.relative_to(root)}: a defaultPrompt entry is not a string of "
                    f"{MAX_PROMPT_CHARS} characters or fewer; longer ones are truncated"
                )
    check_mcp(manifest, path)


def check_mcp(manifest: dict, manifest_path: pathlib.Path) -> None:
    declared = manifest.get("mcpServers")
    if isinstance(declared, str):
        mcp_path = plugin_root / declared.removeprefix("./")
        if not mcp_path.is_file():
            errors.append(f'{manifest_path.relative_to(root)}: mcpServers points at "{declared}", which does not exist')
            return
        servers = (load(mcp_path) or {}).get("mcpServers")
    elif isinstance(declared, dict):
        mcp_path, servers = manifest_path, declared
    else:
        return
    if not isinstance(servers, dict) or not servers:
        errors.append(f"{mcp_path.relative_to(root)}: mcpServers must be a non-empty object")
        return
    # A connection plugin owns its server in the Claude manifest too; the two must agree on the
    # host, or signing in on one side grants nothing on the other.
    claude_servers = claude_manifest.get("mcpServers")
    if not isinstance(claude_servers, dict):
        return
    claude_urls = {s.get("url") for s in claude_servers.values() if isinstance(s, dict)}
    for server_name, server in servers.items():
        if not isinstance(server, dict):
            errors.append(f"{mcp_path.relative_to(root)}: server `{server_name}` must be an object")
            continue
        if server.get("url") not in claude_urls:
            errors.append(
                f'{mcp_path.relative_to(root)}: server `{server_name}` points at {server.get("url")}, '
                f"but the Claude manifest points at {sorted(u for u in claude_urls if u)}"
            )


def check_skill_agents() -> None:
    skills_root = plugin_root / "skills"
    if not skills_root.is_dir():
        errors.append(f"missing {skills_root.relative_to(root)}; run scripts/sync-chatgpt-plugin.py")
        return
    for skill_dir in sorted(p for p in skills_root.iterdir() if p.is_dir() and not p.name.startswith(".")):
        path = skill_dir / "agents" / "openai.yaml"
        if not path.is_file():
            errors.append(
                f"missing {path.relative_to(root)}; without it ChatGPT has no display name for "
                f"the `{skill_dir.name}` skill"
            )
            continue
        agent = load(path, yaml.safe_load)
        if agent is None:
            continue
        if not isinstance(agent, dict):
            errors.append(f"{path.relative_to(root)}: must be a mapping")
            continue
        for key in sorted(set(agent) - AGENT_TOP_LEVEL):
            errors.append(f"{path.relative_to(root)}: key `{key}` is rejected; only {sorted(AGENT_TOP_LEVEL)} are allowed")
        interface = agent.get("interface")
        if not isinstance(interface, dict):
            errors.append(f"{path.relative_to(root)}: interface must be a mapping (this is what broke AI CMO)")
            continue
        for field in ("display_name", "short_description"):
            if not isinstance(interface.get(field), str) or not interface[field].strip():
                errors.append(f"{path.relative_to(root)}: interface.{field} must be a non-empty string (snake_case here, not camelCase)")


def check_marketplace() -> None:
    if not marketplace_path.is_file():
        errors.append(f"missing {marketplace_path.relative_to(root)}; ChatGPT has no way to find the plugin without it")
        return
    market = load(marketplace_path)
    if market is None:
        return
    entries = [e for e in market.get("plugins", []) if isinstance(e, dict) and e.get("name") == name]
    if len(entries) != 1:
        errors.append(f'{marketplace_path.relative_to(root)}: expected exactly one entry named "{name}", found {len(entries)}')
        return
    entry = entries[0]
    expected_path = f"./plugins/{name}"
    if entry.get("source", {}).get("path") != expected_path:
        errors.append(f'{marketplace_path.relative_to(root)}: source.path must be "{expected_path}"')
    policy = entry.get("policy", {})
    if policy.get("installation") not in INSTALLATION_POLICIES:
        errors.append(f"{marketplace_path.relative_to(root)}: policy.installation must be one of {sorted(INSTALLATION_POLICIES)}")
    if policy.get("authentication") not in AUTHENTICATION_POLICIES:
        errors.append(f"{marketplace_path.relative_to(root)}: policy.authentication must be one of {sorted(AUTHENTICATION_POLICIES)}")
    if not entry.get("category"):
        errors.append(f"{marketplace_path.relative_to(root)}: entry needs a category")


check_manifest()
check_skill_agents()
check_marketplace()

if errors:
    print(f"FAIL: {len(errors)} problem(s) in the ChatGPT packaging for {root.name}:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(f"OK: {root.name} ships a valid ChatGPT packaging for {name}")
