[English](README.md) | [中文](README.zh-CN.md)

# Obsidian Vault Assistant - Codex Plugin

Let Codex directly query and modify your selected local Obsidian vault.

Supports Chinese paths, full-text/filename search, read, create, edit, append, move, and delete Markdown notes. Modifications are backed up before writing, with content-conflict checks. Users choose their own vault and read-only/read-write permissions. No Obsidian REST API or API key is required.

## Installation

Requires **Codex CLI, Git, and [uv](https://docs.astral.sh/uv/getting-started/installation/)**, with `uv` in Codex's PATH. First launch downloads dependencies online; uv can install Python 3.11+ on demand.

```sh
codex plugin marketplace add https://github.com/ChengChenNO1/obsidian-vault-reader.git
codex plugin add obsidian-vault-reader@obsidian-vault
```

Or send this message to Codex on another machine:

> Install the Obsidian Vault Assistant from https://github.com/ChengChenNO1/obsidian-vault-reader. Check Git and uv, add the repository's marketplace, then install obsidian-vault-reader@obsidian-vault.

After installation, **start a new Codex task** and say:

> Use the Obsidian Vault Assistant, connect to "full path to my vault", allow query and modification.

Windows path example: `D:\MyVault`; macOS path example: `/Users/yourusername/Documents/MyVault`.
The plugin does not auto-guess paths and never connects to the repository author's vault.

Once connected, you can say:

- "Search for notes related to project retrospective, with sources."
- "Change this paragraph in plan.md to..., keeping everything else."
- "Create inbox/ideas.md with the content..."
- "Move old-note.md to the archive directory, check references that need updating."

## Scope & Backup

- Directly reads and writes `.md` / `.markdown` files; changes are reflected in Obsidian. Single-note size limit: 2 MiB.
- Backs up before overwrite, append, move, or delete existing notes; write operations require a prior read and content hash.
- Local configuration and backups are stored in `~/.obsidian-codex/`. The plugin code contains no user notes, vault paths, or credentials.
- Moves do not auto-fix wikilinks in other notes; ask Codex to update related references separately.
- Hidden directories, symlinks, and junctions are not accessible; PDF/OCR, image, or Canvas editing is not supported.
- This is a local Codex plugin. Regular ChatGPT web cannot directly access your disk through this plugin.

Full usage, limitations, and recovery methods are in the [plugin docs](plugins/obsidian-vault-reader/README.md).

## Updates

```sh
codex plugin marketplace upgrade obsidian-vault
codex plugin add obsidian-vault-reader@obsidian-vault
```

Start a new task after updating to load the new version. If Codex does not recognize the `plugin` subcommand, upgrade Codex CLI first.

## Implementation & Verification

Built on [trsdn/obsidian-mcp](https://github.com/trsdn/obsidian-mcp) and [FastMCP](https://github.com/PrefectHQ/fastmcp), with dependencies pinned via `uv.lock`.
The adapter layer adds vault selection, permissions, local backups, conflict checks, path validation, and Windows Chinese-path search support.

```sh
cd plugins/obsidian-vault-reader
uv run --frozen python scripts/verify.py
```

Tests operate only on temporary test vaults. Windows has been verified for read, search, create/edit/move/delete, backup recovery, and boundary checks; macOS/Linux have not been tested on real hardware.
Verified on 2026-09-03 with an independent Codex configuration: added the marketplace from this GitHub repo, installed the plugin, launched the downloaded copy, and discovered all 9 MCP tools.

This is an independent community plugin, not an official Obsidian/OpenAI plugin. MIT license; dependencies retain their respective licenses.