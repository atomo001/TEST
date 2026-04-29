# Recovery Assistant MVP (基于 TestDisk / PhotoRec)

## 1. 整体技术方案

### 1.1 目标
本项目将 TestDisk / PhotoRec 的底层能力封装为面向普通用户的图形化恢复工具，默认只读扫描，降低误操作风险。

### 1.2 TestDisk / PhotoRec 可复用能力分析
- **TestDisk**：分区表识别、分区结构检测、引导区修复、磁盘设备枚举。
- **PhotoRec**：RAW 扫描与文件签名恢复、按类型恢复、恢复日志输出。
- **复用方式**：本项目通过 `TestDiskAdapter` 统一构造命令并调用外部二进制，不重写底层恢复算法。

### 1.3 新架构设计
- **UI 层（FastAPI + HTML/JS）**：向导式页面，支持扫描、进度、过滤、恢复目录设置。
- **恢复任务调度层（TaskManager）**：任务状态机、进度更新、日志记录。
- **TestDisk 调用封装层（TestDiskAdapter + CommandRunner）**：命令拼装、超时控制、错误处理。
- **结果解析层（PhotoRec Parser）**：从日志/输出中解析进度与可恢复文件列表。
- **完整性校验层（MVP 占位）**：预留 hash/文件可读性校验扩展点。

### 1.4 安全策略
- 默认恢复流程为只读扫描。
- 对写分区表、修复引导区、覆盖写入等高风险操作强制二次确认。
- 全程日志留存，便于追踪与审计。

---

## 2. 目录结构

```text
src/recovery_app/
  app.py                     # FastAPI 入口
  core/
    command_runner.py        # 外部命令执行/超时/错误处理
  services/
    testdisk_adapter.py      # TestDisk/PhotoRec 统一封装
    task_manager.py          # 任务状态管理
  parsers/
    photorec_parser.py       # 输出与进度解析
  models/
    types.py                 # 数据模型/状态定义
  ui/
    templates/index.html     # 图形界面
    static/style.css         # 样式
    static/app.js            # 前端交互逻辑
tests/
  test_parser.py
  test_runner_and_task.py
```

---

## 3. MVP 功能实现范围

已实现：
- 选择磁盘/分区（输入源路径）。
- 开始扫描。
- 展示扫描进度。
- 展示可恢复文件列表。
- 文件类型筛选。
- 选择恢复目录。
- 执行恢复请求（MVP 为接口接收与风险确认返回）。
- 输出恢复日志。

说明：当前仓库中的扫描流程为 **MVP 演示模式**（模拟进度+示例恢复条目），用于验证架构与交互。接入真实二进制后，直接复用 `CommandRunner + TestDiskAdapter + Parser` 即可。

---

## 4. 安装与运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn recovery_app.app:app --reload
```

打开：`http://127.0.0.1:8000`

---

## 5. 测试

```bash
pytest -q
```

覆盖重点：
- 命令封装执行。
- 结果解析。
- 任务状态管理。

---

## 6. 限制与后续增强

- MVP 当前未直接驱动真实 `photorec` 长时输出流（使用模拟流程）。
- 未实现文件预览缩略图与恢复后哈希一致性校验（已预留架构）。
- 后续可加入：
  - 实时子进程输出流解析。
  - 分区修复向导与二次确认弹窗。
  - 恢复结果完整性报告（hash、可读性、文件分类统计）。

---

## 7. 安全注意事项

- 除非你明确确认风险，不要执行任何写盘操作。
- 建议恢复到独立磁盘目录，避免覆盖原始数据。
- 建议先制作磁盘镜像，再在镜像上执行恢复尝试。
