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

**重组结论（不照抄任何来源）**：底色由 Sentry 的深紫改为**深青黑**（能源/仪表的冷色仪器感），强调色用**青绿**，`on` 语义用**暖琥珀**——青绿 × 琥珀是仪表盘的经典互补对。夜间睡眠/外出等"低信息"活动刻意降饱和，把饱和度留给真正发生的用电行为。

## 1. Design Principles

1. **数据密集但安静** — 信息靠排版层级和留白分隔，不靠色块和阴影。
2. **时间是一等公民** — 所有时间/数值用等宽 + `tabular-nums`，字宽不跳动。
3. **颜色即语义** — 青绿=交互，琥珀=用电中，石板灰=静止/缺席。装饰性用色一律禁止。
4. **深色优先，浅色可用** — 两套主题共用同一组语义 token 名。
5. **动效服务意义** — 只动 `transform` / `opacity`；不做无信息量的悬停动画。

## 2. Color System

所有色值以 CSS 变量形式定义在 `src/index.css`，dark 为 `:root` 默认，light 在 `.light` 覆盖。
组件只允许写 `var(--…)` 或 Tailwind token（`bg-surface` / `text-fg-muted` / `border-border`）。

### 表面 / 文本（dark 默认）

| Token | Dark | Light | 用途 |
| --- | --- | --- | --- |
| `--bg` | `#0A0F12` | `#FAFAF9` | 页面底色 |
| `--surface` | `#0F161A` | `#FFFFFF` | 卡片 |
| `--surface-2` | `#141D22` | `#F4F4F2` | 卡片内嵌区 / 表头 |
| `--surface-3` | `#1A252B` | `#EAEAE7` | hover / 激活底 |
| `--border` | `#1E2A30` | `#E7E5E4` | 1px 结构线（默认） |
| `--border-strong` | `#2A3840` | `#D6D3D1` | 输入框 / 分隔强调 |
| `--fg` | `#E7EDF0` | `#1A1D1F` | 主文本（不用纯黑/纯白） |
| `--fg-muted` | `#93A4AC` | `#57534E` | 次要文本 |
| `--fg-subtle` | `#64757E` | `#8A8580` | 标签 / 单位 |

### 语义

| Token | Dark | Light | 语义 |
| --- | --- | --- | --- |
| `--accent` | `#2FC4B2` | `#0E8F80` | 交互主色（青绿） |
| `--accent-fg` | `#04211E` | `#FFFFFF` | 强调底上的文本 |
| `--accent-soft` | `rgba(47,196,178,.14)` | `rgba(14,143,128,.10)` | 选中底 / 焦点环底 |
| `--energy` | `#F5A524` | `#B45309` | **用电中**（暖琥珀，电器 on） |
| `--energy-soft` | `rgba(245,165,36,.14)` | `rgba(180,83,9,.10)` | 用电徽章底 |
| `--success` | `#3DD68C` | `#047857` | 完成 / 正常 |
| `--danger` | `#F2555A` | `#B91C1C` | 失败 / 警告 |
| `--info` | `#5B9DFF` | `#1D4ED8` | 中性提示 |

### 成员泳道色（仅用于泳道标识，不用于语义）

`--member-1 #2FC4B2` · `--member-2 #7C9CFF` · `--member-3 #C084FC` · `--member-4 #FB923C`

### 活动分类色（时间轴色块 = 分类，非成员）

| 分类 | token | Dark | 说明 |
| --- | --- | --- | --- |
| 睡眠 `sleep` | `--cat-sleep` | `#3F4E5A` | 刻意低饱和——占全天一半以上，不应抢注意力 |
| 用餐 `meal` | `--cat-meal` | `#E8A33D` | 琥珀 |
| 家务 `chore` | `--cat-chore` | `#2FC4B2` | 青绿 |
| 学习工作 `focus` | `--cat-focus` | `#7C9CFF` | 蓝紫 |
| 休闲 `leisure` | `--cat-leisure` | `#C084FC` | 紫 |
| 外出 `away` | `--cat-away` | `#4B5A64` | 灰 + 虚线描边 = "不在此处" |

色块渲染公式（在 JS 中预计算，不依赖 `color-mix`）：
背景 `alpha(cat, .22)` · 描边 `1px alpha(cat, .45)` · 文本 `alpha(cat, .92)` 提亮 · 左侧 3px 实心条 = 成员色。

## 3. Typography

| 角色 | 字体 | 规格 |
| --- | --- | --- |
| UI（默认） | `ui-sans-serif, system-ui, -apple-system, "Segoe UI Variable Text", "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei UI", "Microsoft YaHei", sans-serif` | — |
| 数值 / 时间 | `"JetBrains Mono", "Cascadia Mono", "SFMono-Regular", Consolas, "Liberation Mono", monospace` | `font-variant-numeric: tabular-nums` |

> **为何不用 webfont**：本地离线研究工具，webfont 请求失败会触发 FOUT/布局跳动；中文子集体积过大。
> 对比度改由**排版层级**建立：微标签大写 + 宽字距、超大等宽读数、标题负字距。

| 层级 | 字号 / 行高 | 字重 | 字距 | 用途 |
| --- | --- | --- | --- | --- |
| Display 时间读数 | `34px / 1.0` | 500 | `-0.02em` | 时间控制条 `HH:MM`（等宽） |
| 指标数值 | `24px / 1.15` | 500 | `-0.01em` | 指标条 kWh / W（等宽） |
| 面板标题 | `14px / 1.3` | 600 | `-0.01em` | 卡片头 |
| 正文 | `13px / 1.55` | 400 | `0` | 描述 |
| 次要 | `12px / 1.5` | 400 | `0` | 提示 |
| 微标签 (CJK) | `11px / 1.2` | 500 | `0.08em` | 指标名 / 分组名 |
| 微标签 (Latin) | `10px / 1.2` | 600 | `0.14em` + `uppercase` | 单位 `KWH` / `W` / 状态码 |

## 4. Spacing & Layout

基准 **4px**，Tailwind 刻度直接映射：`1=4 2=8 3=12 4=16 5=20 6=24 8=32 10=40 12=48`。

- 卡片内边距：`p-4`(16) 常规、`p-5`(20) 主面板；卡片间距 `gap-3`(12)。
- 页面外边距：`px-4 lg:px-5`，纵向 `gap-3`。
- 结构：`header`（粘顶，磨砂）→ `main` 三栏 `grid-cols-[minmax(0,320px)_minmax(0,1fr)_minmax(0,340px)]`（`<1280px` 折为单列）→ `footer` 时间控制条（粘底）。
- 内容宽度：主区不受 `max-w` 限制（研究工具，屏幕即画布），但左右面板最小宽 300px。

## 5. Radii / Elevation / Borders

| Token | 值 | 用途 |
| --- | --- | --- |
| `--r-sm` | `6px` | 输入、徽章、kbd |
| `--r-md` | `10px` | 按钮、色块 |
| `--r-lg` | `14px` | 卡片、面板 |
| `--r-xl` | `18px` | 抽屉、浮层 |
| `--r-pill` | `9999px` | 状态点、极小徽章 |

- 结构线**永远 1px**，用 `--border`；禁止 ≥2px 的装饰边框。
- 阴影：仅两档。`--shadow-1: 0 1px 2px rgba(0,0,0,.32)`（浮层）；`--shadow-2: 0 18px 40px -12px rgba(0,0,0,.55)`（抽屉/弹层）。
  卡片默认**无阴影**，靠 1px 描边与底色差分层。禁止 Tailwind `shadow-md/lg/xl` 默认值。
- 主按钮加内阴影 `inset 0 1px 0 rgba(255,255,255,.08)` 形成可按压的实体感。
- 磨砂：`backdrop-filter: blur(18px) saturate(180%)`，仅用于 header / footer / 弹层。

## 6. Motion

| Token | 值 | 用途 |
| --- | --- | --- |
| `--t-fast` | `120ms` | hover / 焦点 |
| `--t-base` | `180ms` | 展开、tab 切换 |
| `--t-slow` | `320ms` | 面板入场 |
| `--ease` | `cubic-bezier(0.16, 1, 0.3, 1)` | 全局 |

- 只动 `transform` / `opacity`。禁止动 `top/left/width/height`。
- 入场：`translateY(6px) + opacity 0 → 1`，`--t-slow --ease`，同组元素按 `index * 40ms` 级联。
- `:active` 主按钮 `scale(0.985)`。
- **播放游标不做补间动画**——它由 `minute` 直接驱动，逐帧位移即真实数据；不得额外加 transition 造成滞后。
- 遵循 `prefers-reduced-motion: reduce`：关闭入场位移与级联。

## 7. Component Primitives

| 原语 | 文件 | 契约 |
| --- | --- | --- |
| `Button` | `components/ui/button.tsx` | shadcn；`default` 用 `--accent`，`outline` 用 1px `--border-strong` |
| `Card` | `components/ui/card.tsx` | shadcn；本项目覆盖为 `bg-surface` + `1px --border` + `--r-lg` + 无阴影 |
| `Panel` | `components/primitives/Panel.tsx` | 研究台统一面板：`title` / `hint` / `actions` / `children`，头部分隔线 1px |
| `MetricCell` | `components/primitives/MetricCell.tsx` | 微标签 + 等宽数值 + 单位，固定 `min-w` 防跳动 |
| `StatusDot` | `components/primitives/StatusDot.tsx` | 8px 圆点，`on`=`--energy`，`off`=`--fg-subtle` |
| `TimeReadout` | `components/primitives/TimeReadout.tsx` | 等宽 `HH:MM`，`tabular-nums` |

**活动分类推导**（`lib/activity.ts`）：后端 `ActivitySegment` 无 `category` 字段，前端按关键词映射到 6 个分类，映射表集中在一处，未命中 → `leisure`。这是展示层推导，**不新增任何 API 字段**。

## 8. Responsive & Accessibility

断点：`<768px` 单列堆叠；`768–1279px` 双列（时间轴占满，两侧面板落到下方）；`≥1280px` 三列。

- 所有交互元素 `min-height: 32px`，图标按钮 `32×32`；`focus-visible` 统一 `2px --accent` + `offset 2px`。
- 颜色对比：正文 `--fg` on `--bg` ≥ 12:1；`--fg-muted` ≥ 5.5:1；`--accent` on `--bg` ≥ 7:1。
- 时间轴色块文本用提亮后的分类色，实测对比 ≥ 5:1。
- 语义靠**颜色 + 形状**双通道：`away` 用虚线描边，用电状态除颜色外用 `StatusDot` 实心/空心区分。
- 键盘：`Space` 播放/暂停，`←/→` ±15min，`Shift+←/→` ±60min，`Home/End` 首尾；焦点在输入框/下拉内时不劫持按键。
- 页面 `lang="zh-CN"`；图表容器带 `aria-label`；`prefers-reduced-motion` 降级。

## 9. Accepted Debt

| 项 | 原因 | 偿还条件 |
| --- | --- | --- |
| 使用 Lucide（minimalist-skill 禁用） | 任务硬性要求 | 若后续引入 Phosphor/Radix Icons 可替换 |
| 无 webfont，靠系统字体栈 | 本地离线工具，避免 FOUT 与中文子集体积 | 若打包内嵌字体子集可升级 |
| `HouseFloorplan` / `SnapshotPanel` / `EnergyChart` / `PipelineDrawer` 为占位壳 | 属后续里程碑范围 | 对应里程碑实现后替换 |
| 活动分类为前端关键词推导 | 契约无 `category` 字段 | 若后端新增字段则改为直读 |
| vis-timeline 自带 DOM 结构，部分样式靠 `!important` 覆盖 | 第三方库样式优先级 | 若自绘时间轴则移除 |

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
  types.ts             冻结契约：SceneState / CharacterPose / AppliancePose / RoomPose / TownHouse
  layout.ts            确定性户型布局（切片切分 + 邻接图 + 门点 + 房间间路径）
  lighting.ts          昼夜光照纯函数（night / tint / peakWindow / lampRooms）
  tokens.ts            canvas 内解析 CSS 变量（getComputedStyle + 主题变更重读）
  appliances.ts        电器字形 / 状态色调 / 房间内槽位
  effects.ts           电器特效判定（steam / airflow / screen / ring / drum / glow）
  useSceneState.ts     DayReplay + minute → SceneState（唯一派生入口）
  SceneStage.tsx       Stage + 命令式相机（滚轮/拖拽/双击复位/自动取景）+ 光照覆盖层
  RoomLayer.tsx        房间地板 / 墙体 / 房间名 / 即时瓦数 / 外出带状区
  ApplianceLayer.tsx   电器精灵（四态 + 呼吸/循环脉冲 + 悬停 tooltip）
  CharacterLayer.tsx   角色（沿房间路径补间行走 / 睡眠 Z / OUT 徽标 / 轨迹）
  EffectLayer.tsx      特效层（单动画驱动，不拦点击）
  AgentHud.tsx         角色详情（人格 / 当前活动 / 在用电器 / 接下来 / Esc 关闭）
  Town.tsx             小镇视图（房屋阵列 + 缩放平移）
  HouseBuilding.tsx    单栋房屋（窗户点亮数 ∝ 负荷 + 负荷条 + OUT 徽标）
  SceneView.tsx        组合器：小镇 ↔ 室内、特效/轨迹开关、成员选择条、无障碍摘要
```

### 11.2 自测清单

| # | 项 | 结果 | 证据 |
| --- | --- | --- | --- |
| 1 | 布局确定性、无重叠、铺满、连通 | ✅ | `node src/scene/layout.selftest.ts` → **34 passed / 0 failed** |
| 2 | 光照单调性、无跳变（单分钟 Δ<0.01）、色值合法 | ✅ | `node src/scene/lighting.selftest.ts` → **18 passed / 0 failed** |
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

### 12.3 未执行的文件级目录拆分（及原因）

`src/scene/` 目前是 20 个文件的平铺目录。按 §12.2 拆成 `core/ layers/ views/` 三个子目录在结构上更清晰，但**本轮未执行**，原因：

1. `dashboard/` 在 git 中仍是**未跟踪状态**（`?? dashboard/`），没有版本控制安全网；20 个文件 + 约 30 处 import 的批量移动一旦留下半成品，无法一键回滚。
2. 收益偏小：现有文件名已按角色自解释（`*Layer` / `Scene*` / `use*` / 纯逻辑单词名），20 个文件的平铺仍在可导航范围。

建议：先 `git add dashboard/` 建立基线提交，再做移动（届时每步都可 `git checkout` 回退）。

### 12.4 UI 架构（当前）

```
┌ 顶栏（全局，glass 吸顶）
│  BrandMark │ 工作区切换（观察 │ 控制） │ 选择控�制 run/date/house/policy │ 主题
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

