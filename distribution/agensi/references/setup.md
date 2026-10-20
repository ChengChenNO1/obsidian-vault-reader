# Local runtime setup

## Requirements

Use a local agent that supports both SKILL.md and stdio MCP servers. Install uv on the computer running the agent. Python 3.11+ is required; uv can provision it. The first dependency sync may need internet access. An agent subscription or model API cost is separate from the skill purchase.

This package contains the working Python MCP server, uv.lock, and the original Codex plugin under `assets/obsidian-vault-reader/`. The purchase does not provide cloud hosting or a new Obsidian account. The adapter is MIT licensed; dependencies retain their own licenses.

## Codex: install the bundled plugin

Extract the ZIP to a permanent local directory. From `assets/obsidian-vault-reader/`, run:

```sh
python scripts/install.py
```

The installer requires Codex CLI and uv in PATH. It copies the bundled plugin to `~/plugins/obsidian-vault-reader/`, preserves existing personal-marketplace entries, installs locked dependencies, and registers the plugin. It refuses to overwrite a different existing plugin source. If it reports an existing directory, inspect that installation and perform a deliberate update instead of deleting it.

Start a new Codex task after installation. Ask the user for their vault path and access mode; do not connect to a sample path.

The public GitHub marketplace remains an alternative installation source:
```sh
codex plugin marketplace add https://github.com/ChengChenNO1/obsidian-vault-reader.git
codex plugin add obsidian-vault-reader@obsidian-vault
```

## Other MCP-capable local agents

Keep the extracted runtime in a permanent directory and add a stdio MCP server in the host's supported configuration format. Use the absolute path to the extracted `assets/obsidian-vault-reader` directory. For hosts using the common `mcpServers` JSON structure, adapt this example:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "uv",
      "args": [
        "run", "--frozen", "--no-dev",
        "--project", "/ABSOLUTE/PATH/assets/obsidian-vault-reader",
        "python", "/ABSOLUTE/PATH/assets/obsidian-vault-reader/scripts/server.py"
      ],
      "env": {"PYTHONUTF8": "1"}
    }
  }
}
```

On Windows, use JSON-escaped absolute paths or forward slashes. Replace both placeholders with the same extracted runtime location. Follow the host's own configuration UI and schema; do not assume this JSON can be pasted into every agent unchanged. Restart/reload the host and verify that all nine tools appear. Start with `connection_status`.

A hosted chat session without access to the user's local MCP server cannot use this package to reach their disk.

## Tool inventory

| Tools | Purpose |
|---|---|
| connection_status, connect_vault | Select a vault and read-only/read-write mode |
| list_notes, search_notes, read_note | Paginate, locate, and read Markdown notes |
| write_note, append_note | Create, replace, and append with hash checks |
| move_note, delete_note | Move or delete explicitly requested notes with backup |

## Data, permissions, and recovery

The runtime reads the selected vault and writes only when the connection is read-write. Configuration and backups are stored under `~/.obsidian-codex/`; the optional `OBSIDIAN_CONNECTOR_DATA_DIR` environment variable overrides that location. These are local data files and must not be added to a distribution archive.

Existing-note operations save a byte-exact backup and return its path. To restore, read that exact backup with an authorized local file tool and use normal note write/hash checks. Backups have no automatic retention cleanup. The calling AI host receives the note content requested through MCP; its own data policy still applies.

## Verify without using a real vault

From the runtime directory:
```sh
uv run --frozen python scripts/verify.py
```

The test creates disposable vaults and an isolated data directory. It checks the nine tools, Chinese paths, search, permissions, path boundaries, conflict detection, backups, create/edit/append/move/delete, restoration, and saved connection restart.
