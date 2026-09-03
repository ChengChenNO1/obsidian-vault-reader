# 发布项目事项

- 用户授权将 Obsidian 知识库助手发布到 GitHub，供其他 Codex 直接安装。
- 公开仓库：`ChengChenNO1/obsidian-vault-reader`；marketplace：`obsidian-vault`。
- 插件标识保留 `obsidian-vault-reader`，当前包含 9 个查询与读写工具。
- 发布内容来自插件源码 FILES 白名单；实际笔记、用户连接、本机备份、依赖环境不得提交。
- 本仓库采用 `.agents/plugins/marketplace.json` + `plugins/obsidian-vault-reader/` 布局。
- 既有真实 MCP 功能测试已通过；本次验证重点为远程 marketplace 下载、安装和启动。
- 更新功能时同步修改本文件及插件目录 agent.md，发布前检查依赖锁和变更范围。

## 2026-09-03 发布验收

- 公开仓库已创建，默认分支 main；17 个发布文件均经白名单、凭据及本机绝对路径检查。
- 使用独立 Codex 测试配置，执行 GitHub marketplace add 和 plugin add，成功下载并安装远程插件。
- 根据下载副本的 `.mcp.json` 启动真实 MCP 服务，9 个工具均可发现，connection_status 返回未连接。
- 未选择或操作真实知识库；本机原有 personal 安装保持启用，并同步了 GitHub 说明及链接。
- 测试配置和结果仅保存在 gitignore 排除的 `.verification/` 中，不提交到 GitHub。
