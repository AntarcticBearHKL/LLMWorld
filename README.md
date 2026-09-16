# LLMWorld

LLM-driven synthetic household energy simulator + research console.

A world is a set of **districts**. Each district gets an LLM-written description,
each household in it is composed by the LLM (member count/type → a persona
sampled from the local database → LLM-adapted), and then that household's
**rooms and all their appliances** are generated. The pipeline then simulates a
day of activity and appliance-level electricity use. A local dashboard lets you
build worlds district by district — create districts, generate descriptions
(preset or custom prompt), add households, generate homes, and preview every
house's rooms, people and appliances — watch every LLM call, run simulations,
and replay the result. The same server exposes an MCP endpoint so an agent can
drive it without a browser.

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
| Worlds | Every world at a glance (draft / frozen). Create a blank world, clone one, or delete one. |
| World detail → Households | The world's **districts**. Create a district (a blank name auto-generates a `district_<word>` id), generate its description from a preset or your own prompt, add households, then generate each home's rooms + appliances. Expand any household to preview its rooms, members and appliances inline. |
| World detail → Scenarios | The world's **scenarios** — each is a parallel version of the same households under its own policy, news and dates. Create one, then open it in Watch. |
| Watch | One day of a scenario, drilled down: world overview (all blocks) → block → household → indoors. The time play bar appears only here. |
| Jobs | Job queue and live logs. |
| Settings | Model / temperature / token / retry knobs, applied to the next job. |

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
# world generation: create districts locally, write each district description
# (a preset or your own --prompt), compose households, then their rooms + appliances
.venv\Scripts\python.exe run.py --mode world --world world_demo --districts "clayton,dockside" --preset clayton_3168 --households 1 --home

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
