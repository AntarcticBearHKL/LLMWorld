# LLMWorld

LLM-driven synthetic household energy simulator + research console.

A five-stage LLM pipeline generates households (types → personas → household →
assemble) and then simulates a day of activity and appliance-level electricity
use. A local dashboard lets you build worlds step by step, watch every LLM call,
run simulations, and replay the result — and the same server exposes an MCP
endpoint so an agent can drive it without a browser.

## Requirements

- Python **≥ 3.10**
- Node.js **≥ 20** (for the dashboard UI) and `npm`
- `git` (with [Git LFS](https://git-lfs.com) for the persona dataset)
- A DeepSeek API key (the pipeline calls the LLM)

## Quick start

```powershell
# 1. clone (Git LFS pulls the persona dataset)
git lfs install
git clone https://github.com/AntarcticBearHKL/LLMWorld.git
cd LLMWorld

# 2. python env + dependencies
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r dashboard\requirements.txt
.venv\Scripts\python.exe -m pip install -e .

# 3. secrets
copy .env.example .env      # then edit .env and set DEEPSEEK_APIKEY

# 4. build the dashboard UI once
cd dashboard\web
npm install
npm run build
cd ..\..

# 5. run (from the dashboard/ directory)
cd dashboard
..\.venv\Scripts\python.exe -m uvicorn backend.main:app --port 8000
```

Open <http://127.0.0.1:8000>. The single port serves the UI, the REST API
(`/api/*`) and the MCP endpoint (`/mcp`).

Health check: `curl http://127.0.0.1:8000/api/health`.

## The dashboard

| View | What it does |
|---|---|
| 构建 | Create an empty world, then build it step by step (类型 → 人格 → 家庭 → 装配). Each step shows what it reads/writes, runs as a job, and reveals the exact prompts and responses with timing. |
| 生成 / 模拟 | One-shot world generation and day-by-day simulation (both spend LLM tokens). |
| 观看 (小镇 / 住户网格 / 住户详情) | Replay a simulated day: a top-down town, a household grid, and a per-member timeline. |
| 任务 | Job queue, live logs. |
| 设置 | Model / temperature / token / retry knobs, applied to the next job. |

The build pipeline is pure file-driven; the dashboard only orchestrates it and
never reimplements research logic.

## MCP (drive it without a browser)

The server mounts an MCP app at `http://127.0.0.1:8000/mcp` (18 hand-written
tools: worlds, build steps, jobs, artifacts, LLM traces, runs).

```jsonc
// Claude Code / Cursor  — root key is "mcpServers"
{ "mcpServers": { "llmworld": { "type": "http", "url": "http://127.0.0.1:8000/mcp" } } }

// VS Code — root key is "servers", NOT "mcpServers"
{ "servers": { "llmworld": { "type": "http", "url": "http://127.0.0.1:8000/mcp" } } }
```

By default it is reachable on localhost only. Set `MCP_TOKEN` in the environment
to additionally require `Authorization: Bearer <MCP_TOKEN>`.

## Command line (research pipeline)

```powershell
# world generation
.venv\Scripts\python.exe run.py --mode world --world world_demo --count 2

# one day of simulation (always pass an explicit --date)
.venv\Scripts\python.exe run.py --mode simulate --world world_demo --house 0 --member 0 --date 2026-09-11 --days 1
```

## Data

`import/` holds the inputs the pipeline reads. See
[`import/README.md`](import/README.md) for provenance and licensing. The persona
dataset (`import/persona/synthetic_*.csv`, ~1.0 GB) is stored with **Git LFS**
and is required for persona sampling.

## Tests

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests
```

## License

MIT — see [`LICENSE`](LICENSE).
