# Dashboard 开发 Backlog 执行记录

> 本文件跟踪 goal.md §12（Dashboard 控制台开发，M1–M8）的执行状态与验收证据。
> 边界：只覆盖 `dashboard/`；不涉及 §1–§11 的研究闭环。

## 0. 会话记录（2026-09-15，接手 §12.0 冻结状态）

### 决策项 4（§12.4）：`收编` — 已由用户确认

§12.0 的 6 个未提交后端文件**全部收编**，并完成功能级验收（此前从未真正建过世界/跑过一步）。

**静态验收（0 token）**
- `py_compile`：6/6 通过。
- 红线扫描（`as any` / `@ts-ignore` / `@ts-expect-error` / `# type: ignore` / 裸 `except:` / `TODO` / `FIXME`）：0 违规。
- 运行时契约逐项核对源码，全部命中：
  - `src/generate_world.py:174 init_world()` 写 `world.json` 并返回 `(world_dir, log_dir)`；
  - `world_admin.POSTCODE="3168"` = `generate_world.CLAYTON_POSTCODE`；`import/world` 仅有 `Melbourne` = 默认配置；
  - `build.py` 生成的 argv 与 s1–s4 四模块 `main()` 的 argparse（`--world/--house/--count/--seed`）完全一致；
  - s4 非幂等已证实（`update_world_meta` 无条件 `.append`）→ `_dedup_households_meta` 去重目标精准。

### M1 验收 — ✅ PASS（零 LLM）

经 `http://127.0.0.1:8000` 实测（`GET /api/health` → `routers=["worlds","replay","jobs","build"]`，`missing_routers=[]`）：

| 用例 | 结果 |
|---|---|
| `POST /api/worlds {world_id:"m1_probe"}` | `created=true`；`output/worlds/m1_probe/world.json` 存在且内容正确（Melbourne / 3168） |
| 重复 POST 同 id | `created=false`（幂等） |
| `POST /api/worlds {world_id:"bad id!"}` | **400** + 可读原因（非法字符） |
| `GET /api/worlds/{w}/build` | `exists=true`、`houses=[]`、`steps=4`，各步 `runnable`/`blocked_reason` 正确 |
| `DELETE /api/worlds/{w}` | 可恢复删除 → `output/_trash/m1_probe_<ts>/`；原目录消失 |
| 删除后再 `GET .../build` | **404** `world not found` |
| 再 `DELETE` 同 id | `existed=false`（幂等） |
| 零 LLM 证明 | `GET /api/jobs` 计数 `0 → 0`，创建空世界不产生任何 job |

### M2 验收 — ✅ PASS（§12.0 口径：建世界 / 跑一步 / 重跑 s4 不重复）

`assemble` 步骤 **0 LLM 调用**（`estimate` 自述 "no LLM calls"），用最小 fixture 走通真实 job 队列：

| 用例 | 结果 |
|---|---|
| 建 1 户世界的 fixture（`household_types.json` + `house_0001/household.json` + `aligned_texts.json` + `persona_provenance.json`），并**预置 `households.json` 含 2 条 house_0001 重复项 + 1 条 house_0002** | — |
| `POST /api/jobs {kind:"build", step:"assemble", house:"0", confirm:true}` | `estimate=0 calls`；真实子进程 argv = `... s4_world_assemble.py --world m2_probe --house 0 --seed 42`；`status=done` |
| run#1 后 `households.json` | 移除 2 条陈旧项，**house_0001 恰好 1 条**；house_0002 保留 |
| **重跑 assemble（run#2）** | **house_0001 仍恰好 1 条**（dedup 生效，M2 核心验收） |
| `.bak.<ts>` 备份 | ✅ `households.json` / `household.json` / `personas.json` 写前均生成 `.bak.<ts>` |
| `build_state` 收敛 | 4 步全部 `done=true` |
| `POST /api/jobs` 缺 `confirm` | **400**（拒绝昂贵作业） |
| 不存在的 world / 非法 step | **400 / 422** |
| `GET .../build/steps/assemble/preview` | reads/writes/overwrites 解析正确 |
| **失败路径**（真实 LLM `types` 步） | `status=failed` 且 `error` 可读：`build step 'types' exited with code 1: ... [JSON output failed] DeepSeek API error 402 ...` |

### M3 验收 — ✅ PASS（真实 trace 端到端）

- **后端**：`build.build_env()` 给 build 子进程注入
  `LLM_TRACE_FILE=<world>/<postcode>/log/llm_trace_<job_id>.jsonl`（**按 job 隔离** → 每条调用天然归属到某步，
  **零改动 `src/`**）；新增 `backend/llm_trace.py` 读取器 + `GET /api/jobs/{job_id}/llm-calls` 与
  `GET /api/jobs/{job_id}/llm-calls/{call_id}`。
- **前端**：新增 `StepInspector.tsx`（调用列表 + 提示词/响应/耗时/状态/失败详情），`JobsPanel` 为 build 作业给出
  「LLM 调用 | 实时日志」页签；`types.ts`/`client.ts`/`useJobs.ts` 同步（`JobKind` 增 `"build"`）。
- **证据（真实数据）**：跑 `types` 步 → 命中 DeepSeek **402** → 落盘 trace；浏览器（live 构建）实测 StepInspector
  显示 `#1 HTTP 402 失败 655 ms · 5.6k 字符`，详情含 模型 `deepseek-v4-flash`、完整**提示词**、**原始响应**
  （provider `raw_text` 402 JSON）。接口返回 `exists=true total=1 http=402 dur=0.655s ok=False`。
- **验收门**：后端 `py_compile` 全绿；`npx tsc -b` exit 0；`npm run build` exit 0；`npm run lint` exit 0；红线扫描 0 违规。
- 已知取舍：默认构建（`VITE_USE_MOCK` 未设）为 mock 模式；**live 构建需 `VITE_USE_MOCK=0`**，本会话 live 构建已实测通过（`dist/` 已 ignore）。

### M4 验收 — ✅ PASS

- **接口**：新增 `backend/artifacts.py`（路径限定在世界目录内，拒绝 `..` / 绝对路径 / 越界）+
  `GET /api/worlds/{world}/artifact?path=` 与 `PUT /api/worlds/{world}/artifact`。
- **安全契约**：写前自动 `.<name>.bak.<ts>`（新增文件不备份）；`.json` 先校验（非法 → **400，不落盘**）；
  返回 unified **diff** + 顶层类型变化 warning；父目录不存在 → **400**（提示先跑前置步骤）。
- **证据（真实数据）**：
  - 创建/读取/编辑：`created=true` → 再写 `changed=true` + `backup=<…>.bak.<ts>` + `diff`；`GET` 返回解析后的 `data`；
  - 非法 JSON / 路径穿越（`../../../.env`）/ 缺父目录 → 均 **400** 且原因可读；
  - **验收口径**：写 `house_0001/household.json`(3 成员) → `assemble` → `households.json` `members_count=3`；
    **手工改成 4 成员**（产生 `.bak`）→ 再 `assemble` → `members_count=4` → **下一步骤确用改后内容**；
    House_0001 仍恰好 1 条（M2 去重未破）。
- 前端编辑器 UI 归入 M5（世界详情构建面板）；M4 交付为**接口**，同时供 M6 的 `get_artifact`/`put_artifact` 复用。

### M5 验收 — 🟡 部分完成（构建工作区 + URL 复现已交付）

- **新增「构建」工作区**（`WorldBuilder.tsx` + `BuildStepCard.tsx` + `BuildPreviewList.tsx` + `useWorldBuild.ts`）：
  世界列表（`GET /worlds`）→ 新建空世界（`POST /worlds`，零 LLM）→ 删除（`DELETE`，可恢复）；
  右侧 4 步 stepper（类型/人格/家庭/装配）显示 `done/runnable/blocked_reason` + 住户级状态；
  每步 `运行` 经既有 `JobSubmitBar`（估算 → 确认 → 提交，`kind:"build"`）；读写预览 `GET .../preview`；
  每步挂 `StepInspector` 显示 LLM 交互（M3）。
- **URL 复现**：`?view=build&world=<W>&step=<S>`（`store/time.ts` 加 `build` 视图 + `world`/`step`；`useUrlSync.ts` PARAM_ORDER 扩展）。
- **证据（真实数据，浏览器 live 构建）**：新建空世界 `m5_probe`（`0 户 · world 目录已就绪`）→ stepper 正确门控
  （类型可运行；其余 `blocked_reason`）→ 预览 `world.json`/`info.md` EXISTS、`household_types.json` MISSING →
  估算 `1 次 LLM 调用` → 提交 `types` → 402 失败被可读渲染（`最近一次失败：… 402 …`）+
  `StepInspector` 显示 `#1 HTTP 402 失败 697ms · 5.6k 字符` + 模型 `deepseek-v4-flash` + 完整提示词。
- **修复**：`useJobLlmCalls` 在作业由「运行中」转「终态」时补拉一次（否则轮询停止后停在空结果 —— 已实测复现并修复）。
- **验收门**：`npx tsc -b` / `npm run build` / `npm run lint` 均 exit 0；红线扫描 0 违规。
- **待做（M5 余项）**：世界详情容器（构建 / 模拟 / 观看 三模式）、观看内 `小镇/网格/详情` 密度切换、`?mode=`/`?density=` 参数。

### ⚠️ 外部阻塞：DeepSeek API **402 Insufficient Balance**

**账户余额耗尽**，导致 `types/personas/household` 的 **LLM 成功路径无法实测**。
按 §10 安全熔断处理：切到 L0/L1，把能验证的全部验证（上表）。这是账户问题而非代码缺陷；代码侧 argv/去重/备份/job 管线/失败兜底均已证。
**待余额恢复后补验**：`types → personas → household` 的真实成功路径。

## 1. M1–M8 状态

| M | 内容 | 验收口径 | 状态 |
|---|---|---|---|
| **M1** | 世界 CRUD（`POST /worlds` 空世界、`DELETE`、`GET .../build`） | 建完 `world.json` 存在；零 LLM | ✅ **PASS（本会话验证）** |
| **M2** | 4 步构建接口 + job 化 + s4 去重 + 失败兜底 | 逐步骤跑完一户；重跑 s4 不重复 | ✅ **PASS（§12.0 口径）**；LLM 成功路径待余额恢复补验 |
| **M3** | `LLM_TRACE_FILE` 接入 + `StepInspector` 通用化 | 每步可见 prompt / 原始响应 / 耗时 / 失败原因 | ✅ **PASS（本会话，真实 402 trace 端到端浏览器核对）** |
| **M4** | 产物读写接口：`.bak.<ts>` + JSON 校验 + diff | 手改 `household.json` 后下一步骤使用改后内容 | ✅ **PASS（本会话，3→4 成员实测通过）** |
| **M5** | IA 重构：世界列表 → 世界详情（构建/模拟/观看）；URL 可复现 | 链接直接复现「某世界构建第 3 步」 | 🟡 **部分完成**：构建工作区 + `?world=&step=` URL 复现**已交付并实测**；世界详情三模式 / 观看内密度切换待做 |
| **M6** | MCP 同端口挂载 + ~15 工具 + 认证 | `curl /mcp` 通；客户端能建世界并跑一步 | ⬜ |
| **M7** | 设置面板 + 死配置清理 + 真重试 | 面板改 `MODEL` 后下一次调用生效 | ⬜ |
| **M8** | 开源化：git 清理、LICENSE、README、`.env.example`、编码修复 | 新克隆一条命令跑起来，不含 1.1 GB 数据与密钥 | 🔴 阻塞（§12.4 决策 1/2） |

## 2. §12.4 其余待决策

| # | 决策 | 状态 |
|---|---|---|
| 1 | `import/` ≈1.09 GB 人格 CSV（已跟踪）：LFS / 下载脚本 / 移出仓库 | ⬜ 待用户 |
| 2 | LICENSE：MIT / Apache-2.0 / GPL-3.0 | ⬜ 待用户 |
| 3 | MCP 认证：纯 localhost / 静态 Bearer（推荐） | ⬜ 待用户（阻塞 M6） |
| 4 | 6 个未提交后端文件：验证后收编 / 回滚 | ✅ **已决策：收编（已验证）** |
| 5 | 「停掉所有开发任务」范围 | ⬜ 待用户 |

## 3. 验收门（§12.5.4）

- 后端 `py_compile`：**6/6 OK**
- `npx tsc -b`：**exit 0**
- `npm run build`：**exit 0**（`vite` 对 `<script src="/config.js">` 的 stderr 提示为无害，退出码 0）
