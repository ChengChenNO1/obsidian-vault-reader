"""Codex adapter for trsdn-obsidian-mcp 0.1.2 (MIT).

The upstream note operations are reused; this adapter adds vault selection,
safe paths, Windows-compatible search, backups and optimistic concurrency.
"""
from __future__ import annotations

import functools
import hashlib
import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Literal

from fastmcp import FastMCP
from obsidian_mcp import server as upstream
from pydantic import Field

mcp = FastMCP("obsidian-vault-connector")
DATA = Path(os.environ.get("OBSIDIAN_CONNECTOR_DATA_DIR", "~/.obsidian-codex")).expanduser()
CONFIG_FILE = DATA / "connection.json"
MAX_BYTES = 2 * 1024 * 1024
SUFFIXES = {".md", ".markdown"}
LOCK = threading.RLock()
connection: dict | None = None
loaded = False
READ = {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False}
WRITE = {"readOnlyHint": False, "destructiveHint": True, "openWorldHint": False}


def serialized(fn):
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        with LOCK:
            return fn(*args, **kwargs)
    return wrapped


def _load():
    global connection, loaded
    if not loaded:
        if CONFIG_FILE.is_file():
            value = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            if value.get("access") not in {"read-only", "read-write"}:
                raise ValueError("Invalid saved access mode. Reconnect with connect_vault.")
            connection = value
        loaded = True


def _vault(write=False) -> Path:
    _load()
    if connection is None:
        raise ValueError("No vault selected. Ask the user for a path, then call connect_vault.")
    root = Path(connection["vault_path"]).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("The selected vault is not a directory. Reconnect with connect_vault.")
    if write and connection["access"] != "read-write":
        raise PermissionError("Read-only connection. Reconnect with read-write access when requested.")
    upstream.CONFIG = upstream.Config(root, connection["access"] == "read-only")
    return root


def _linked(path: Path) -> bool:
    return path.is_symlink() or bool(getattr(path, "is_junction", lambda: False)())


def _path(rel: str, *, note=False, write=False) -> Path:
    root = _vault(write)
    relative = Path(rel.replace("\\", "/"))
    if relative.is_absolute() or relative.drive or ".." in relative.parts:
        raise ValueError("Use a vault-relative path without '..' or a drive prefix.")
    if any(part.startswith(".") or ":" in part for part in relative.parts):
        raise ValueError("Hidden/configuration paths and alternate data streams are excluded.")
    if note:
        if not relative.name:
            raise ValueError("A note path is required.")
        if not relative.suffix:
            relative = relative.with_suffix(".md")
        if relative.suffix.lower() not in SUFFIXES:
            raise ValueError("Only .md and .markdown notes are supported.")
    target = root / relative
    cursor = root
    for part in relative.parts:
        cursor = cursor / part
        if _linked(cursor):
            raise ValueError("Symbolic links and directory junctions are excluded.")
    resolved = target.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError("Path escapes the selected vault.")
    return resolved


def _rel(path: Path) -> str:
    return path.relative_to(_vault()).as_posix()


def _walk(folder="", recursive=True):
    base = _path(folder)
    if not base.is_dir():
        raise ValueError("Folder does not exist.")
    def fail(error):
        raise error
    for directory, folders, files in os.walk(base, followlinks=False, onerror=fail):
        folders[:] = sorted(n for n in folders if not n.startswith(".") and not _linked(Path(directory) / n))
        for name in sorted(files):
            path = Path(directory) / name
            if not name.startswith(".") and path.suffix.lower() in SUFFIXES and not _linked(path):
                yield _path(_rel(path), note=True)
        if not recursive:
            break


def _bytes(path: Path) -> bytes:
    # Bounded reads also protect against a file growing after stat().
    with path.open("rb") as stream:
        value = stream.read(MAX_BYTES + 1)
    if len(value) > MAX_BYTES:
        raise ValueError("Note exceeds the 2 MiB limit; split it before using this connector.")
    return value


def _hash(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _check(path: Path, expected: str) -> bytes:
    value = _bytes(path)
    if not expected or _hash(value) != expected:
        raise ValueError("Note changed or expected_sha256 is missing. Read it again before editing.")
    return value


def _backup(path: Path, value: bytes) -> str:
    vault_id = _hash(str(_vault()).encode("utf-8"))[:16]
    folder = DATA / "backups" / vault_id
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    destination = folder / f"{stamp}-{uuid.uuid4().hex}.md"
    destination.write_bytes(value)
    destination.with_suffix(".json").write_text(json.dumps({
        "vault_path": str(_vault()), "note_path": _rel(path), "sha256": _hash(value)
    }, ensure_ascii=False), encoding="utf-8")
    return str(destination)


def _content(content: str):
    if len(content.encode("utf-8")) > MAX_BYTES:
        raise ValueError("Content exceeds the 2 MiB note limit.")


@mcp.tool(annotations=READ)
@serialized
def connection_status() -> dict:
    """Report the selected vault and access mode without reading any notes."""
    _load()
    return {"connected": connection is not None, "connection": connection,
            "config_file": str(CONFIG_FILE), "backup_directory": str(DATA / "backups")}


@mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "openWorldHint": False})
@serialized
def connect_vault(vault_path: str, access: Literal["read-only", "read-write"] = "read-only",
                  remember: bool = True) -> dict:
    """Select a user-specified absolute vault path and permissions. Never guess the user's vault.

    remember stores this choice outside the plugin for future sessions. An existing session
    retains its own selected vault. This operation does not change vault contents.
    """
    global connection, loaded
    candidate = Path(vault_path).expanduser()
    if not candidate.is_absolute():
        raise ValueError("Provide an absolute vault path.")
    root = candidate.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Vault path must be an existing directory.")
    value = {"vault_path": str(root), "access": access}
    if remember:
        DATA.mkdir(parents=True, exist_ok=True)
        temporary = DATA / f"connection-{uuid.uuid4().hex}.tmp"
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
        temporary.replace(CONFIG_FILE)
    connection, loaded = value, True
    return {**connection_status(), "has_obsidian_settings": (root / ".obsidian").is_dir(),
            "remembered": remember}


@mcp.tool(annotations=READ)
@serialized
def list_notes(folder: str = "", recursive: bool = True,
               limit: Annotated[int, Field(ge=1, le=1000)] = 100,
               offset: Annotated[int, Field(ge=0)] = 0) -> dict:
    """List note paths with pagination, excluding hidden files and links."""
    import itertools
    paths = [_rel(p) for p in itertools.islice(_walk(folder, recursive), offset, offset + limit + 1)]
    return {"notes": paths[:limit], "has_more": len(paths) > limit, "next_offset": offset + min(len(paths), limit)}


@mcp.tool(annotations=READ)
@serialized
def read_note(path: str) -> dict:
    """Read a Markdown note. Use returned sha256 for later edits or deletion."""
    target = _path(path, note=True)
    value = _bytes(target)
    # Upstream uses the same validated .md/.markdown path. Hash the bytes returned
    # by its read so a concurrent edit cannot pair old content with a new hash.
    content = upstream.read_note(_rel(target))
    if content != value.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n"):
        raise ValueError("Note changed during reading; retry read_note.")
    return {"path": _rel(target), "content": content, "sha256": _hash(value), "bytes": len(value)}


@mcp.tool(annotations=READ)
@serialized
def search_notes(query: str, folder: str = "", filenames_only: bool = False,
                 case_sensitive: bool = False,
                 limit: Annotated[int, Field(ge=1, le=500)] = 50) -> dict:
    """Search literal text in note paths or lines; works with Windows and Chinese paths.

    Results include note paths and line numbers. truncated means more results may exist.
    Large or undecodable notes are reported as skipped, not silently treated as no matches.
    """
    if not query:
        raise ValueError("Search text must not be empty.")
    needle = query if case_sensitive else query.casefold()
    results, skipped = [], []
    for target in _walk(folder):
        rel = _rel(target)
        if filenames_only:
            lines = [(0, rel)]
        else:
            try:
                lines = enumerate(_bytes(target).decode("utf-8-sig").splitlines(), 1)
            except (OSError, UnicodeDecodeError, ValueError) as error:
                skipped.append({"path": rel, "reason": str(error)})
                continue
        for number, line in lines:
            if needle in (line if case_sensitive else line.casefold()):
                results.append({"path": rel, "line": number, "text": line[:2000]})
                if len(results) >= limit:
                    return {"results": results, "truncated": True, "skipped": skipped}
    return {"results": results, "truncated": False, "skipped": skipped}


@mcp.tool(annotations=WRITE)
@serialized
def write_note(path: str, content: str, expected_sha256: str = "") -> dict:
    """Create a note, or replace an existing note using the hash from read_note.

    Existing notes are backed up first. Preserve frontmatter and wikilinks when editing.
    """
    target = _path(path, note=True, write=True)
    _content(content)
    exists = target.exists()
    if not exists and expected_sha256:
        raise ValueError("The previously read note no longer exists. Recheck before creating it.")
    backup = None
    if exists:
        backup = _backup(target, _check(target, expected_sha256))
        _check(target, expected_sha256)
    result = upstream.write_note(_rel(target), content, overwrite=exists)
    return {**result, "sha256": _hash(_bytes(target)), "backup": backup}


@mcp.tool(annotations=WRITE)
@serialized
def append_note(path: str, content: str, expected_sha256: str, separator: str = "\n\n") -> dict:
    """Append to an existing note after checking its read_note hash; save a backup first."""
    target = _path(path, note=True, write=True)
    value = _check(target, expected_sha256)
    _content(value.decode("utf-8") + separator + content)
    backup = _backup(target, value)
    _check(target, expected_sha256)
    result = upstream.append_note(_rel(target), content, separator)
    return {**result, "sha256": _hash(_bytes(target)), "backup": backup}


@mcp.tool(annotations=WRITE)
@serialized
def move_note(path: str, destination: str, expected_sha256: str) -> dict:
    """Move/rename a note with backup; never overwrite a destination.

    Wikilinks in other notes are not automatically updated. Search for incoming links first.
    """
    source = _path(path, note=True, write=True)
    target = _path(destination, note=True, write=True)
    if target.exists():
        raise FileExistsError("Destination already exists.")
    value = _check(source, expected_sha256)
    backup = _backup(source, value)
    _check(source, expected_sha256)
    target.parent.mkdir(parents=True, exist_ok=True)
    result = upstream.move_note(_rel(source), _rel(target), overwrite=False)
    return {**result, "backup": backup, "links_updated": False}


@mcp.tool(annotations=WRITE)
@serialized
def delete_note(path: str, expected_sha256: str) -> dict:
    """Delete one explicitly requested Markdown note after checking its hash and backing it up."""
    target = _path(path, note=True, write=True)
    backup = _backup(target, _check(target, expected_sha256))
    _check(target, expected_sha256)
    return {**upstream.delete_note(_rel(target)), "backup": backup}


if __name__ == "__main__":
    mcp.run(show_banner=False)
