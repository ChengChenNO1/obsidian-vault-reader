"""Install this shareable plugin into a new personal marketplace entry.

Run with Python 3.11+. Existing, different plugin sources are never overwritten.
"""
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

NAME = "obsidian-vault-reader"
FILES = (
    ".codex-plugin/plugin.json", ".mcp.json", ".gitignore", "pyproject.toml", "uv.lock",
    "README.md", "agent.md", "LICENSE", "scripts/server.py", "scripts/install.py",
    "scripts/verify.py", "skills/obsidian-vault/SKILL.md",
)


def prepare(source: Path, home: Path):
    destination = home / "plugins" / NAME
    marketplace_file = home / ".agents/plugins/marketplace.json"
    if marketplace_file.exists():
        marketplace = json.loads(marketplace_file.read_text(encoding="utf-8-sig"))
    else:
        marketplace = {"name": "personal", "interface": {"displayName": "Personal"}, "plugins": []}
    market_name = marketplace.get("name", "")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", market_name):
        raise ValueError("Existing personal marketplace has an invalid name; no files changed.")
    if not isinstance(marketplace.get("plugins"), list):
        raise ValueError("Existing marketplace plugins field must be an array.")
    entry = next((p for p in marketplace["plugins"] if p.get("name") == NAME), None)
    expected_source = {"source": "local", "path": f"./plugins/{NAME}"}
    if entry and entry.get("source") != expected_source:
        raise ValueError("A different plugin source already uses this name; no files changed.")
    if destination.exists() and destination.resolve() != source.resolve():
        raise FileExistsError(f"Destination exists: {destination}. Use Codex to review an update.")
    for relative in FILES:
        if not (source / relative).is_file():
            raise FileNotFoundError(f"Incomplete plugin package: {relative}")
    if destination.resolve() != source.resolve():
        destination.mkdir(parents=True)
        for relative in FILES:
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / relative, target)
    if entry is None:
        marketplace["plugins"].append({"name": NAME, "source": expected_source,
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity"})
        marketplace_file.parent.mkdir(parents=True, exist_ok=True)
        # Preserve the previous catalog before first registration; no update flow is implemented.
        if marketplace_file.exists():
            backup = marketplace_file.with_name("marketplace.before-obsidian.json")
            if not backup.exists():
                shutil.copy2(marketplace_file, backup)
        staging = marketplace_file.with_name(f"marketplace.{os.getpid()}.tmp")
        staging.write_text(json.dumps(marketplace, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        staging.replace(marketplace_file)
    return destination, market_name


def main():
    uv = shutil.which("uv")
    codex = shutil.which("codex.cmd" if os.name == "nt" else "codex") or shutil.which("codex")
    if not uv or not codex:
        raise SystemExit("Install uv and Codex CLI, then restart the terminal. See README.md.")
    source = Path(__file__).resolve().parents[1]
    destination, marketplace = prepare(source, Path.home())
    # Keep dependencies out of the source/share tree during installation.
    env = {**os.environ, "UV_PROJECT_ENVIRONMENT": str(Path.home() / ".cache" / NAME / "venv")}
    subprocess.run([uv, "sync", "--frozen", "--no-dev", "--project", str(destination)], env=env, check=True)
    subprocess.run([codex, "plugin", "add", f"{NAME}@{marketplace}"], check=True)
    print("Installed. Open a NEW Codex task and specify your vault path and access mode.")


if __name__ == "__main__":
    main()
