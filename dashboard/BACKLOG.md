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

### M6 验收 — ✅ PASS（同端口 MCP，零 LLM 端到端；LLM 路径受 402 阻塞）

- **交付物**：
  - 新增 `backend/mcp_server.py`：`mcp.server.MCPServer(name="llmworld")` + **18 个手写工具**（无 OpenAPI 自动转换），全部复用既有后端服务。
  - `backend/main.py`：`app.mount("/mcp", asgi_app)` 走既有 **defensive try/except** 模式（成功 → `ATTACHED`，失败 → `MISSING`）；
    lifespan 内 `async with server.session_manager.run()`（Starlette 不会运行挂载子应用的 lifespan）；
    CORS 增 `expose_headers=["Mcp-Session-Id"]` 并显式放行 `Mcp-*` 请求头；
    新增纯 ASGI `_McpPathNormalizer` 把裸 `/mcp` 改写为 `/mcp/`，**消除 307**（部分 MCP 客户端不跟随重定向）。
  - `requirements.txt`：新增 `mcp>=2.0`。
- **工具清单（18）**：`list_worlds` `create_world` `delete_world` `get_build_state` `get_build_preview` `run_build_step`
  `list_jobs` `get_job` `cancel_job` `list_llm_calls` `get_llm_call` `get_artifact` `put_artifact`
  `list_runs` `get_run_meta` `run_simulation` `get_day_replay` `get_snapshot`。
  - 复用映射：`store.list_worlds`/`list_runs`/`run_meta`；`world_admin.create_world/delete_world/build_state/build_preview`；
    `jobs.create_job`（build/simulate，`confirm=True` 才放行）/`list_jobs`/`get_job`/`cancel_job`；
    `llm_trace.list_calls`/`get_call`；`artifacts.read_artifact`/`write_artifact`；`derive.build_day_replay`/`build_snapshot`。
  - token 把关：`run_build_step`/`run_simulation` 均带 `confirm: bool = False`，未确认即明确拒绝（与 REST 一致）。
- **证据（真实 MCP 客户端，`%TEMP%\mcp_probe.py`，连 `http://127.0.0.1:8000/mcp`）**：
  - `initialize` → server `llmworld@0.1.0`；`tools/list` → **18** 个，名字与上表完全一致。
  - `list_worlds` → `isError=false`。
  - `create_world {world_id:"m6_probe_59610"}` → `{created:true, world_dir:output/worlds/m6_probe_59610}`（零 LLM）。
  - `get_build_state` → `exists=true`，`types.runnable=true`，其余三步 `blocked_reason` 正确。
  - `run_build_step {step:"types"}`（缺 confirm）→ `isError=true`，文本：
    `refusing to run a token-costly build step: pass confirm=True …`。
  - `delete_world` → `{existed:true, deleted:true, moved_to:output/_trash/m6_probe_59610_20260915_180650}`。
- **认证**：`MCP_TOKEN` 未设置 → `/mcp` 直接可用（localhost）；设置后由 `BearerTokenGate` 强制
  `Authorization: Bearer <MCP_TOKEN>`。进程内实测：无头/错头 → **401**（`WWW-Authenticate: Bearer`，响应体不含 token）；
  正确头 → 200；令牌未设置 → 透明放行。token 从不打印/记录。
- **传输/跨域**：非 localhost `Host` → **421**；`OPTIONS` 预检 200 且 `access-control-allow-headers` 回显 `mcp-session-id,…`；
  简单响应含 `access-control-expose-headers: Mcp-Session-Id`；裸 `POST /mcp` → **400**（非 307，重定向已消除）。
- **验收门**：后端 `py_compile` 全绿；红线扫描 0 违规；`/api/health` → `routers=[…,"mcp"]`、`missing_routers=[]`（dashboard 仍正常）。
- **环境说明（必要兼容）**：本机 dev server 的解释器把 venv `site-packages` 经 `sys.path` 注入而非 `site.addsitedir`，
  导致 `pywin32.pth` 未执行、`import mcp` 在 `pywintypes` 处失败。`mcp_server.py` 在 import `mcp` 前做了**幂等的 `.pth` 补偿**
  （仅当 `pywintypes` 不可导入时触发），恢复 site 本会做的路径注册。
- **客户端配置**（根键不同！）：
  ```jsonc
  // Claude Code / Cursor —— 根键 "mcpServers"
  { "mcpServers": { "llmworld": { "type": "http", "url": "http://127.0.0.1:8000/mcp",
    "headers": { "Authorization": "Bearer ${MCP_TOKEN}" } } } }
  // VS Code —— 根键是 "servers"，不是 "mcpServers"
  { "servers": { "llmworld": { "type": "http", "url": "http://127.0.0.1:8000/mcp" } } }
  ```
- **待补（受 402 阻塞）**：`run_build_step`/`run_simulation` 的 **LLM 成功路径**（与 M2/M5 同因账户余额耗尽），
  `confirm=True` 的作业提交与状态机已由 REST/M2 证；MCP 侧复用同一 `jobs.create_job` 路径。

### M7 验收 — ✅ PASS（用户授权最小改 `src/`）

- **授权**：用户确认「允许 M7 最小改 `src/`」——仅 config 旋钮 env 化 + 真重试 + 死配置清理；不动模拟/政策/prompt 语义。
- **`src/config.py`（最小改）**：`MODEL`/`TEMPERATURE`/`MAX_TOKENS`/`REQUEST_TIMEOUT_SECONDS`/`MAX_RETRIES`/`RETRY_BACKOFF_SECONDS`
  改为 `os.getenv("LLMWORLD_*", <原默认>)`；删除**确证死配置** `DEFAULT_DAYS`/`ENV_MODE`/`ENV_MANUAL_FILE` + `git rm src/env_manual.json`。
  ⚠️ **修正 §12.2**：`DEFAULT_START_DATE` **并非死配置**（被 4 个 simulate step 使用：`s1_macro_plan`/`s2_coordinate`/`s3_enrich`/`s4_appliance_decision`），**保留**。
- **`src/engine/subagent.py`（最小改）**：`call_with_retry` 由「直接转发」改为**真重试**（`retryable` 错误 + `MAX_RETRIES` + 线性退避）；`single_call` 已委派它 → 覆盖所有 step 调用路径。
- **新增** `backend/settings.py` + `GET/PUT /api/settings`（写 `dashboard/settings.json`，已 gitignore）+ `/api/health` 增 `settings`；
  `jobs.py` 用 `settings.job_env()` 把 6 个 `LLMWORLD_*` 注入**每个**作业子进程（build 作业另带 `LLM_TRACE_FILE`）；移除已被取代的 `build.build_env`（无死代码）。
- **新增前端「设置」面板**：`SettingsPanel.tsx` + `useSettings.ts` + `client.putJson/getSettings/updateSettings`。
- **验收口径证据**：`LLMWORLD_MODEL=probe-model-xyz` → `src/config.py` `MODEL=probe-model-xyz`（env 覆盖生效）；
  UI 改模型 → 保存 → `GET /api/settings` 与 `settings.json` 均为新值、`git check-ignore` 确认不入库；随后恢复默认。
- **回归**：`python -m unittest discover -s tests` → **Ran 298 tests, OK**（src 改动未破坏研究）。
- **验收门**：`py_compile` 全绿；`npx tsc -b` / `npm run build` / `npm run lint` exit 0；红线扫描 0 违规。

### M8 验收 — 🟡 部分完成（文档齐备；LFS 迁移待批）

- **已交付（安全、无历史改写）**：
  - 根 `LICENSE`（**MIT**，用户决策 #2）；
  - 根 `README.md`（一条命令起服务 + MCP 客户端配置 + 研究用法 + 测试 + 数据/LFS 说明）；
  - `.env.example`（仅键名与占位，**不含任何密钥**；含 6 个 `LLMWORLD_*` 旋钮 + `MCP_TOKEN`）；
  - `import/README.md`（数据来源说明：`world/Melbourne/3168` 源自 ABS 2021 普查 CC BY 4.0；
    `persona/synthetic_*.csv` 为**合成**属性表、上游来源未记录，需作者确认）。
- **核验纠偏（对 §12.2 的两处修正）**：
  - `import/` 实测 **1048 MB / 45 文件**（≈1.09 GB 属实）；
  - `stats.csv` **整文件合法 UTF-8**（BOM + 6,778,936 B 全量 `decode('utf-8')` 通过；`gbk` 在 byte 79 失败）
    → §12.2 的「GBK 乱码」为**控制台显示假象**，**无需改编码**；
  - `dimension_map.json` **确不存在**，但 `reader.py`/`sampler.py` 缺失时**优雅回退英文标签**（不崩），故非阻塞。
- **阻塞（需用户批准）**：让 `import/` 真正「新克隆不含 1.1 GB」需 `git lfs migrate import`（**重写历史**），
  而 §12.0 明令「禁止 `rebase`/`filter-branch`/`gc --prune`」（为保留 `output/` 可恢复）。二者冲突 → 见 §12.4 决策 #1。

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
| **M6** | MCP 同端口挂载 + ~15 工具 + 认证 | `curl /mcp` 通；客户端能建世界并跑一步 | ✅ **PASS（本会话，MCP 客户端端到端；LLM 需余额恢复）** |
| **M7** | 设置面板 + 死配置清理 + 真重试 | 面板改 `MODEL` 后下一次调用生效 | ✅ **PASS（本会话，UI 保存→config 生效实测；298 测试仍绿）** |
| **M8** | 开源化：git 清理、LICENSE、README、`.env.example`、编码修复 | 新克隆一条命令跑起来，不含 1.1 GB 数据与密钥 | 🟡 **部分完成**：MIT `LICENSE` + 根 `README.md` + `.env.example` + `import/README.md`（数据说明）**已交付**；**LFS 迁移受 §12.0「禁止重写历史」阻塞（待批）**；`stats.csv` 经字节级核验**本就是合法 UTF-8**（§12.2 的「GBK 乱码」为控制台显示假象） |

## 2. §12.4 其余待决策

| # | 决策 | 状态 |
|---|---|---|
| 1 | `import/` ≈1.09 GB 人格 CSV（已跟踪）：LFS / 下载脚本 / 移出仓库 | ✅ **已决策：Git LFS**；⚠️ 真正迁移（`git lfs migrate`）会**重写历史**，与 §12.0「禁止 rebase/filter-branch/gc --prune」冲突 → **待用户批准重写** |
| 2 | LICENSE：MIT / Apache-2.0 / GPL-3.0 | ✅ **已决策：MIT**（根 `LICENSE` 已加） |
| 3 | MCP 认证：纯 localhost / 静态 Bearer（推荐） | ✅ **已实现「超集」**：默认纯 localhost（非 localhost → 421）+ 设 `MCP_TOKEN` 则强制 Bearer（401）；两个选项均覆盖，可随时切换 |
| 4 | 6 个未提交后端文件：验证后收编 / 回滚 | ✅ **已决策：收编（已验证）** |
| 5 | 「停掉所有开发任务」范围 | ✅ 按 §12 边界默认**仅 dashboard**（不碰研究闭环） |

## 3. 验收门（§12.5.4）

- 后端 `py_compile`：**全绿**
- 研究回归：`python -m unittest discover -s tests` → **Ran 298 tests, OK**（M7 改 `src/` 后仍绿）
- `npx tsc -b`：**exit 0**
- `npm run build`：**exit 0**（`vite` 对 `<script src="/config.js">` 的 stderr 提示为无害，退出码 0）
- `npm run lint`：**exit 0**（仅既有 warnings，新文件 0 违规）
