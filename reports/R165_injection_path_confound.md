# R165 — 注入路径混淆（B-x3）澄清：**preset vs custom 同内容 → 无显著差异**（路径非混淆）

- **轮次**：Round 165
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（world_838587 h002 M1；`--event-template` 与 `--event` **同标题同内容**，各 n=15；~120 calls）
- **结论**：✅ **路径本身不是混淆**：同文本 preset vs custom **各指标均无显著差异**（总 −5.1%、峰 +6.3%、谷 −20%，均 n.s.）
  → R157/R158 的"preset 降峰 / custom 反升"差异来自**内容不同 + 小样本**，非注入路径。

---

## 1. 目标（B-x3）

R157（custom 通用晚峰税 → 峰 **+18.9%**，n=9）与 R158（preset storm → 峰 **−21.1%**，n=9）曾提示
**注入路径（`--event` vs `--event-template`）** 可能是混淆。但二者**内容也不同**（tax vs storm），无法分离。
本轮用**完全相同的文本**只变路径，干净分离。

## 2. 方法（可复现）

```powershell
# preset 臂：内容取自 NEWS_TEMPLATES["storm"]
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "stormp_$i" --event-template "2026-09-11|storm" --workers 1
# custom 臂：逐字相同文本
python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "stormc_$i" --event "2026-09-11|Severe storm|A severe storm is expected this evening, with possible local power outages." --workers 1
# i = 1..15；比较
python src/analyze/compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-11 --base-prefix stormp --treat-prefix stormc --n 15 --tag baseline
```

**等价性核验**：两臂注入 prompt 的新闻行**逐字相同**（`- (2026-09-11) Severe storm: A severe storm is expected…`）；
storm 不在 `EVENT_WEATHER_EFFECTS` 中 → 两臂**天气字段也相同** → 唯一差异是 `template` 字段（惰性）与代码路径。

## 3. 结果（n=15，配对 t，df=14）

| 指标 | preset | custom | Δ | t | p |
|---|---|---|---|---|---|
| 总电量 | 8.972 | 8.511 | −5.1% | −1.47 | 0.16（n.s.） |
| 峰段 16–21 | 3.583 | 3.810 | +6.3% | +0.88 | 0.39（n.s.） |
| 谷期 22–7 | 2.509 | 2.008 | −20.0% | −1.17 | 0.26（n.s.） |
| 峰值功率 | 3970 | 3694 | −7.0% | −0.95 | 0.36（n.s.） |

## 4. 解读（B-x3 结论）

1. **同内容下路径无差异**：全部指标 n.s. → **"preset vs custom" 本身不是混淆变量**。
2. **R157/R158 的差异归因**：来自 **(a) 内容（通用税 vs 风暴）** + **(b) n=9 小样本**（R159 已示 preset storm
   n=15 → null，n=9 的 −21.1% 是假象）。
3. **对既有实验的影响**：N4/N5/N9（custom 通用事件"抬升"）**不应**归因为"路径伪影"；更可能是
   **内容（通用/含混）+ world_838587 h002 特异反应性**（与 R146 世界特异一致）。
4. **红线修正建议**：goal.md 红线 4 由"注入路径混淆"改为"**通用/含混内容 vs 设备特异内容是主要混淆；
   注入路径经同内容对照排除（R165）**"。

## 5. Validity

- same-era 配对、n=15、**同内容**对照（文本逐字核验）；单住户、单世界。
- 限制：仅 storm 一种内容；其它内容（税/信息）的路径对照未测，但机制上路径已证惰性。

## 6. token

- 约 **120 次调用**（preset×15 + custom×15）。
