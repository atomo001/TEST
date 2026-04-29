# Recovery Assistant Native (Rust 主体构建)

你提到“主题”是指**编译型主体语言**，本版本已将 MVP 主体改为 **Rust** 实现（可编译二进制），而不是 Python 作为主运行时。

## 架构
- `native/src/main.rs`：Rust HTTP 服务入口（本地 127.0.0.1:8787）。
- `native/src/parser.rs`：PhotoRec 输出解析（进度、文件列表）。
- `native/src/task.rs`：任务状态管理（pending/running/completed）。
- `native/src/runner.rs`：外部命令执行封装。
- `native/static/*`：前端页面（默认 Rust 风格主题）。

## MVP 功能
- 选择磁盘/分区（输入源路径）
- 开始扫描
- 展示扫描进度
- 展示可恢复文件列表
- 输出日志
- 默认只读扫描流程

## 运行
```bash
cd native
cargo run
```
浏览器打开 `http://127.0.0.1:8787`

## 测试
```bash
cd native
cargo test
```

## 安全说明
- 默认只读扫描。
- 所有写入型恢复动作必须在后续版本走显式二次确认（本版保留接口方向）。
