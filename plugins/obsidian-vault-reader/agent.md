# 项目事项

- 目标：可分享的 Codex 插件，使用者自行选择 Obsidian 库，在 Codex 内查询和操作笔记。
- 用户补充要求：支持修改；实现可选只读/读写、创建、更新、追加、移动、删除、备份及修改冲突检查。
- 用户已批准在插件目录创建 README.md 和 agent.md。库的内容、路径配置不进入分享包。
- 上游：trsdn/obsidian-mcp 0.1.2（MIT），FastMCP 3.4.7；依赖由 uv.lock 固定。
- 已完成：库选择、本机配置、9 个 MCP 工具、上游读写适配、独立配置/备份、安装器和分享说明。
- 已发现上游 Windows ripgrep 输出按冒号拆分会误解析盘符；适配层使用受限的 Python 内容搜索。
- 每次功能结束更新本文件；不要将真实笔记放进测试或分享包。

## 2026-09-03 验收结果

- Windows + Python 3.14：真实 stdio MCP 握手及 9 个工具 schema 通过。
- 临时库：中文路径、CRLF、正文/文件名搜索、只读拦截、路径越界/隐藏目录/符号链接拦截通过。
- 新建、修改、追加、移动、删除、原始字节备份、恢复、旧哈希拒绝覆盖通过。
- 分页、切换库和保存配置后重启读取通过。
- 分享安装器：新目录复制、保留现有 marketplace 条目、重复注册不重复添加、拒绝覆盖另一源目录通过。
- 插件及 skill 校验通过；skill 校验在 Windows 上须用 `python -X utf8`，以避开校验脚本默认 GBK 编码。
- Codex 已安装并启用；使用安装副本的 `.mcp.json` 启动验证通过，返回 9 个工具，初始无库选择。
- 未连接真实知识库，也未修改任何实际笔记。用户在新 Codex 任务指定库路径后开始使用。
- 分享包使用安装器的 FILES 白名单；不打包运行环境、配置、备份、真实笔记。
- 限制：跨进程写入非事务；移动不自动修复入链；2 MiB/篇；仅 Markdown；未在 macOS/Linux 实机验收。

## GitHub 发布

- 用户明确要求上传 GitHub，供其他 Codex 直接安装；公开目标为 `ChengChenNO1/obsidian-vault-reader`。
- 远程 marketplace 名称为 `obsidian-vault`，插件位于仓库 `plugins/obsidian-vault-reader/`。
- 仓库仅从安装器 FILES 白名单复制；保留本机个人 marketplace 安装。
- 远程安装入口及验证进展记录在发布仓库根目录 `agent.md`。
