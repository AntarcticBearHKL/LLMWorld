# R198 — 交通罢工第 3 世界 ✅：总 +29.3% → **第 7 个 headline**

- **轮次**：Round 198
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（world_143345 h002 M1；baseline×15 + `transport_strike`×15；~120 calls）
- **结论**：✅ **跨 3 世界达成**：总 **+29.3%（t=+2.28, p=0.039）**；三世界 **+33.9% / +22.2% / +29.3%**
  → **transport_strike 升为 headline（第 7 个）**。

## 1. 结果（n=15，三世界）

| 世界 | 总电量 Δ | p |
|---|---|---|
| W1 `838587` h002 | **+33.9%** | 0.028 |
| W2 `172148` h002 | **+22.2%** | 4.2e-4 |
| **W3 `143345` h002** | **+29.3%** | **0.039** |

## 2. 解读
1. **三世界总 +22~34%（全显著）** → stay-home 机制族的**第 3 个 headline**（holiday / wfh / **transport_strike**）；
2. **高度一致**（+22~34%，比 holiday 稳）→ "结构性冲击 → 居民居家 → 总用电 +~30%" 稳健；
3. 机制族全景：**强制 lockdown / 日历 holiday / 办公安排 wfh / 交通 transport_strike / 周期 weekend**
   → 同一"**居家时间↑ → 日间用电↑**"，且剂量与**基线工作日离家程度**相关（R190/R195）。

## 3. 论文更新
- `paper/README.md`：headline 表加 transport_strike 行（跨 3 世界）；
- `paper/experiments/event_transport_strike.md`：升级为 cross-world headline。

## 4. token
- 约 **120 次调用**。
