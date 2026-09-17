# DESIGN.md — LLMWorld 研究控制台 (dashboard/web)

> 前端设计契约。所有颜色、字号、间距、圆角、动效必须回溯到本文件的 token。
> 组件不得出现硬编码色值 / 魔法数字。

## 0. Research Log (greenfield)

| 研究通道 | 交付物 | 结果 |
| --- | --- | --- |
| Layer A 风格技能 | `minimalist-skill.md`（Premium Utilitarian Minimalism） | **选用**。要点：颜色是稀缺资源，只用于语义；结构线一律 1px 极淡；卡片内边距慷慨（24–40px）；禁止重阴影；动效"存在但不可察觉"；禁止 emoji。 |
| Layer B 品牌系统 | `sentry.md`（Dark dashboard, data-dense） | **选用**。要点：深色优先且**绝不使用纯黑**（用带色调的深底）；微标签大写 + 字距；按钮内阴影带来"可按压"的实体感；层级表面用磨砂玻璃 `blur(18px) saturate(180%)`；单一高可见度强调色，克制使用。 |
| Layer B 备选（未选） | `kraken.md`、`cohere.md` | 未选原因：Kraken 紫色系与"能源/仪表"语义无关；Cohere 的鲜艳渐变与"安静、数据密集"的诉求冲突。 |
| 偏离记录 | Lucide 图标 | `minimalist-skill` 禁用 Lucide；但任务明确要求 `lucide-react`。**接受该偏离**，以统一 1.5px 线宽、统一 16/14px 尺寸来保证一致性。 |
| **Re-skin lane（第二轮）** | `kanvana/client/src/styles/tokens.css` · `layout.css` · `components/*.css` · `infinite-canvas/web/src/styles/globals.css` | **选用并已落地**。cocoa 纸张（`#fbfaf7` / `#1f1d1a`）、同一套磨砂玻璃、cocoa 中性作为唯一交互色、语义色只服务状态、Baloo 2 字体、`--r-md/xl/pill` 半径与三档大而软的阴影。第一轮的青绿 × 琥珀与深青黑底色整体废弃，见 §15。 |

**重组结论（已废弃，仅存档）**：底色由 Sentry 的深紫改为**深青黑**（能源/仪表的冷色仪器感），强调色用**青绿**，`on` 语义用**暖琥珀**。该方案已在第二轮被 Warm Cocoa 取代。

**重组结论（现行）**：暖可可纸面 + 同一套磨砂玻璃 + Baloo 2 圆体。交互色只用一个"可可中性"（近黑 / 近白），颜色预算全部留给状态语义；圆角、间距、阴影从 `--r-*` / 4px 基准 / `--shadow-*` 取值，组件层由 `card` / `chrome` / `chip` 三件套统一。

## 1. Design Principles

1. **Warm cocoa paper, frosted chrome** — a warm light-cocoa paper in light, a warm dark-cocoa paper in dark, and the *same* frosted-glass chrome in both. Every surface is either opaque `card`/`paper` or `glass`/`chrome`; a half-transparent fill without blur is never used, because the dot grid would show through it.
2. **The cocoa neutral is the interaction colour** — primary buttons, active nav, selected rows and active chips are near-black on cream (light) / near-white on cocoa (dark). The product has no decorative accent.
3. **Colour is state only** — `--danger`, `--success`, `--energy`, `--info` describe a real state (failed / done / drawing power / frozen). They never appear as a plain button fill, a decorative border or a section tint.
4. **Rounded and generous** — Baloo 2 (400–800) for the whole UI, radii from `--r-sm` to `--r-pill`, card padding 12–16px, page gutters 12–16px, one large soft shadow per floating surface.
5. **Data is still monospaced** — time, watts, kWh, ids and counts keep the `num` utility (`--font-mono` + `tabular-nums`) so digits never reflow.
6. **Motion serves meaning** — only `transform` / `opacity` / colour; hover lifts a card, active presses a button, `enter` cascades a group. No decorative animation.

## 2. Colour System

All values are CSS variables in `src/index.css`; dark is the `:root` default and light is the `.light` override on `<html>`.
Components may only use `var(--…)` or the Tailwind token classes (`bg-surface`, `text-fg-muted`, `border-border`, `bg-brand`, `text-brand-fg`, `bg-brand-soft`, `bg-item-hover`, `text-danger`, …).

### Surfaces / text

| Token | Dark | Light | Use |
| --- | --- | --- | --- |
| `--bg` | `#181715` | `#f4f2ed` | page (carries the dot grid) |
| `--surface` | `#1f1d1a` | `#fbfaf7` | cards, panels, drawers |
| `--surface-2` | `#292524` | `#e7e5df` | nested areas, inputs (dark), chips |
| `--surface-3` | `#33302b` | `#dcd9d1` | raised neutral, tracks |
| `--border` | `#44403c` | `#d6d3ca` | 1px structural line |
| `--border-strong` | `#57534e` | `#b8b4a8` | inputs, chip outlines |
| `--fg` | `#f5f5f4` | `#292524` | primary text |
| `--fg-muted` | `#d6d3d1` | `#78716c` | secondary text |
| `--fg-subtle` | `#a8a29e` | `#a8a29e` | micro labels, units |

### Cocoa neutral (interaction)

| Token | Dark | Light | Use |
| --- | --- | --- | --- |
| `--brand` | `#fafafa` | `#171717` | primary fill, focus outline, cursor |
| `--brand-fg` | `#171717` | `#ffffff` | text on the primary fill |
| `--brand-soft` | `white 10%` | `black 6%` | selected row / soft cocoa wash |
| `--brand-ring` | `white 25%` | `black 12%` | focus ring, selected outline |
| `--item-hover` | `white 8%` | `black 6%` | hover wash |
| `--item-selected` | `white 12%` | `black 10%` | selected wash |
| `--overlay` | `black 60%` | `black 32%` | modal scrim |
| `--on-danger` | `#171717` | `#ffffff` | text on `--danger` |

### Semantic (state only)

`--energy` (drawing power / queued / running) · `--energy-soft` · `--success` (done) · `--danger` (failed) · `--info` (frozen world) — plus the matching `*-soft`/tint washes used by status chips.

### Glass

| Token | Value |
| --- | --- |
| `--glass-bg` | dark `rgb(31 29 26 / .72)` · light `rgb(251 250 247 / .72)` |
| `--glass-bg-opaque` | `#1f1d1a` / `#fbfaf7` |
| `--glass-border` | `white 10%` / `black 10%` |
| `--glass-blur` | `blur(24px) saturate(150%)` |
| `--glass-blur-lg` | `blur(40px) saturate(150%)` |

Glass text always uses `--fg` / `--fg-muted`; the 72% cocoa wash already darkens/lightens the backdrop, and light text on it never drops below the muted contrast floor.

### Canvas

`--dot-color` + `--dot-tile` (22px) paint the dot grid on `body`. `--member-1..4` identify members; `--cat-*` classify activities. Neither is semantic and neither may be reused for UI chrome.

## 3. Typography

| Role | Font | Spec |
| --- | --- | --- |
| UI (default) | `"Baloo 2"` (400–800, bundled locally via `src/styles/fonts.css`) | `--font-sans` |
| Numbers / time / ids | `"JetBrains Mono", "Cascadia Mono", …` | `num` utility, `tabular-nums` |

Baloo 2 is bundled as two `woff2` subsets (latin, latin-ext) so the console never blocks on a network font request.

| Level | Size / line-height | Weight | Utility | Use |
| --- | --- | --- | --- | --- |
| View title | `15–16px` | 700–800 | — | Worlds / World / page headers |
| Panel title | `14px` | 700 | — | `Panel` header |
| Card title | `13–14px` | 600 | — | world id, spacetime name, block postcode |
| Body | `13px / 1.55` | 400–500 | — | descriptions |
| Secondary | `11–12px` | 400–500 | — | hints, meta |
| Micro label | `11px` | 600 | `label-micro` | field labels, stat rows |
| Latin micro | `10px` | 700 + `0.12em` uppercase | `label-latin` | units, status codes |
| Numeric readout | `22–36px` | 500 | `num` | metric cells, clock |

## 4. Spacing & Layout

Base **4px**; Tailwind steps map directly (`1=4 2=8 3=12 4=16 5=20 6=24 8=32`).

- Page gutters `p-3 lg:p-4`; vertical rhythm `gap-3`.
- Card padding `px-3.5/px-4 py-3` for bars, `p-4/p-5` for panels and forms.
- Toolbars: `chrome px-3.5 py-3`; floating chrome (`chrome`) is reserved for bars, headers and the play bar; `chrome-lg` for popovers, drawers and canvas HUDs.
- **No centred page columns.** Every view fills the viewport width; the only page gutter is `main`'s `p-3 lg:p-4`. Reading-measure `max-w-*` inside a component (a modal, an empty-state paragraph) is still allowed — §16.

## 5. Radii / Elevation / Borders

| Token | Value | Use |
| --- | --- | --- |
| `--r-sm` | 6px | kbd, tiny tags |
| `--r-md` | 8px | inputs, buttons (small), sliders |
| `--r-lg` | 10px | buttons, small tiles |
| `--r-xl` | 18px | cards, panels, popovers, chrome |
| `--r-pill` | 999px | chips, segmented controls, status dots |

- Structure lines are always **1px** `--border`; `--border-strong` marks inputs and chip outlines. No 2px decorative borders.
- Elevation is three steps: `--shadow-1` (resting card / button), `--shadow-2` (hover lift, popover), `--shadow-3` (drawer, canvas HUD). No Tailwind default `shadow-md/lg/xl`.
- Selected surfaces use `--brand-soft` + `--brand-ring`, never a coloured border.

## 6. Motion

| Token | Value | Use |
| --- | --- | --- |
| `--t-fast` | 150ms | hover / focus |
| `--t-base` | 200ms | card lift, tab switch |
| `--t-slow` | 320ms | panel entrance |
| `--ease` | `cubic-bezier(0.16, 1, 0.3, 1)` | global |

- Only `transform` / `translate` / `opacity` / colour properties. Interactive cards use `card-lift` (which transitions `translate`, `transform`, shadow and border together) paired with `hover:-translate-y-0.5 hover:shadow-2`.
- Group entrance: `enter` utility, `translateY(6px) + opacity 0 → 1` staggered by `--enter-index` (40ms).
- Primary buttons press with `scale(0.985)`.
- The replay cursor never tweens — it is driven by `minute`, frame by frame.
- `prefers-reduced-motion: reduce` disables entrance motion and every transition.

## 7. Component Primitives

Shared vocabulary (all token-backed utilities in `index.css`):

| Utility | Contract |
| --- | --- |
| `card` | opaque cocoa data surface: `--surface` + 1px `--border` + `--r-xl` + `--shadow-1` |
| `chrome` | frosted glass bar: `--glass-bg` + `--glass-blur` + `--glass-border` + `--r-xl` |
| `chrome-lg` | heavier-blur glass for popovers, drawers, canvas HUDs |
| `chip` / `chip-active` | cocoa pill for stats and status; `chip-active` marks the selected pill |
| `glass` / `glass-lg` / `paper` | background-only variants (chrome without border/radius) |
| `card-lift` | the transition used by interactive cards |
| `enter` | staggered entrance animation |
| `num` / `label-micro` / `label-latin` | typographic roles |

| Primitive | File | Contract |
| --- | --- | --- |
| `Button` | `components/ui/button.tsx` | `default` = cocoa primary (`bg-brand` + `text-brand-fg` + `shadow-1`), `outline` = 1px `--border-strong` + `--surface`, `secondary` = `--surface-3`, `ghost` = hover wash; `active:scale-[0.985]` |
| `Badge` | `components/ui/badge.tsx` | pill; `outline` = `--surface-2` + `--border-strong` |
| `Input` / `Textarea` | `components/ui/input.tsx`, `textarea.tsx` | `--surface` (dark `--surface-2`) + `--border-strong` + `--r-md`, focus `--brand-ring` |
| `Tabs` | `components/ui/tabs.tsx` | cocoa segmented control: pill list on `--surface-2`, active trigger `bg-brand text-brand-fg` |
| `Select` / `DropdownMenu` | `components/ui/select.tsx`, `dropdown-menu.tsx` | floating surfaces: `chrome-lg` + `--shadow-2`; items hover with `--item-hover` |
| `Tooltip` | `components/ui/tooltip.tsx` | opaque `--popover` + `--shadow-2` so the arrow can carry the border |
| `Sheet` | `components/ui/sheet.tsx` | opaque `--surface` drawer over a `--overlay` scrim, `--shadow-3` |
| `Switch` / `Slider` | `components/ui/*` | checked/range = `--brand`, track = `--border-strong` / `--surface-3`, thumb = `--surface` |
| `Panel` | `components/primitives/Panel.tsx` | `card` + header with 1px divider; `title` / `hint` / `actions` / `children` |
| `WorldBadge` | `components/primitives/WorldBadge.tsx` | `Draft` = neutral pill, `Frozen` = `--info` tint |
| `MetricCell` | `components/primitives/MetricCell.tsx` | micro label + `num` value + unit, fixed `min-w` |
| `StatusDot` | `components/primitives/StatusDot.tsx` | 8px dot, `on` = `--energy` |
| `CategoryLegend` | `components/primitives/CategoryLegend.tsx` | activity-category swatches from `--cat-*` |

**Activity-category derivation** (`lib/activity.ts`) is unchanged: the backend `ActivitySegment` has no `category`, so the front-end maps keywords to the six categories in one place (miss → `leisure`). This is display-layer derivation and adds no API field.

## 8. Responsive & Accessibility

Breakpoints: `<768px` single column; `768–1279px` two columns; `≥1280px` full three-column observation layout. Verified down to ~700px; the shell is desktop-first at 1440×900.

- Every interactive element is at least 32px tall (icon buttons 32×32, `xs` buttons 24px inside dense rows).
- `:focus-visible` is a global `2px --brand` outline with 2px offset; floating surfaces additionally use `--brand-ring`.
- Contrast: body `--fg` on `--surface`/`--glass-bg` ≥ 12:1; `--fg-muted` ≥ 5.5:1; on glass the bg is 72% cocoa, so only `--fg` / `--fg-muted` are used — never a lighter grey.
- State is carried by colour **and** shape/text: away blocks are dashed, job status is a chip with a word, power is a filled vs hollow dot.
- Keyboard: `Space` play/pause, `←/→` ±15min, `Shift+←/→` ±60min, `Home/End`; keys are not hijacked while a field has focus. Charts carry `aria-label`; canvas scenes expose an equivalent outline list.
- `prefers-reduced-motion` is honoured (see §6).

## 9. Accepted Debt

| Item | Reason | Payoff condition |
| --- | --- | --- |
| Lucide icons (banned by `minimalist-skill`) | task requirement | replace if Phosphor/Radix Icons are adopted |
| `HouseFloorplan` / `SnapshotPanel` / `EnergyChart` / `PipelineDrawer` are placeholder shells | owned by later milestones | replace when the milestone lands |
| Activity categories derived on the front end | contract has no `category` field | switch to the field if the backend adds one |
| vis-timeline injects its own DOM, so some rules use `!important` | third-party specificity | remove if the timeline is drawn in-house |
| Konva scene colours are resolved from CSS variables at runtime | canvas cannot consume CSS variables directly | inline the resolved tokens if the scene is server-rendered |

## 10. 场景渲染（react-konva）

### 10.1 选型决策

**采用 `react-konva` 19.2.7 + `konva` 10.5.0，抽象（非像素）角色风格。** 决策已定，不再评估 Phaser。

理由：

- 场景本质是"少量图元 + 高频状态刷新"的数据可视化，不是游戏循环：Stage / Layer / Group / Shape 与 React 组件同构，房间、角色、电器按 `SceneState` 声明式渲染即可。
- 需要命中测试与选中交互（点角色选中、点空白取消），Konva 内置 per-shape 事件与 `Konva.Tween`，无需自建拾取/动画系统。
- 抽象风格只需圆 + 首字母 + 矩形，没有贴图 / 精灵图资源管线；角色身份用 `--member-1..4` 泳道色，与时间轴保持一致（颜色即语义）。
- 与现有栈一致：React 19 + 严格 TS；演示页 `src/scene/SceneDemo.tsx` 挂在 `?demo=scene`，不干扰主应用。

代价：konva 使主包显著增大（见 §10.5），因此演示页按查询串隔离；正式接入时需评估动态加载。

### 10.2 图层结构

canvas 自下而上分层，每层独立 canvas，只重绘发生变化的层：

| 层 | 内容 | 更新时机 |
| --- | --- | --- |
| `floor` 地板层 | 房间矩形、房间名、门 / 走廊 | 仅布局变化 |
| `appliances` 电器层 | 电器圆点、状态色（`--energy` / `--fg-subtle`） | 随 `minute` 变化 |
| `characters` 角色层 | 成员圆（半径 `CHARACTER_RADIUS`）+ 首字母 + 选中环 | 随 `minute` 变化；换房间用 `Konva.Tween` 补间，禁止瞬移 |
| `effects` 特效层 | 用电脉冲、峰值窗口高亮、夜间遮罩 | 随 `minute` 变化；可整体关闭 |
| `ui` 覆盖层 | FPS 读数、图例、按钮 | HTML 覆盖在 canvas 之上，不进入 Konva 树 |

canvas 无法直接消费 CSS 变量：`SceneDemo` 在运行时用 `getComputedStyle(document.documentElement)` 解析 token（`--bg` / `--surface-2` / `--border-strong` / `--fg` / `--fg-muted` / `--brand` / `--member-1`），主题切换后重读，使"组件不硬编码色值"的契约在 canvas 内同样成立。

### 10.3 降级开关

1. 关闭 `effects` 层（不创建该 Layer）。
2. 补间降级：`Konva.Tween` 改为低频补间（目标 15fps，或 200ms 内完成），牺牲平滑度换 CPU 余量。
3. 回退既有网格视图（`MultiHouseGrid` / `HouseFloorplan` 占位壳），即整体关闭 canvas 场景。
4. 停止测帧采样（`useFpsMeter.stop()`），移除测量自身的开销。
5. 跟随 `prefers-reduced-motion: reduce` 关闭补间（与 §6 一致）。

### 10.4 回退规则（硬阈值）

- **帧率**：1440 步（全天逐分钟）回放中，平均 FPS 低于 **45** → 启用降级。
- **内存**：一整天回放结束后，`performance.memory.usedJSHeapSize` 相对回放开始增长超过 **20%** → 启用降级。
- 触发顺序：先关 `effects` 层 → 再降频补间 → 仍不达标则回退网格视图。

判定口径由 `src/hooks/useFpsMeter.ts` 提供：rAF 按 500ms 窗口聚合均值，标签页隐藏 / 长卡顿后重置窗口；`performance.memory` 不可用时内存字段为 null（如 Firefox）。当前阶段（I1-3）demo 仅 3 房间 + 1 角色，**未触发回退规则**；完整保真的 1440 步 FPS / 内存测量推迟到 **I1-18**（真实场景就位后按上述阈值实测）。

### 10.5 实测数据（I1-3 构建）

- 构建：`npm run build`（tsc -b + vite build），退出码 0。
- `dist/assets/index-*.js`：**1,683.76 kB raw / 482.08 kB gzip**（vite 报告；zlib level 9 复测 476.87 kB）。
- 对照构建（同一源码，仅移除 `?demo=scene` 入口）：1,357.61 kB raw / 381.21 kB gzip。
- **konva / react-konva 可归因增量：+326.14 kB raw / +100.87 kB gzip**（含约 10 kB 未压缩的演示源码）。
- 历史基线（konva 引入前）：1,187.30 kB raw；当前相对该基线 +496.46 kB raw，其中 konva 之外的增量来自主应用同期新增代码。

### 10.6 运行期 API 基址（端口无关）

前端默认取**相对路径** `/api`，由浏览器按"当前页面 origin"解析 —— 因此**后端换端口无需重新构建**。若要把 dist 与 API 分离部署，后端通过 `/config.js` 暴露运行期配置：

```
GET /config.js  →  window.__API_BASE__ = "<LLMWORLD_API_BASE 环境变量值，默认 /api>";
```

- `index.html` 在 `<head>` **最先**引入该脚本（先于 module bundle，消除 classic/module 执行顺序的隐式依赖）
- `client.ts` 解析顺序：**运行期 `window.__API_BASE__` → 构建期 `VITE_API_BASE` → 相对 `/api`**
- SSE 日志同样走这套基址
- 开发模式下 `vite.config.ts` 同时代理 `/api` 与 `/config.js` 到 8000

实测：以 `LLMWORLD_API_BASE=http://127.0.0.1:8000/api` 启动后端，页面仍正确取到真实数据（10 房间 / 40 电器 / 325 W），证明注入链路端到端生效。

## 11. 场景交付与验收（I1-4 ~ I1-18）

### 11.1 交付结构

```
src/scene/
  core/    纯逻辑（可被 Node 直跑自测）
    types.ts            冻结契约：SceneState / CharacterPose / AppliancePose / RoomPose / TownHouse
    layout.ts           确定性户型布局（切片切分 + 邻接图 + 门点 + 房间间路径）
    layout.selftest.ts  布局自测（node 直跑）
    lighting.ts         昼夜光照纯函数（night / tint / peakWindow / lampRooms）
    lighting.selftest.ts 光照自测（node 直跑）
    tokens.ts           canvas 内解析 CSS 变量（getComputedStyle + 主题变更重读）
    appliances.ts       电器字形 / 状态色调 / 房间内槽位
    effects.ts          电器特效判定（steam / airflow / screen / ring / drum / glow）
    useSceneState.ts    DayReplay + minute → SceneState（唯一派生入口）
  layers/  只渲染，不依赖 app 层
    RoomLayer.tsx       房间地板 / 墙体 / 房间名 / 即时瓦数 / 外出带状区
    ApplianceLayer.tsx  电器精灵（四态 + 呼吸/循环脉冲 + 悬停 tooltip + 高亮环）
    CharacterLayer.tsx  角色（沿房间路径补间行走 / 睡眠 Z / OUT 徽标 / 轨迹）
    EffectLayer.tsx     特效层（单动画驱动，不拦点击）
  views/   组合与交互
    SceneStage.tsx      Stage + 命令式相机 + 光照覆盖层
    SceneView.tsx       组合器：小镇 ↔ 室内、开关、成员条、无障碍摘要
    Town.tsx            小镇视图（房屋阵列 + 缩放平移）
    HouseBuilding.tsx   单栋房屋（窗户点亮数 ∝ 负荷 + 负荷条 + OUT 徽标）
    AgentHud.tsx        角色详情（人格 / 当前活动 / 在用电器 / 接下来 / Esc 关闭）
    SceneOutline.tsx    房间→电器可聚焦清单（无障碍等价路径）
    PerfHud.tsx         帧率/内存诊断 + 降级判定
```

### 11.2 自测清单

| # | 项 | 结果 | 证据 |
| --- | --- | --- | --- |
| 1 | 布局确定性、无重叠、铺满、连通 | ✅ | `node src/scene/core/layout.selftest.ts` → **34 passed / 0 failed** |
| 2 | 光照单调性、无跳变（单分钟 Δ<0.01）、色值合法 | ✅ | `node src/scene/core/lighting.selftest.ts` → **18 passed / 0 failed** |
| 3 | 后端 `room_meta` 与 `household.json` 一致 | ✅ | `world_143345/house_0003`：10 房间，逐项 size 相同 |
| 4 | 严格类型检查 | ✅ | `npx tsc -b` 退出码 0（`noUncheckedIndexedAccess` / `noUnusedLocals` / `verbatimModuleSyntax`） |
| 5 | 生产构建 | ✅ | `npm run build` 退出码 0 |
| 6 | 真实数据端到端（室内） | ✅ | 浏览器无障碍摘要：`10 个房间，40 台电器，3 台在用电，3 人外出，325 瓦` |
| 7 | 小镇视图渲染与进入室内 | ✅ | 截图 `town-view-2` / `interior-house0003`，无控制台报错 |
| 8 | 单步推进（10 分钟/格） | ✅ | 读数 `第 60/144 格`，切换后房间瓦数与成员活动同步变化 |
| 9 | konva 拆包（不拖慢首屏） | ✅ | 主包 1,338.79 kB raw / **379.93 kB gzip**；konva 独立 chunk 318.25 kB / 98.38 kB |
| 10 | 键盘可达 | ⚠️ 部分 | 成员选择条为真实 `<button>` 并可 `Tab`/`Enter`；**canvas 图元本身不可聚焦**（设计取舍，见 §11.5） |
| 11 | FPS / 内存压测 | ⚠️ 环境受限 | 见 §11.6：内存**无泄漏信号**（60s 连续动画 +0.4 MB / 0.9%）；**FPS 在本环境不可测**（内嵌浏览器面板不在前台时 rAF 被节流到 ~1 fps），测帧器已能识别并拒绝该样本 |

### 11.3 数据一致性核对

| 对比项 | 场景内 | 既有面板 | 结论 |
| --- | --- | --- | --- |
| 户总功率（`house_0003` @ 10:00） | 325 W | `/api/replay` 返回 325 W | 一致 |
| 在用电器台数（同上） | 3 台 | 该户 `always_on` 设备数 = 3（冰箱/冰柜/路由） | 一致 |
| 房间瓦数合计 | 由 `wattsAt()` 按房间归并 | `SnapshotPanel` 同源 `lib/appliance.ts` | 同源，无第二套状态判断 |

场景层不新增任何网络请求与 LLM 调用，只消费既有 `/api/runs`、`/api/runs/{run}/days/{date}/houses/{house}`、`/api/replay`。

### 11.4 降级与无障碍实现

- `prefers-reduced-motion: reduce`：`CharacterLayer` 直接定位不补间；`ApplianceLayer` / `EffectLayer` 不起动画循环；相机不做过渡。
- 特效整体开关（`特效开/关`）、轨迹开关（`轨迹开/关`）已接在 `SceneView` 头部。
- `SceneStage` 容器带 `role="img"` + 房间/电器/成员数 `aria-label`；`SceneView` 输出 `aria-live` 场景摘要（房间数、电器数、在用台数、外出人数、总功率）。
- 成员选择条（`aria-pressed`）提供不依赖 canvas 命中测试的选择路径。

### 11.5 遗留与未完成

| 项 | 说明 |
| --- | --- |
| FPS 实测（§10.4 阈值） | **本环境不可测**：内嵌浏览器面板不在前台时 rAF 被节流到 ~1 fps。已在 `useFpsMeter` 加入失速检测（帧间隔 >250ms 计失速，失速率 >50% 判「采样无效」），避免把节流误报为性能问题并误触发降级。需在**浏览器前台**按 §11.6 步骤实测 |
| canvas 图元键盘遍历 | 房间/电器/角色不是 DOM 节点，无法 `Tab`；已用「成员选择条」+「清单」面板（房间→电器逐条可聚焦、`aria-pressed`、点击在 canvas 上打高亮环）提供等价路径 |
| 工作区状态不持久化 | 「小镇/室内」等 `view` 是组件内 state，刷新回默认视图；时间/运行/住户/日期已在 URL 中 |
| 户外目的地建筑 | 用户决策：不画，外出仅以 OUT 徽标 + 户外带状区表示 |
| 轨迹依赖会话内记忆 | `trails` 只记录本次打开后走过的房间；刷新后从当前时刻重新累积 |
| 房屋迷你负荷曲线 | `HouseBuilding` 用当前负荷条替代全天缩略曲线，避免额外请求 |

### 11.6 FPS / 内存实测步骤（需浏览器前台）

前置：`cd dashboard` → `..\.venv\Scripts\python.exe -m uvicorn backend.main:app --port 8000`，浏览器打开 `http://127.0.0.1:8000/`，**保持窗口在前台且可见**（后台标签页 / 被遮挡的窗口会被 Chrome 节流 rAF，测出的帧率无效）。

1. 顶栏进入「小镇」→ 点任一房子进入「室内」
2. 点 `开始测帧`
3. 底栏切「跳格」，步长保持 `10 分/格`，倍速切 `×16`（每格 120ms）
4. 点播放，让它跑完一整天（144 格 ≈ 17s）
5. 读 HUD：`fps` / `堆 ±X MB` / `增长%` / `采样时长`

判定（同 §10.4）：平均 **fps < 45** 或堆增长 **> 20%** → 启用降级。
HUD 显示 `采样无效` 表示该次采样被判为节流（帧间隔失速率 > 50%），**不要**据此调参，换到前台重测。

已获得的部分结果：60 秒连续动画下堆增长 **+0.4 MB（0.9%）**，无泄漏信号。

## 12. 收尾重构记录

### 12.1 本轮修复的问题

| # | 问题 | 现象 | 修法 |
| --- | --- | --- | --- |
| 1 | **契约撒谎**：`/runs/{run}/meta` 无 `response_model` 返回裸 dict，前端却声明为 `RunInfo`（缺 4 个字段） | 类型与运行时不一致，属潜在 bug | 后端新增 `RunMeta` 模型 + `response_model` 校验；前端新增 `RunMeta` 类型、`client.ts` 改签名、mock 增加 `asRunMeta` 归一化 |
| 2 | **工作区状态不持久** | 刷新回默认视图，无法分享链接 | `view` 从 App 组件 state 迁入 zustand store，并由 `useUrlSync` 纳入 URL（`?view=`），支持 URL 恢复 |
| 3 | **测帧误报** | 页面不在前台时 rAF 被节流到 ~1fps，被判「已降级」并误关特效 | `useFpsMeter` 增加失速检测（帧间隔 >250ms 计失速，失速率 >50% 判 `采样无效`）；`PerfHud` 只在有效样本上降级 |
| 4 | **降级不可逆** | 一旦降级无法恢复，无人工覆盖入口 | 连续 4 个有效好样本自动解除降级；点击特效按钮可强制开启并解除 |
| 5 | **降级语义误导** | 按钮显示 `特效开·降`，但实际特效是关的 | 改为显示**生效状态**（`特效开/关`）+ `（已降级）`，并以 `effectsOn = effectsEnabled && !degraded` 单一真源驱动 |
| 6 | **死代码** | `SceneDemo` + `?demo=scene` 门控被真实场景取代后仍占一个 chunk | 删除 `SceneDemo.tsx` 与门控，`main.tsx` 只渲染 `App` |
| 7 | **诊断面板常驻** | 性能读数一直占头部空间 | 折叠进「诊断」开关（默认关闭） |
| 8 | **指标条只在一个工作区** | 小镇/网格看不到户级指标 | 观察类工作区（小镇/网格/详情）统一显示 `MetricStrip` |
| 9 | **工作区切换不易扫读** | 6 个平铺 tab，观察与控制混在一起 | 按语义分组，中间加分隔线（观察：小镇/网格/详情 │ 控制：生成/模拟/任务） |

### 12.2 结构梳理（模块职责）

| 层 | 目录 | 职责 | 依赖方向 |
| --- | --- | --- | --- |
| 契约 | `dashboard/backend/models.py` ↔ `src/api/types.ts` | 唯一真源；两侧字段一一对应 | 无 |
| 后端 | `backend/{paths,store,derive,jobs}.py` + `backend/routers/*` | `store` 只做索引与账目缓存；`derive` 只做「读盘 → 场景/回放负载」；`jobs` 只做子进程与队列；routers 只做 HTTP 映射 | store/derive ← routers |
| 前端数据 | `src/api/client.ts` | 唯一出网口（含 mock 切换、运行期基址、错误归一） | 被 hooks 调用 |
| 前端状态 | `src/store/time.ts` | 唯一全局状态（时间/选择/播放/工作区），含 URL 初始化 | 被所有组件读 |
| 前端派生 | `src/hooks/*` | react-query 封装 + 播放循环 + FPS 采样 + URL 同步 | store + client |
| 展示 | `src/components/*` | 仪表盘 UI（非 canvas） | hooks |
| 场景 | `src/scene/*` | canvas 场景；`core`（types/layout/lighting/tokens/appliances/effects/useSceneState）为纯逻辑，`layers`（Room/Appliance/Character/Effect）只渲染，`views`（SceneStage/SceneView/Town/HouseBuilding/AgentHud/SceneOutline/PerfHud）负责组合 | core → layers → views |

约束（已在代码中成立）：canvas 层不反向依赖 app 层；纯逻辑模块可被 Node 直接跑自测（`layout` / `lighting`）；场景零新增网络请求与 LLM 调用。

### 12.3 文件级目录拆分（已执行）

`src/scene/` 已由平铺 20 文件拆为三层：**`core/` 9（纯逻辑）· `layers/` 4（只渲染）· `views/` 7（组合交互）**，根目录零残留。

- 依赖方向：`views → layers → core`，core 不反向依赖；core 内相对导入全在同目录，故 **core 无需任何改动**
- 导入重写：`layers/*` 与 `views/*` 共 28 处 `"./X"` 改为 `"../core/X"` / `"../layers/X"`；`views/` 内 6 处同级引用（AgentHud / PerfHud / SceneOutline / SceneStage / Town / HouseBuilding）保持不变
- 自测路径变更：`node src/scene/core/layout.selftest.ts`、`node src/scene/core/lighting.selftest.ts`
- 外部唯一改动：`App.tsx` 懒加载路径 `@/scene/SceneView` → `@/scene/views/SceneView`

**过程教训（已踩过）**：首次拆分用 PowerShell `Set-Content` 重写导入，**把文件写坏了**（JSX 全面解析失败）。原因是 PS 5.1 的文本读写编码不可靠。已改用 `git` 恢复到基线提交（`616891f`），再以 **Node `fs` 显式 utf8 读写**完成重写。

因此流程约定：**批量文件操作前先建 git 基线**（本次 `616891f` 正是回滚救命的依据）；文本重写用 Node，不用 PowerShell 的 `Set-Content`。

### 12.4 UI 架构（当前）

```
┌ 顶栏（全局，glass 吸顶）
│  BrandMark │ 工作区切换（观察 │ 控制） │ 选择控制 run/date/house/policy │ 主题
├ 指标条（观察类工作区）  总电量 / 峰功率 / 峰时段 / 负荷率 / 活跃电器 / 成员数
├ 主区（按工作区切换）
│  小镇    → 房子阵列（Konva）→ 点房进室内
│  室内    → 成员选择条 │ 房间/电器/小人 canvas │ 成员 HUD（左下）│ 清单（右）│ 诊断（上）
│  网格    → 每户一张卡（成员摘要 + 用电）
│  详情    → 平面图+负荷曲线 │ 成员卡+时间轴 │ 快照+住户切换+决策流水线
│  生成/模拟/任务 → 表单类工作区（无时间轴）
└ 底栏（观察类工作区）  时间控制：回到00:00 │ 上一格 │ 播放 │ 下一格 │ 跳到24:00 │ 步长 │ 倍速 │ 连续/跳格
```

交互一致性：**一个时间游标驱动全部视图**（滑块、时间轴竖线、曲线游标、场景人物位置、电器亮灭、房间瓦数、住户网格、快照）；`selectedMember` 与 `view`/`minute`/`run`/`date`/`house`/`policy` 全部可在 URL 中复原。

### 12.5 性能诊断与修复（第二轮）

用户反馈「切换卡顿」并「默认改浅色」。诊断出 4 个成因，其中 **3 个是代码问题**：

| # | 成因 | 性质 | 修法 |
| --- | --- | --- | --- |
| 1 | 场景 chunk 首次下载 **356 kB**（konva 打包在内，且无预取） | 加载慢（非 bug） | `App` 挂载 **1.2s 后闲时预取** `import("@/scene/views/SceneView")`，切到小镇时已在缓存；Suspense fallback 换成 `SceneFallback` 骨架屏（按场景布局的房间网格 + 右侧面板 shimmer + 旋转指示 + 体积说明） |
| 2 | **`buildLayout()` 每分钟重算** | **代码问题** | 从主 memo 拆成独立 memo，只依赖 `[replay, size]`。此前一天 144 步会重建 144 次 Treemap + O(n²) 邻接图 + BFS 闭包 |
| 3 | **50 个 Konva `<Text>` 字形随脉冲动画每帧重绘** | **代码问题** | 字形 / 高亮环 / 悬停提示拆到**独立静态 Layer**（`listening={false}`），动画层只重绘圆点；且脉冲动画**不再按分钟重启**（deps 去掉 `minute`，动画每帧读 `getChildren()` 自然跟随） |
| 4 | **选中成员触发整场景重算** | **代码问题** | `CharacterPose.selected` 从契约移除，改由 `CharacterLayer` 直读 store —— 选中不再重算 `SceneState`（只重渲角色层） |

主题：默认改为**浅色** —— `useTheme.readTheme()` 默认 `"light"`，同时 `index.html` 预置 `<html class="light">` 消除首屏闪暗（无 JS 时也是浅色）。

未测项（环境限制，同 §11.6）：本环境内嵌浏览器面板不在前台时 rAF 被节流，**改前/改后的 FPS 数字都无法在此取得**；上述修复的收益是结构性推导（重算次数 144→1、每帧文本绘制 50→0、选中重算 1→0），不是实测帧率对比。

### 12.6 流畅性优化（第三轮）

在 §12.5 基础上继续压 Konva 层的硬成本：

| # | 问题 | 成本 | 修法 |
| --- | --- | --- | --- |
| 1 | 电器**动画层开着 `listening`** | 每帧重建 50 个圆点的**命中图（hit canvas）** | 动画层改 `listening={false}`；命中目标改为静态层中 50 个 `fill="transparent"` 的圆 → 命中图只随分钟重建 |
| 2 | 电器圆点 `fill === stroke` 触发 Konva **perfectDraw 两遍绘制** | 绘制成本 ×2 | `perfectDrawEnabled={false}` + `shadowForStrokeEnabled={false}`（fill/stroke 同色，关掉无视觉影响） |
| 3 | **每个小人各自一个 `Konva.Animation`**，却都指向同一 Layer | N 个动画 = **每帧 N 次层重绘** | 合并为**一条共享动画**：`walkers: Map` + 单实例 `Konva.Animation`，空闲自动 `stop()`、下次需要时重建 → 重绘 **N→1** |
| 4 | `SceneOutline` 60 行 DOM 重建 | React 协调 | 仅「清单」打开时渲染（已条件渲染）；未做虚拟化（60 行量级不值得） |

**累计结构性收益**（相对优化前）：布局重算 144→1 · 每帧文本绘制 50→0 · 每帧命中图重建 1→0 · 每帧层重绘 6→1 · 单形绘制遍数 2→1 · 选中重算 1→0。

验证：`tsc -b` 0 / `npm run build` 0；浏览器实跑连点「下一格」三步（600→610→620→630），**无 console 报错**，场景数据一致（10 房间 / 40 电器 / 3 台在用电 / 325 W）。

**仍未实测 FPS**：本环境 rAF 被节流（§11.6），数字取不到；以上为结构性推导，不是帧率对比。

### 12.7 世界工作台（M5 收尾）

| 项 | 交付 | 说明 |
| --- | --- | --- |
| 导航 | 「构建」→「世界」 | `view` 键仍为 `"build"`，既有 `?view=build` 链接继续有效 |
| 世界工作区 | `components/WorldWorkspace.tsx` | 模式 `构建 / 模拟 / 观看`；store `mode`（`"build" \| "simulate" \| "watch"`，默认 `build`），URL `?mode=` |
| 观看密度 | `SegmentedControl` + store `density`（`"town" \| "grid" \| "detail"`，默认 `town`），URL `?density=` | 分别渲染 `SceneView`（懒载）/ `MultiHouseGrid` / 详情三栏 |
| 共享观察布局 | `components/ObserveViews.tsx` | `ObserveScene` / `ObserveGrid` / `ObserveDetail` 同时服务独立视图（scene/grid/detail）与观看模式，无重复标记 |
| 模拟预填 | `SimulateForm` 新增 `lockedWorld` | 进入模拟模式时世界字段预填并锁定为当前 `world`；住户 / 日期 / 政策照旧可编辑 |
| 工具栏 | `RunPicker` + `MetricStrip` + `TimeController` | 观看模式下随观察视图显示（`view=build && mode=watch`）；构建 / 模拟模式隐藏 |

- URL 复现：`?view=build&world=<W>&mode=<m>&density=<d>&step=<S>`；仅带 `mode`/`density` 而无 `view` 的链接默认进入世界工作区。
- 独立视图（scene / grid / detail / generate / simulate / jobs / settings）原样保留，两条路径共存。
- 验收：`npx tsc -b` / `npm run build` / `npm run lint` 均 exit 0。

## 13. Information architecture — Worlds / World / Watch (restructure part 1)

> Supersedes §12.4 (top bar) and §12.7 (world workspace navigation). All user-visible
> copy is English from this point on.

**Conceptual model** — a *world* is a fixed set of blocks (postcodes) and households;
a *spacetime* is one simulation run over that world (policy + news/events + start date
+ arbitrary days) and only ever reads the households. A world with ≥1 spacetime is
**frozen**: to edit its households you clone it into a new draft.

**Navigation** — the top bar has exactly three items: `Worlds | Jobs | Settings`.

| Level | View | Content |
| --- | --- | --- |
| L0 | `view=worlds` (default) | World cards: id, block / household / spacetime counts, `Draft` (0 spacetimes) or `Frozen` badge, last activity. Actions: new blank world, clone, delete (recoverable, confirm first). |
| L1 | `view=world&world=W` | Header (id, badge, clone, back link) + two tabs. `Spacetimes`: list + inline creation wizard; each row opens Watch. `Households`: draft → embedded `WorldBuilder`; frozen → read-only block/house structure with a lock banner (Lucide `Lock` icon; §1 bans emoji) and a clone action. |
| L2 | `view=watch&world=W&run=R` | 4-layer drill-down: world → block → house → indoor (§14). |

**Store / URL contract** (`store/time.ts`, `hooks/useUrlSync.ts`) — `view` is
`"worlds" | "world" | "watch" | "jobs" | "settings"`; the store also carries
`world`, `tab` (`"spacetime" | "household"`), `run`, `date`, `block`, `house`,
`indoor`, `policy`, `minute` (plus `step`, still used by the household builder).
Initial values come from the URL and fall back to defaults; `PARAM_ORDER` is
`view, world, tab, run, date, block, house, indoor, policy, minute`.
The `mode` / `density` fields were local state in the `WorldWorkspace` shell,
which part 2 deleted; watch layers are URL state instead (§14).

**New primitives / components** — `ui/textarea`, `primitives/WorldBadge`,
`WorldsList`, `WorldDetail`, `SpacetimeList`, `SpacetimeWizard`, `WorldHouseholds`,
`CloneWorldButton`; hooks `useWorld` / `useCloneWorld`
(`useWorldBuild.ts`) and `useSpacetimes` / `useCreateSpacetime` /
`useDeleteSpacetime` / `useWorldDayBlocks` (`useSpacetimes.ts`). No new tokens were
required; everything reuses §2–§6. `WatchPlaceholder` was a part-2 stepping stone
and is replaced by `WatchView` in §14.

## 14. Information architecture — L2a Watch (restructure part 2)

`view=watch&world=W&run=R` renders `components/WatchView.tsx`. The active layer is
derived from URL state, never from local component state:

| Layer | Condition | Content |
| --- | --- | --- |
| 1 World | no `house`, no `block` | Town map (`ObserveScene` → lazy `SceneView` in map-only chrome, no interior toggle) plus a compact block strip from `useWorldDayBlocks` (postcode / households / total kWh / peak W). Selecting a block sets `block`. |
| 2 Block | `block`, no `house` | Block summary + `ObserveGrid` = `MultiHouseGrid` filtered to the block's house ids. Selecting a household sets `house`. |
| 3 House | `house`, `indoor=false` | `MetricStrip` + `ObserveDetail` (floor plan, load curve, members, activity timeline, snapshot, decision pipeline). Prominent `Enter indoor` sets `indoor=1`. |
| 4 Indoor | `house`, `indoor=1` | Full-height `HouseFloorplan`: rooms with occupants, appliances and live load. `Back to house` clears `indoor`. |

- **Breadcrumb** `World W / R / date / block / house`; every crumb is clickable and clears the
  deeper selections. A back link returns to L1 (`view=world&world=W`).
- **Day selector** reads `GET /api/runs/{run}/meta` via `useRunMeta` and writes `date`; an effect
  converges `date` to the first valid day when the URL points at a missing one.
- **Play bar gating** — `TimeController` is rendered only by `WatchView` (bottom glass frame), so
  no other view shows it. `usePlayback` (rAF loop + keyboard shortcuts) mounts with `WatchView` too.
- **Data** — replays come from the existing `useDayReplay`; day blocks from `useWorldDayBlocks`.
  No new fetch primitives, no new tokens.
- **Empty states** (English): no world / spacetime selected, loading, meta failure, no simulated
  days, block without households, household without a replay.
- **Reused primitives gained optional props** (defaults unchanged): `MultiHouseGrid.houses`,
  `HouseFloorplan.className`, `SceneView.onEnterHouse`.

**Cleanup** — deleted `WatchPlaceholder`, `WorldWorkspace`, `RunPicker`,
`primitives/Placeholder`, `primitives/SegmentedControl`, `hooks/useBootstrapSelection`,
`SimulateForm` and `GenerateWizard` (each unreachable after the watch wiring: their only entry
points were the removed placeholder/workspace). The `mode` / `density` model went with
`WorldWorkspace`.

**English-only enforcement** — all user-visible copy, comments and fixtures under `src/` are
English. The build additionally strips CJK from vendor sources via the `strip-vendor-cjk` plugin
in `vite.config.ts` (moment locales, `vis-timeline`'s bundled translations, Chinese comments in
`xss` / `cssfilter`); `ActivityTimeline` imports the unbundled `vis-timeline/esnext` build so
`moment-with-locales` never enters the bundle. Gate: scanning `dist/` for `[\u4e00-\u9fff]`
returns 0 matches.

## 15. Warm Cocoa re-skin (whole-console)

The visual language of §1–§9 was replaced wholesale. Palette, radii, glass recipe and the Baloo 2
type stack live in `src/index.css`; the mirror sources are
`sister/kanvana/client/src/styles/tokens.css` + `layout.css` + `components/*.css` and
`sister/infinite-canvas/web/src/styles/globals.css`, so all three products read as one family.

### 15.1 What changed

| Layer | Change |
| --- | --- |
| Tokens | surfaces/text/borders re-based on warm cocoa; `--brand` is now the cocoa neutral (`#171717` light / `#fafafa` dark) with `--brand-fg` as its inverse; semantic colour narrowed to state |
| New tokens | `--item-hover`, `--item-selected`, `--overlay`, `--on-danger` (light + dark) and their Tailwind mappings (`bg-item-hover`, `bg-item-selected`, `bg-overlay`, `text-on-danger`, `ring-brand-ring`) |
| New utilities | `chrome`, `chrome-lg` (frosted bars vs. heavy-blur overlays), `card` (opaque cocoa data surface), `card-lift` (interactive-card motion), `chip`, `chip-active` |
| App shell | sticky `glass` header, cocoa brand mark, pill nav with `bg-brand` active item, outline theme toggle |
| L0 Worlds | glass toolbar (title + counts + refresh + new-world form) above a responsive grid of `card` tiles: Baloo semibold world id, `Draft`/`Frozen` badge, stat pill, last activity, Clone/Delete footer; hover lift |
| L1 World | glass header (back · id · badge · stat pill · Clone), cocoa segmented tab control, spacetime rows as cards with semantic status chips, wizard as a glass form |
| L2a Watch | glass breadcrumb/day bar, paper pill block chips, glass layer headers, glass play bar (still mounted only by `WatchView`) |
| Jobs / Settings / Build | `card` panels, `--item-hover` / `--item-selected` list rows, status chips with semantic tints, shared textarea/input/switch styling |
| Observation panels | `Panel` is now `card`; room tiles, member cards, household cards and pipeline segments follow the same border/radius/tint rules; `MetricStrip` legend is a pill row |
| Scene chrome | `SceneView` panel is `card`; outline/diagnostics toggles are cocoa pills; `AgentHud` and the rooms outline are `chrome-lg` + `--shadow-3`; canvas hints are `chip`; `scene/core/tokens.ts` fallbacks retuned to cocoa (runtime values still come from CSS variables) |
| Docs | this section; §1–§9 rewritten; `vis-timeline.css` keeps its token-driven overrides (item radius raised to `--r-md`) |

### 15.2 Invariants kept

- No behaviour, data wiring, URL parameter, store shape or routing change; the play bar remains
  `WatchView`-only.
- All user-visible copy stays English.
- Components reference tokens only — the single remaining hardcoded palette lives in
  `scene/core/tokens.ts` as the non-DOM fallback, which is the documented canvas boundary.
- `tsc -b`, `npm run build` and `npm run lint` are the gate for this change.

### 15.3 Contrast notes

Glass is 72% cocoa in both themes, so glass chrome uses `--fg` / `--fg-muted` only. Cocoa primary
buttons pair `--brand` with `--brand-fg` (the exact inverse), so the pair inverts cleanly with the
theme. Status chips always combine a semantic tint, a 1px border and a word, so state survives
greyscale and colour-blind viewing.

## 16. Full-bleed layout (master–detail worlds)

Supersedes the centred content columns of §4 and the L0/L1 presentation of §13; the data wiring,
store shape and URL contract there are unchanged. `max-w-3xl` (settings), `max-w-6xl` (worlds) and
`max-w-5xl` (world detail) page wrappers are gone — every view is full-bleed inside `main`'s
`p-3 lg:p-4` gutter.

| View | Layout contract |
| --- | --- |
| Worlds / World — one workspace for `view=worlds` and `view=world` | `grid h-full min-h-0 grid-rows-[minmax(0,1fr)] gap-3 lg:grid-cols-[minmax(300px,360px)_minmax(0,1fr)]`. **Left pane** (`card`, scrolls on its own) owns select / add / delete: new-world form, then one row per world (id, `Draft`/`Frozen`, block · household · spacetime counts, last activity, Clone, Delete) with the selected row on `--item-selected` + `--brand-ring`. **Right pane** is the world detail (glass header with badge + Clone, `Spacetimes` / `Households` tabs) or, with no selection, the "Select a world" empty state. Below `lg` the workspace collapses to one column: list first, the detail replaces it once a world is selected, and the header's back button (hidden at `lg`) clears `world` to bring the list back. Selecting a row writes `world` to the store and the URL; `view` is left alone so both old links keep working. |
| Watch (`view=watch`) | Unchanged full-height stack: full-width glass breadcrumb + day bar, layer content in `min-h-0 flex-1`, full-width glass play bar pinned at the bottom. |
| Jobs (`view=jobs`) | `grid h-full min-h-0 grid-cols-1 gap-3 lg:grid-cols-[minmax(0,340px)_minmax(0,1fr)] lg:grid-rows-[minmax(0,1fr)_auto]`; the job list and the log / LLM-call inspector fill the height side by side and scroll internally. |
| Settings (`view=settings`) | Full-width `card`; fields in a `md:grid-cols-2 xl:grid-cols-3` form grid, each field carrying a one-line description and its `LLMWORLD_*` variable. |

Invariants: panes use `h-full min-h-0` with an inner `overflow-y-auto`, so the page never grows a
second scrollbar; the play bar stays `WatchView`-only; no new tokens, no store-shape change.

## 17. Focus pass — one screen, one job

> **Supersedes §16's single two-pane workspace.** §1–§9 tokens, type, radii, motion and the Warm
> Cocoa language are **unchanged** — this pass fixes *density and hierarchy*, not the palette.
> The style skill in force is still `minimalist-skill.md` (see §0); this section adds the
> `layout-skill.md` spatial contract that was missing.

### 17.1 Diagnosis (the defect being fixed)

At 1440×900 the Worlds route showed all of this at once: a 3-item top nav; a 560px list
pane carrying an always-visible create form **and** a 5-column table; and the entire world
detail beside it (header + badge + stat pill + Clone + 2 tabs + an explanatory paragraph +
a districts table + a second explanatory paragraph + a households table). Concretely:

| # | Defect | Evidence |
| --- | --- | --- |
| 1 | Two refresh buttons, two create entries | `Refresh worlds` + `Refresh districts`; `New blank world` + `New district` |
| 2 | The same concept explained twice on one screen | "Households are a world's fixed physics…" beside "A scenario is a parallel version…" |
| 3 | `Clone` offered twice | once per list row, once in the detail header |
| 4 | Counts duplicated | the stat pill AND the same numbers in the tables |
| 5 | **Three nested scroll regions side by side** | list pane, districts table, households table — the exact case `layout-skill.md` §1 calls a defect |
| 6 | No primary action | create / generate-description / generate-home / Steps / Clone / Delete all carry near-equal weight |

Nothing was primary, so everything competed. The width squeeze documented in §16 (a 560px
worlds pane plus a 42% districts column) was a *symptom* of defect 5, not a fixed constraint.

### 17.2 Rules this pass enforces

1. **One screen, one job.** A route renders ONE primary region. `view=worlds` is the full-width
   worlds index; `view=world&world=W` is that world's detail. **They are never shown side by
   side.** The store/URL already modelled this — §16 merged it, this section splits it back.
2. **One primary action per screen.** Exactly one `default`-variant button is visible without
   interaction (the screen's create action). Every other action is `outline` / `ghost` / icon-only,
   or lives behind a `Sheet`.
3. **Create forms are never part of the layout.** New world / new district open in a right-hand
   `Sheet` triggered by one button — the pattern §7's `Sheet` primitive already provides. No
   always-visible form sits on a screen.
4. **Say it once per screen.** Conceptual explanation is removed from panes and kept only in the
   `Sheet` that performs the action, or in the empty state that actually needs it.
5. **Counts appear once.** A count lives either in a table cell or in a header pill, never both.
6. **Named scroll ownership** (`layout-skill.md` §1) — recorded in §17.3. Every scrollable region
   must have a named job; no two scroll containers may be nested without one.
7. **Named layout primitives** (`layout-skill.md` §3) — screens are built from `scroll-body-shell`,
   `list-detail`, `cluster` and intrinsic grids instead of ad-hoc flex/grid.

### 17.3 Screen contracts

| Route | Spatial model | Scroll owner (named) | Primary action | Secondary actions |
| --- | --- | --- | --- | --- |
| `view=worlds` | full-width: toolbar over a table | the worlds table body only | `New world` (opens `Sheet`) | refresh (icon), per-row clone / delete (icon) |
| `view=world&world=W` | header, then `Households` \| `Scenarios` tabs | one named region per visible pane, side by side, never nested | `New district` (Households tab) | per-district description / steps / delete (icon) |
| `view=world&…&tab=scenarios` | same shell, `Scenarios` pane | the scenarios list only | `New scenario` | open / delete per row |
| `view=watch` | unchanged (§14) | unchanged | — | — |
| `view=jobs` | unchanged (§16) | unchanged | — | — |
| `view=settings` | unchanged (§16) | unchanged | — | — |

The Households pane uses the `list-detail` primitive: districts on the left, the selected
district's households on the right. Both are full-width-pane tables, so neither needs the
compressed proportions §16 required.

### 17.4 Required stress states (`layout-skill.md` §6)

Per screen: **empty** (no worlds / no districts / no households), **long label** (a 40-character
id truncates with `title`), **unbroken string** (`min-w-0` + `truncate`), and **reflow** — at
375px each screen is a single readable column with **no horizontal scroll of primary content**.
Each is rendered as a full-width table row or the pane's own empty state.

### 17.5 Accepted debt

| Item | Reason | Payoff condition |
| --- | --- | --- |
| `/visual-qa` dual-oracle gate not run for this pass | this environment cannot capture pixels (the embedded browser panel's screenshot path errors, and the Playwright MCP profile is locked by a stale instance) | re-run `/visual-qa` at 375 / 768 / 1280 on a machine with working capture |
| `FrozenHouseholds` still renders block cards, not a table | out of scope for this pass; the frozen view shows simulation blocks (kWh / peak W), a different shape from the districts list | convert when the frozen view is next touched |

## 18. District lifecycle — uninitialized → initialized → locked

### 18.1 States

| Status | Meaning | Source |
| --- | --- | --- |
| `uninitialized` | A newly created district. It has no description, so the world holds no information about it yet. | **derived** — `has_description == false` |
| `initialized` | The district has a description. **Still editable**: both its name and its description can be rewritten. | **derived** — `has_description == true` and not locked |
| `locked` | The description was accepted and frozen. **There is no unlock.** | **persisted** |

`locked` is persisted in a marker file **outside** `district.json`
(`output/worlds/<world>/<district>/.locked`, holding the ISO timestamp), so a pipeline
rewrite of `district.json` can never silently clear the lock. It travels with the
directory on rename and on the recoverable delete to `output/_trash/`.

### 18.2 Transitions

| From | Action | To | Notes |
| --- | --- | --- | --- |
| — | create district | `uninitialized` | local, no LLM (see §7) |
| `uninitialized` | edit description (name + description) | `initialized` | the LLM **optimises the operator's prompt**; this step is a text optimisation, not a generation |
| `initialized` | lock | `locked` | **one-way** |
| `locked` | copy | a NEW district in `initialized` | copies description + location + economic level; **copies no households** |
| any | delete | — | recoverable: moves to `output/_trash/` (§7) |

A `locked` row therefore offers exactly two actions: **copy** and **delete**.

### 18.3 Hard gate

The `household` and `home` build steps are runnable **only for a `locked` district**.
Before the lock the households pane is rendered **frosted and non-interactive** — a
disabled surface, not a hidden one. The gate is enforced in the backend
(`BuildStepStatus.runnable` / `blocked_reason`), not just in the UI: the Steps sheet and
the HTTP API must both refuse.

The treatment is `glass-lg` over the **list region only** (the pane's header strip with its
`Description` / `Steps` buttons stays outside the mask and therefore stays usable): the
table beneath carries `pointer-events-none` + `aria-hidden`, and the mask itself is a
centred lock-glyph in a `--surface-2` disc above the one-line reason. The mask never uses a
second Tailwind `backdrop-blur` — `glass-lg` already owns `backdrop-filter`, and stacking a
utility on top of it silently degrades the declared `blur(40px)` to the utility's 8px.
An unlocked district always has zero households (the gate forbids generating them first),
so the mask must state the rule itself rather than rely on dimmed content to imply it.

### 18.4 Action colours — recorded deviation

§1 principle 3 says colour is state only. The district row actions are a deliberate,
user-requested exception:

| Action | Colour | Icon |
| --- | --- | --- |
| edit description | `--success` | sparkles |
| lock | `--brand` (the cocoa neutral) | lock |
| copy (locked rows only) | `--fg-subtle` (grey) | copy |
| delete | `--danger` | trash |

They remain icon-only buttons with **no button chrome** (`ghost` + `icon-xs`), each with a
`title` and an `aria-label`. Because the colour is the only thing separating them, each
also keeps a **distinct icon**, so the row survives greyscale and colour-blind viewing (§8).

## 19. Centered panels, and empty masters

### 19.1 The centered panel

`SheetContent` gains a third variant, `side="center"` (it is still the Radix Dialog
primitive, so focus trapping, `Esc` and the scrim are unchanged):

| Property | Value |
| --- | --- |
| Position | `fixed inset-0 m-auto h-fit` — centred on both axes, never off-screen |
| Width | `w-[calc(100%-2rem)]` plus a per-instance `max-w-*`; the instance picks the measure |
| Height | capped at `max-h-[85dvh]`; the body is the scroll owner (`min-h-0 overflow-y-auto`) |
| Surface | `--surface` + 1px `--border` + `--r-xl` + `--shadow-3`, same as a drawer |
| Motion | `zoom-in-95` / `zoom-out-95` + fade (§6 tokens; no directional slide) |
| Width/measure | authoring panels `sm:max-w-lg`; a prose editor `sm:max-w-2xl`; an embedded table `sm:max-w-3xl` |

**Rule — which surface an action gets.** A surface that *authors or mutates* uses the
**centered panel**. A surface that only *inspects* uses the right-hand **drawer**. So the
five authoring surfaces — new world, new district, district description, household, steps —
are centred; `PipelineDrawer` (a read-only LLM-trace viewer) stays a drawer.

### 19.2 An empty master never leaves a blank detail pane

A `list-detail` screen (§17.3) whose master list is empty must **not** render the detail
pane at all — a half-blank two-column split was the reported defect. Instead the screen
collapses to a single centred **`cover`** (`layout-skill.md` §3): grid rows `auto 1fr auto`,
`min-height: 100%`, holding the empty-state title, the one-line explanation, and the screen's
**primary action** so the CTA is reachable from the empty state itself.

This applies to every list-detail screen, not just districts. Loading and error states keep
their existing full-width row treatment.

## 20. The floating window — a surface you watch while you work

### 20.1 Why a third surface type

§19 splits surfaces into two kinds: authoring uses the **centered panel**, inspection uses
the **drawer**. Neither can be watched *in parallel*: both are modal, so the page underneath
is inert while they are open. Monitoring is a third job — you start a job, then keep working
in Worlds while you watch the LLM calls and the live log.

**Rule.** A surface the operator must watch *while continuing to work* is a **floating
window**: non-modal, moveable, dismissible, and it never blocks the page. A surface that
must be answered before anything else continues stays modal (§19).

### 20.2 The `FloatingPanel` primitive

| Property | Value |
| --- | --- |
| Modality | **Non-modal.** No scrim, no focus trap, no `aria-modal`. The page underneath stays fully interactive. |
| Role | `role="complementary"` with an `aria-label` — it is an auxiliary region, not a dialog. |
| Position | `fixed`, default bottom-right (`right-4 bottom-4`), moved by dragging its header. |
| Size | `w-[min(920px,calc(100vw-2rem))] h-[min(600px,calc(100dvh-2rem))]`; the body owns its scroll (`min-h-0` + `overflow-hidden`, inner panes scroll). |
| Surface | `chrome-lg` (heavy frosted glass, §7) + `--shadow-3` + `--r-xl`. |
| Header | Title + live status + a close button (`ghost icon-xs`, `aria-label`). The header is the drag handle; a drag must not fire a click on its children. |
| Stacking | `z-40` — **below** the modal surfaces (`z-50`), so a confirmation panel always wins. |
| Keyboard | `Escape` closes it while it holds focus; nothing inside steals focus on open. |
| Motion | `--t-base` slide/fade on open, `transform`/`opacity` only (§6). |

Drag is `transform`-based (never `left`/`top`), begins only on the header, and is disabled
under `prefers-reduced-motion` (the window then stays at its default corner).

### 20.3 Jobs moves into the floating window

- The top bar drops the `Jobs` item: the nav is **`Worlds | Settings`**.
- The trigger is a top-bar icon button (`Activity`, `aria-label="Job activity"`) carrying a
  live count of `running`/`queued` jobs; it opens the floating window over whatever view is
  current, and the window stays open across view switches.
- The window's body is the existing `JobsPanel` (job list + `LLM calls` / `Live log` tabs) —
  no new job UI is invented, and no new fetch primitive is added.
- Open/closed lives in the store (`jobsOpen`) so it survives navigation but does **not**
  enter the URL: a shared link should not carry someone else's monitor state.
- `view=jobs` keeps working for old links: it renders the Worlds-family view underneath and
  forces the window open (`view=jobs` → effective view `worldsView`, window open).

## 21. Instrument headers — typography, not containers

§7 documented `WorldBadge` as a pill and the world header drew its counts in a `chip`. Two
rounded-rectangle tags of equal visual weight sat beside the world id, so the header reported
everything and ranked nothing.

**Rule.** A header that reports state and counts builds hierarchy from **type**, not from
containers:

| Element | Treatment |
| --- | --- |
| State (`Draft` / `Frozen`) | a 6px dot + an 11px `label-latin` micro-label. **Hollow** dot = draft, **filled** `--info` dot = frozen — state rides on shape as well as colour (§8). No border, no fill, no radius. |
| Counts | a `num` value at 13px/600 in `--fg`, then its noun in `label-latin`; the three pairs are separated by `1px --border` rules. The number leads, the label recedes. |
| Structural rules | `1px --border` — never `--border-strong`, which is reserved for inputs and chip outlines (§5). |
| Separators | one `h-4 w-px` rule after the back control; `h-3 w-px` rules between stat pairs. |

`chip` (§7) survives for **selectable** pills (`DistrictPromptFields`, `WorldBuilder` preset
pickers) and for in-canvas HUDs (`SceneStage`, `Town`) — it is no longer used for header
counts. `WorldBadge` keeps its name and both call sites (`WorldsList` rows, `WorldDetail`) so
the list and the header stay consistent.

`lib/format.ts` gained `nounLabel(value, singular)` so a bare noun can sit beside a separate
`num` value; `countLabel` now composes it and its output is unchanged.

## 22. Pane headers and their actions

### 22.1 Amendment to §17.2 rule 2 (primary-action assignment)

§17.2 rule 2 read "exactly one `default`-variant button per screen". Applying it literally to
the Households tab put the cocoa primary on **`New district`** — the action of the *list*
pane — while the pane you are actually working in had none. Amended:

**The cocoa primary belongs to the SELECTED item's pane.** So on the Households tab the
primary is the selected district's `Add household`, and `New district` is demoted to
`outline`. The empty state keeps its centred `default` CTA (it is the only action then, and
`New district` is not rendered). Still exactly one `default` button is visible.

### 22.2 Pane header contract

A detail pane's header carries **at most one primary and one secondary**, plus quiet icon
controls:

| Rank | Treatment |
| --- | --- |
| Primary | `default`, `size="sm"` |
| Secondary | `outline`, `size="sm"` |
| Tertiary (advanced / rare) | `ghost`, `size="icon-xs"`, `title` + `aria-label` only |

On the households pane: **`Description`** = secondary (`outline`, `Sparkles`),
**`Add household`** = primary, **`Steps`** = tertiary ghost icon (`ListChecks`) — the raw
step runner stays reachable without competing for attention.

### 22.3 The household action is state-gated (§18.3 made visible)

`Add household` is the visible form of §18.3's gate, so it renders the gate rather than
hiding it:

| District status | Button |
| --- | --- |
| `uninitialized` | disabled, `Lock` icon, reason `Write the district description first.` |
| `initialized` | disabled, `Lock` icon, reason `Lock this district first.` |
| `locked` | **enabled primary** — opens the count panel (§22.4) |

A disabled control must say what unblocks it, so each state carries its own reason in
`title` and `disabledReason`.

### 22.4 The count panel

`Add household` opens a centered panel (§19) holding a single **count** field (integer ≥ 1,
default 1) and the shared `JobSubmitBar` with the payload
`{ kind: "build", world, district, step: "household", count: n }`. It is the UI half of the
batch mode §18.2 stage 1 already implements — one LLM call producing `n` household
descriptions.

### 22.5 No restated state in the pane header

`DescriptionChip` is removed from the households pane header. Whether a description exists is
already the left table's `Status` column (§18.1), and §17.2 rule 5 forbids showing the same
state twice on one screen. The chip component itself survives for other callers.

## 23. Live generation state

### 23.1 The rule

While a build job is running, the surface that is **being filled** must say so — not leave the
operator guessing whether a click did anything. A job is "active" when its status is
`running` or `queued` (`isActiveJob`, `hooks/useWorldBuild`), and the wiring already polls
faster while one is active (`useBuildState`).

| Surface being filled | Treatment |
| --- | --- |
| A district row's `Status` cell (§18.1) | the status chip gains a leading spinner while any active job targets that district — the stored status stays visible, the spinner adds "and something is happening". |
| The households pane (the `household` step's output) | a one-line `Generating…` strip above the list, carrying the step label, plus the `View job` link (§23.3). |

The indicator is a `Loader2` at `size-3` with `animate-spin` and `motion-reduce:animate-none`
(§6 — motion serves meaning, and reduced motion still gets a static marker). Colour is
`--energy`, the documented "running / drawing power" state colour (§2) — never a decorative
accent.

### 23.2 Nothing else changes

The indicator never replaces the data it annotates: the status chip keeps its word, the
households list keeps its rows and its empty/loading/error states (§17.3), and the frosted
lock mask (§18.3) keeps precedence — an unlocked district has no active job by construction.

### 23.3 `View job` — a text link, not a button

The link is **tertiary** (§22.2): plain text in `label-latin`, `--fg-muted`, underlined on
hover, with no button chrome. Pressing it opens the floating job window **focused on that
job** so the live log and LLM calls are on screen immediately, rather than a window listing
everything with nothing selected.

Wiring: `store/time.ts` gains `jobsFocus: string | null` and `openJob(jobId)` (which sets
`jobsOpen = true` **and** `jobsFocus = jobId`); `FloatingJobsWindow` forwards it as an optional
`focusJobId` prop on `JobsPanel`, which seeds its selected row from it and re-seeds when it
changes. Neither the focus nor the open flag enters the URL (§20.3).

## 24. Flat surfaces — the card material is retired

**Supersedes §15's material.** §15 re-skinned the console with frosted glass, three soft
shadows and `--r-xl` cards. §0's Layer A is `minimalist-skill.md`, which forbids heavy shadows
and asks for 1px structural lines — the glass/card material had drifted away from the style
skill the project chose. This section returns to it.

| Was (§15) | Now |
| --- | --- |
| `card` = `--surface` + 1px border + `--r-xl` + `--shadow-1` | frame + 1px `--border`, `--r-md`, **no shadow** |
| `chrome` / `chrome-lg` = frosted glass (72% wash + `backdrop-filter`) | flat `--surface` + 1px `--border`, `--r-md`, no blur |
| `glass` / `glass-lg` = frozen glass | flat `--surface-2`, no blur; a masked region is opaque and marked by `aria-hidden` + `pointer-events-none` (§18.3) |
| `--shadow-1/2/3` | resolve to **none** (the tokens stay declared so nothing breaks) |
| `--r-xl` 18px · `--r-lg` 10px · `--r-md` 8px | `--r-xl` 10px · `--r-lg` 8px · `--r-md` 6px |
| hover = lift (`translateY` + shadow) | hover = `--item-hover` wash only — no lift, no shadow |

Rules:

1. **Elevation is background, never shadow.** Raised = `--surface-2` / `--surface-3`; resting = `--surface`. `--bg` is the page.
2. **Exactly one structural line width: 1px.** `--border` for structure; `--border-strong` only for inputs and chip outlines (§5).
3. **Opaque only.** With no blur left, no surface may be translucent (§1's rule survives its reason): every surface resolves to a solid colour. `--overlay` stays translucent — it is a modal scrim, not a surface.
4. **Motion is colour, not position.** `card-lift` loses its translate; hover and press are background/colour transitions (§6).
5. **The dot grid stays** on `body` over the flat `--bg` — texture is not material, and a completely untextured flat page reads sterile (`minimalist-skill` §6).

**Migration.** Because `card` / `chrome` / `glass` / `card-lift` are redefined in `index.css`,
every existing usage becomes flat without touching its file. The per-screen sweep is then only
about leftovers — pill-shaped tags, spacing, and the surfaces that used to justify their shape
by elevation.

### 24.2 Regions, not boxes

§24 removed the *depth* from the cards but left the **boxes**: 21 `card` shells were still
bordered, rounded rectangles separated by a `gap-3`, which is the card style itself. A flat
console separates its areas with **hairlines, not gaps**:

| Element | Treatment |
| --- | --- |
| A pane (`card`) | a flat region on `--surface` — **no border, no radius, no shadow** |
| The page gutter (`main`) | the only outer spacing (`p-3 lg:p-4`) |
| Between horizontal neighbours | `gap-0`, and the **leading** region carries `border-r border-border` |
| Between stacked neighbours | `gap-0`, and the upper region carries `border-b border-border` |
| A bar (`chrome`) | full-width, **radius 0**, 1px bottom hairline |
| A floating surface (the centered panel §19, the floating window §20, `chrome-lg` popovers and drawers) | **keeps `--r-md`** — it is a control-like object hovering over the page, not a region of it |
| Inner elements (inputs, buttons, chips, tags) | keep `--r-md` / `--r-sm` — crisp outside, soft inside |

So one continuous flat surface is subdivided by 1px lines instead of being cut into floating
tiles. Radius is a property of *controls and floating objects*, never of *areas*.

## 25. Resizable panels

A column of stacked panels (§7's `Panel`) splits the available height by flex weights, so a
panel that needs more room — the activity timeline with six members, a floor plan — gets
squeezed and clipped instead. The operator, not the layout, should decide the split.

### 25.1 The handle

Every `Panel` carries a **drag handle** on its bottom edge:

| Property | Value |
| --- | --- |
| Appearance | a 1px `--border` hairline flush with the panel's bottom; it thickens to 3px and turns `--brand` while hovered or dragged, so the affordance is visible without adding chrome |
| Cursor | `row-resize` on the handle and on the 8px hit strip above it |
| Behaviour | dragging sets an explicit pixel height on that panel; until the first drag the panel keeps `flex: 1` and the handle is inert |

### 25.2 Bounds and neighbours

`MIN_PANEL_PX` 140 · `MAX_PANEL_PX` 1200. A panel below the minimum is not allowed; a panel
larger than the column simply makes the column scroll (the columns already own their scroll,
§24.2). Panels that were never dragged keep `flex: 1` and absorb whatever is left, so a single
drag re-splits the column without touching the others.

### 25.3 Persistence and a11y

- The height is stored per panel in `localStorage` under `llmworld.panel.<panelId>.height`, so
  a working layout survives a reload. It is **not** put in the URL (§20.3 — a shared link must
  not carry someone else's layout).
- The handle is a `role="separator"` with `aria-orientation="horizontal"`, an
  `aria-label` naming the panel, and `aria-valuenow` in pixels. It is focusable, and `ArrowUp`
  / `ArrowDown` resize by 16px (a keyboard path must exist — §8).
- The drag is direct manipulation, so it has no transition and no `prefers-reduced-motion`
  branch: §6 forbids animating layout properties, it does not forbid the user moving them.

## 26. The Watch layout — a hero timeline

The detail layer exists to read one artefact: the day's activity across every member. §24.2
gave it three equal columns, so the timeline got 787px of a 1440px window — barely half a day
visible at a time — while six panels of context competed at the same visual weight. That is
what "no design sense, tiring to look at" describes: no hero, everything equal.

### 26.1 The layout

```
┌ support row ────────────────────────────────────────────────────────────┐
│ floor plan │ member cards │ load curve │ snapshot · switcher · pipeline │
├── drag divider ─────────────────────────────────────────────────────────┤
│ ACTIVITY TIMELINE — full width, pinned to the bottom                    │
└─────────────────────────────────────────────────────────────────────────┘
```

- The timeline is **full width** (it is the artefact) and pinned to the **bottom** of the
  layer, so it never has to share a column.
- The support row above holds the context panels at equal width; it scrolls on its own.
- One **drag divider** between them sets the split, so the operator can give the timeline
  everything (the timeline panel is `flex-none` and sizes to its own content — §25's handle
  does not apply to it, its height is content-driven and its own min-height wins).

### 26.2 `ResizableColumns`

A two-region primitive, generalised from the same mechanics as §25:

| Property | Value |
| --- | --- |
| Shape | `ResizableColumns({ first, second, storageId })` — a `1fr / divider / 1fr` grid of COLUMNS |
| Handle | the same 1px hairline, thickening to 3px in `--brand` on hover, focus and drag |
| Bounds | both columns keep ≥ 260px; clamped on every change |
| Keyboard | `role="separator"`, focusable, `←/→` move the divider by 24px |
| Persistence | `localStorage` under `llmworld.split.<storageId>`, never the URL |
| Responsive | below `lg` the two panes render as a plain stack and the divider is not rendered |

Used for the districts | households columns of the Households tab.

**Why there is no split around the timeline.** §26.1 pins the timeline to the bottom at
**content height** (`flex-none`, `AXIS + lanes × 54`). A region that is exactly as tall as its
own content has nothing to allocate, so a divider there would only create the blank band this
section exists to remove. The timeline is never squeezed because it is not in a flex race at
all — which is the outcome the drag would otherwise have been used to achieve.

## 27. Document-scale layout — one concern per panel

§24.2 and §25 assumed a **fixed-height shell**: every view filled the viewport, so panels
competed for height, got squeezed, and needed handles to be re-split. That competition is the
source of every compression and clipping defect reported since. This section removes the
assumption instead of managing it.

### 27.1 The shell stops clamping

- `main` **scrolls** (`overflow-y-auto`) rather than `overflow-hidden`, and a view's root takes
  natural height instead of `h-full`. A view that needs 2000px makes the page 2000px long.
- Nothing is sized against the viewport height, so nothing can be squeezed by a neighbour.
- The page keeps one scroll owner: `main`. Panels do not scroll internally unless their content
  is genuinely unbounded (a log, a long list).

### 27.2 One concern per panel

A panel holds exactly one thing. Two panels stacked inside one column (a floor plan above a load
curve) is forbidden — each gets its own full-width panel. Panels stack in **one column**,
separated by the §24.2 hairline, and each is full width.

### 27.3 §25's drag handles are retired

They existed to re-split a competed height. With nothing competing they are affordance without a
job, so `Panel` returns to a plain region and `hooks/usePanelHeight.ts` is deleted. (§26.2's
`ResizableColumns` stays available for the one case where two regions genuinely share a width —
the districts | households columns — but it is not applied to stacked panels.)

### 27.4 The play bar becomes a floating toolbar

The single place §15's material returns: a bottom-centred **`chrome-lg`** bar — frosted glass,
`--r-pill`-adjacent radius, `--shadow-3` — pinned to the **viewport** bottom, holding only what a
transport needs:

| In the bar | Moved out |
| --- | --- |
| the time readout, `Back to 00:00`, `Previous step`, `Play`/`Pause`, `Next step`, `Jump to 24:00` | step size, continuous vs step, speed — collapsed into one compact disclosure inside the bar |

Content carries bottom padding equal to the bar's height plus the gutter, so the bar never hides
the last panel.

### 24.1 The floating window holds at any size

§20's window was laid out with viewport breakpoints (`lg:grid-cols-[…]`), so shrinking the
*window* never reflowed its inside — the list column kept a 340px floor and its rows broke.
The window's body must respond to **its own width**, not the viewport (`layout-skill.md` §4):
`JobsPanel` wraps its two regions in a `container-type: inline-size` parent and switches to a
single stacked column below `~640px` of *container* width, list first. The viewport `lg:` grid
is removed.
