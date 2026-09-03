# 发布项目事项

- 用户授权将 Obsidian 知识库助手发布到 GitHub，供其他 Codex 直接安装。
- 公开仓库：`ChengChenNO1/obsidian-vault-reader`；marketplace：`obsidian-vault`。
- 插件标识保留 `obsidian-vault-reader`，当前包含 9 个查询与读写工具。
- 发布内容来自插件源码 FILES 白名单；实际笔记、用户连接、本机备份、依赖环境不得提交。
- 本仓库采用 `.agents/plugins/marketplace.json` + `plugins/obsidian-vault-reader/` 布局。
- 既有真实 MCP 功能测试已通过；本次验证重点为远程 marketplace 下载、安装和启动。
- 更新功能时同步修改本文件及插件目录 agent.md，发布前检查依赖锁和变更范围。
