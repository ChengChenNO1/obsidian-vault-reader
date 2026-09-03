"""Integration checks through a real stdio MCP process, using disposable fixtures only."""
import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import StdioTransport


async def main():
    root = Path(__file__).resolve().parents[1]
    checks = []
    with tempfile.TemporaryDirectory(prefix="obsidian-connector-") as temporary:
        base = Path(temporary)
        vault = base / "中文 知识库"
        other = base / "第二个库"
        data = base / "private-config"
        vault.mkdir()
        other.mkdir()
        (vault / ".obsidian").mkdir()
        (vault / ".obsidian" / "secret.md").write_text("excluded", encoding="utf-8")
        original = "---\r\ntags: [测试]\r\n---\r\n# 原始笔记\r\n知识库检索 keyword [[关联]]\r\n".encode("utf-8")
        (vault / "原始笔记.md").write_bytes(original)
        (other / "其他.md").write_text("other vault", encoding="utf-8")
        outside = base / "outside.md"
        outside.write_text("outside secret", encoding="utf-8")
        env = {**os.environ, "OBSIDIAN_CONNECTOR_DATA_DIR": str(data), "PYTHONUTF8": "1"}
        def client():
            return Client(StdioTransport(sys.executable, [str(root / "scripts/server.py")], env=env, cwd=str(root)))
        async with client() as session:
            async def call(name, **args):
                result = await session.call_tool(name, args)
                return result.data
            async def denied(name, **args):
                result = await session.call_tool(name, args, raise_on_error=False)
                assert result.is_error, (name, result)
            names = {t.name for t in await session.list_tools()}
            assert names == {"connection_status", "connect_vault", "list_notes", "read_note", "search_notes", "write_note", "append_note", "move_note", "delete_note"}
            checks.append("MCP handshake and 9 tool schemas")
            assert not (await call("connection_status"))["connected"]
            await denied("read_note", path="原始笔记.md")
            await denied("connect_vault", vault_path="relative")
            await denied("connect_vault", vault_path=str(vault), access="invalid")
            await call("connect_vault", vault_path=str(vault), remember=False)
            assert not data.exists()
            await denied("write_note", path="new.md", content="blocked")
            assert not (vault / "new.md").exists()
            checks.append("unconfigured state, validation, read-only enforcement")
            read = await call("read_note", path="原始笔记.md")
            assert "[[关联]]" in read["content"]
            results = await call("search_notes", query="知识库检索")
            assert results["results"][0]["path"] == "原始笔记.md"
            assert results["results"][0]["line"] == 5
            assert (await call("search_notes", query="原始", filenames_only=True))["results"]
            assert (await call("search_notes", query="KEYWORD"))["results"]
            checks.append("Chinese paths, CRLF, filename and content search on Windows")
            for path in ("../outside.md", str(outside), ".obsidian/secret.md", "file.txt", "file.md:stream"):
                await denied("read_note", path=path)
            assert (await call("list_notes"))["notes"] == ["原始笔记.md"]
            try:
                (vault / "link.md").symlink_to(outside)
            except OSError:
                checks.append("symlink test skipped: OS privilege unavailable")
            else:
                await denied("read_note", path="link.md")
                assert not (await call("search_notes", query="outside secret"))["results"]
                checks.append("symlink escape denied")
            checks.append("path traversal, absolute paths, hidden paths and non-Markdown denied")
            await call("connect_vault", vault_path=str(vault), access="read-write")
            assert json.loads((data / "connection.json").read_text(encoding="utf-8"))["vault_path"] == str(vault)
            await denied("write_note", path="原始笔记.md", content="bad", expected_sha256="wrong")
            await denied("append_note", path="原始笔记.md", content="bad", expected_sha256="wrong")
            assert (vault / "原始笔记.md").read_bytes() == original
            updated = await call("write_note", path="原始笔记.md", content=read["content"] + "新增内容\n", expected_sha256=read["sha256"])
            assert Path(updated["backup"]).read_bytes() == original
            await denied("delete_note", path="原始笔记.md", expected_sha256=read["sha256"])
            appended = await call("append_note", path="原始笔记.md", content="追加内容", expected_sha256=updated["sha256"])
            assert "新增内容" in Path(appended["backup"]).read_text(encoding="utf-8")
            checks.append("update and append with byte-exact backups; stale hashes rejected")
            created = await call("write_note", path="文件夹/新建", content="# 新笔记\n")
            await denied("write_note", path="文件夹/新建.md", content="accidental overwrite")
            await denied("move_note", path="文件夹/新建.md", destination="原始笔记.md", expected_sha256=created["sha256"])
            await call("move_note", path="文件夹/新建.md", destination="归档/新建.md", expected_sha256=created["sha256"])
            assert not (vault / "文件夹/新建.md").exists()
            assert (vault / "归档/新建.md").exists()
            moved = await call("read_note", path="归档/新建.md")
            deleted = await call("delete_note", path="归档/新建.md", expected_sha256=moved["sha256"])
            assert not (vault / "归档/新建.md").exists()
            await call("write_note", path="归档/新建.md", content=Path(deleted["backup"]).read_text(encoding="utf-8"))
            assert (vault / "归档/新建.md").read_text(encoding="utf-8") == "# 新笔记\n"
            checks.append("create, move, delete and restore from backup")
            first = await call("list_notes", limit=1)
            second = await call("list_notes", limit=1, offset=first["next_offset"])
            assert first["has_more"] and first["notes"] != second["notes"]
            await denied("write_note", path="../../escape.md", content="bad")
            await call("connect_vault", vault_path=str(other), remember=False)
            assert (await call("list_notes"))["notes"] == ["其他.md"]
            await denied("read_note", path="原始笔记.md")
            checks.append("pagination and switching vaults without cross-vault reads")
        async with client() as restarted:
            status = (await restarted.call_tool("connection_status")).data
            assert status["connection"]["vault_path"] == str(vault)
            assert status["connection"]["access"] == "read-write"
            checks.append("saved connection survives server restart")
        assert outside.read_text(encoding="utf-8") == "outside secret"
    print(json.dumps({"passed": True, "checks": checks}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
