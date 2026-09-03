# Obsidian 知识库助手

在 Codex 中连接自己选择的本地 Obsidian 库，搜索、读取、新建、修改、追加、移动和删除 Markdown 笔记。
插件标识为 `obsidian-vault-reader`，显示名称为 **Obsidian 知识库助手**；当前版本已支持读写。
无需运行 Obsidian，也不需要安装 Obsidian Local REST API 插件或填写 API key。

## 安装与开始使用

需要 Codex 桌面应用/CLI、[uv](https://docs.astral.sh/uv/getting-started/installation/) 及 Python 3.11 以上。
uv 可按需安装 Python，首次安装依赖需要联网。确保运行 Codex 时能在 PATH 中找到 `uv`。

从 GitHub 直接安装（推荐，需 Git）：

```powershell
codex plugin marketplace add https://github.com/ChengChenNO1/obsidian-vault-reader.git
codex plugin add obsidian-vault-reader@obsidian-vault
```

也可以把 [GitHub 仓库](https://github.com/ChengChenNO1/obsidian-vault-reader) 链接交给另一台电脑的 Codex，要求“安装这个插件，并帮助我连接 Obsidian 库”。

如果收到的是独立插件 ZIP，解压后在插件目录运行：

```powershell
python scripts/install.py
```

安装器将插件放到 `~/plugins/obsidian-vault-reader/`，添加到个人 marketplace，再执行 Codex 插件安装。
不会覆盖另一份已有插件目录。依赖固定在 `uv.lock`；请保留解压文件直至安装成功。

安装后新建一个 Codex 任务，通过 `@` 选择“Obsidian 知识库助手”，或者直接说：

> 使用 Obsidian 知识库助手，连接 `D:\我的知识库`，允许查询和修改。

把示例路径换成你的实际库路径。尚未指定路径时，助手会询问，不会自动连接某个库。
也可以说“只读连接这个库”。连接成功后可以继续说：

- 搜索库中关于某个主题的笔记，给出来源。
- 阅读“项目/会议记录.md”，总结本周待办。
- 新建“收件箱/想法.md”，内容是……
- 将“项目/计划.md”中的截止日期更新为……，保留其他内容。
- 将“旧笔记.md”移动到“归档/旧笔记.md”。
- 删除“临时草稿.md”。

切换库：再次说“连接另一库的完整路径”。每个正在运行的任务保持自己的库选择；新任务使用最近保存的配置。

## 操作范围与备份

| 工具 | 用途 |
|---|---|
| connection_status / connect_vault | 查看连接、自选库、选择只读/读写、记住配置 |
| list_notes / search_notes / read_note | 分页浏览、文件名/正文搜索、读取并返回内容哈希 |
| write_note / append_note | 新建、修改、追加内容 |
| move_note / delete_note | 移动或删除单篇笔记 |

已有笔记操作要求先读取，随后传入 `sha256`。内容变化后旧哈希会被拒绝，需要重读并合并。
这是操作前的冲突检查，不是跨进程事务锁；编辑期间请避免其他程序同时改写同一篇笔记。
覆盖、追加、移动、删除前都保存原始字节备份，工具结果包含 `backup` 路径。
需要恢复时，让 Codex 读取该备份，再按通常的读写流程恢复到指定笔记。

配置位于 `~/.obsidian-codex/connection.json`，备份位于 `~/.obsidian-codex/backups/`。
这些本机文件不包含在插件分享包中。备份不会自动清理。

仅操作 `.md` 和 `.markdown`，单篇上限 2 MiB；`.obsidian` 等隐藏目录、符号链接和目录联接不开放。
搜索返回 `truncated`、`skipped` 时不能视为全库检索完成。大库建议指定子目录缩小搜索范围。
移动/重命名**不会自动修正其他笔记的 wikilinks**，可让 Codex 搜索入链后按要求修改。
不提供 PDF/OCR、图片编辑、Canvas 编辑、语义向量检索或 Obsidian 图形界面控制。

## 分享

推荐分享 [GitHub 仓库](https://github.com/ChengChenNO1/obsidian-vault-reader)，让对方使用上面的 marketplace 命令安装。
也可以从 Codex 的插件分享入口分享，或发送独立插件 ZIP 包，让对方解压并运行 `python scripts/install.py`。
GitHub 下载的仓库 ZIP 内，插件文件位于 `plugins/obsidian-vault-reader/` 子目录。
对方连接自己的库，包里不携带你的笔记、库路径、备份或凭据。
这是在本机运行的 Codex 插件；普通 ChatGPT 网页不会因为安装这个包就获得本地磁盘访问能力。
从笔记读取的内容会返回给发起调用的 Codex 会话；本插件不另建云端索引、不把库上传到第三方服务。

## 来源与实现

检索与核对日期：2026-09-03。

- 采用 [trsdn/obsidian-mcp](https://github.com/trsdn/obsidian-mcp)，PyPI 包 `trsdn-obsidian-mcp==0.1.2`，MIT 许可。
  源码核对版本：`08fe44954c8378aceec0dd0e9afefc09d9f61f99`。
  实际复用其读取、写入、追加、移动、删除实现；适配层添加库选择、权限、备份、冲突检查和路径检查。
- 使用 [FastMCP](https://github.com/PrefectHQ/fastmcp) `3.4.7` 提供 stdio MCP 工具。
- 比较过 [cyanheads/obsidian-mcp-server](https://github.com/cyanheads/obsidian-mcp-server)：功能更广，但依赖 Obsidian Local REST API，当前需求选择直接读取本地文件的方案。
- 修正上游在 Windows 上按冒号解析 ripgrep 输出导致盘符识别错误的问题：本适配层采用 Python 的受限文本搜索。
- [Codex 插件文档](https://learn.chatgpt.com/docs/plugins)；`.mcp.json` 使用相对 `cwd`，不绑定开发者电脑的绝对路径。

本适配层与上游项目独立维护，非 Obsidian/OpenAI 官方插件；上游项目仍处于早期阶段。
操作检查约束本插件工具，不构成操作系统级沙箱。

## 开发与验证

```powershell
uv run --frozen python scripts/verify.py
```

验证在临时测试库中通过真实 MCP stdio 连接执行，包括中文路径、权限、备份、哈希冲突、路径越界、增改移删、恢复和重启配置。
2026-09-03 已在 Windows + Python 3.14 上通过上述验证、安装器隔离验证以及安装副本的 MCP 启动验证。
macOS/Linux 路径使用跨平台实现，但尚未在对应操作系统实机验收。
新增功能后同步更新 `agent.md`。发布时只打包源文件，排除 `.venv`、缓存、运行数据及真实知识库内容。
