"""Build a source-only Agensi ZIP with SKILL.md at archive root."""
import argparse
import ast
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "obsidian-vault-reader"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    module = ast.parse((PLUGIN / "scripts/install.py").read_text(encoding="utf-8"))
    files = next(ast.literal_eval(node.value) for node in module.body
                 if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "FILES" for t in node.targets))
    entries = {
        "SKILL.md": ROOT / "distribution/agensi/SKILL.md",
        "references/setup.md": ROOT / "distribution/agensi/references/setup.md",
        "LICENSE": ROOT / "LICENSE",
    }
    for relative in files:
        entries["assets/obsidian-vault-reader/" + relative] = PLUGIN / relative
    forbidden = {".env", ".venv", ".git", "__pycache__", ".obsidian", ".obsidian-codex"}
    for name, path in entries.items():
        if forbidden.intersection(Path(name).parts) or not path.is_file():
            raise ValueError(f"Unexpected or missing package file: {name}")
        if ".." in Path(name).parts or Path(name).is_absolute():
            raise ValueError(f"Unsafe ZIP path: {name}")
    frontmatter = entries["SKILL.md"].read_text(encoding="utf-8")
    assert frontmatter.splitlines()[:2] == ["---", "name: obsidian-vault-assistant"]
    assert frontmatter.splitlines()[2].startswith("description: ")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, path in sorted(entries.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 20, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
    with zipfile.ZipFile(args.output) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == set(entries)
        assert len([n for n in archive.namelist() if n == "SKILL.md"]) == 1
    size = args.output.stat().st_size
    assert size < 50 * 1024 * 1024
    print(json.dumps({"zip": str(args.output), "files": len(entries), "bytes": size,
                      "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest()}, indent=2))

if __name__ == "__main__":
    main()
