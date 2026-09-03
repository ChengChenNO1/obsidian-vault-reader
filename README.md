# Obsidian 知识库助手 · Codex 插件

让 Codex 直接查询和修改你选择的本地 Obsidian 知识库。

支持中文路径、全文/文件名搜索、读取、新建、修改、追加、移动和删除 Markdown 笔记；修改前备份，并检查内容冲突。使用者自行选择库和只读/读写权限，无需 Obsidian REST API 或 API key。

## 直接安装

需要 **Codex CLI、Git 和 [uv](https://docs.astral.sh/uv/getting-started/installation/)**，并确保 `uv` 在 Codex 的 PATH 中。首次启动需要联网下载依赖；uv 可按需安装 Python 3.11 以上版本。

```sh
codex plugin marketplace add https://github.com/ChengChenNO1/obsidian-vault-reader.git
codex plugin add obsidian-vault-reader@obsidian-vault
```

或者将下面这段话发送给另一台电脑的 Codex：

> 请从 https://github.com/ChengChenNO1/obsidian-vault-reader 安装 Obsidian 知识库助手，检查 Git 和 uv，添加该仓库的 marketplace，再安装 obsidian-vault-reader@obsidian-vault。

安装后**新建一个 Codex 任务**，直接说：

> 使用 Obsidian 知识库助手，连接“我的知识库完整路径”，允许查询和修改。

Windows 路径示例：`D:\我的知识库`；macOS 路径示例：`/Users/你的用户名/Documents/我的知识库`。
插件不会自动猜测路径，也不会自动连接仓库作者的库。

连接后可以说：

- “搜索与项目复盘有关的笔记，给出来源。”
- “把计划.md 中这一段修改为……，保留其他内容。”
- “新建收件箱/想法.md，内容是……”
- “将旧笔记.md 移动到归档目录，检查需要更新的引用。”

## 范围与备份

- 直接读写 `.md` / `.markdown`，修改会反映到 Obsidian 中。单篇上限 2 MiB。
- 覆盖、追加、移动和删除已有笔记前备份；修改操作需要先读取并提供内容哈希。
- 本机配置和备份位于 `~/.obsidian-codex/`。插件代码中不包含使用者笔记、库路径或凭据。
- 移动不会自动修正其他笔记的 wikilinks；请同时要求 Codex 更新相关引用。
- 隐藏目录、符号链接和目录联接不开放；不支持 PDF/OCR、图片或 Canvas 编辑。
- 这是本地 Codex 插件。普通 ChatGPT 网页无法通过本插件直接访问电脑磁盘。

完整用法、限制和恢复方法见 [插件说明](plugins/obsidian-vault-reader/README.md)。

## 更新

```sh
codex plugin marketplace upgrade obsidian-vault
codex plugin add obsidian-vault-reader@obsidian-vault
```

更新后新建任务加载新版本。若 Codex 不认识 `plugin` 子命令，请先升级 Codex CLI。

## 实现与验证

基于 [trsdn/obsidian-mcp](https://github.com/trsdn/obsidian-mcp) 和 [FastMCP](https://github.com/PrefectHQ/fastmcp)，通过 `uv.lock` 固定依赖。
适配层增加自选库、权限、本机备份、冲突检查、路径检查和 Windows 中文搜索支持。

```sh
cd plugins/obsidian-vault-reader
uv run --frozen python scripts/verify.py
```

测试仅操作临时测试库。Windows 已验证读取、搜索、增改移删、备份恢复和边界检查；macOS/Linux 尚未实机验收。

本项目为独立社区插件，非 Obsidian/OpenAI 官方插件。MIT 许可；依赖保留各自许可。
