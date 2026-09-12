# R180 — TOU 价差敏感性：**null**（7× 峰谷价差无剂量-反应）

- **轮次**：Round 180
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（world_838587 h002 M1；`tou:0.5,0.18`×15 vs `tou:1.2,0.18`×15；~120 calls）
- **结论**：⚪ **null**：峰谷价差放大 **7×**（峰 0.50→1.20 AUD/kWh）**不显著改变**峰（+1.6%）、总（−3.7%）、谷（+4.8%）
  → **无价格剂量-反应**（guide §2.1 的"调费率做敏感性"实验）。

---

## 1. 目标

guide §2.1 建议"tune the peak/valley rate gap for sensitivity analysis"。检验**更强价格信号是否引起更强移峰**
（RQ2：价格弹性；Albadi & El-Saadany 2008 / Wang 2021）。

## 2. 方法（可复现）

```powershell
foreach ($i in 1..15) {
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "toulo_$i" --policy "tou:0.5,0.18" --workers 1
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "touhi_$i" --policy "tou:1.2,0.18" --workers 1
}
python src/analyze/compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-11 `
  --base-prefix toulo --treat-prefix touhi --n 15 --tag tou --base-tag tou
```
（`compare_cpp.py` 新增 `--base-tag`——两臂同为 `tou` 标签。）

## 3. 结果（n=15，低价差 → 高价差）

| 指标 | tou:0.5,0.18 | tou:1.2,0.18 | Δ | t | p |
|---|---|---|---|---|---|
| 总电量 | 8.576 | 8.259 | −3.7% | −0.45 | 0.66（n.s.） |
| 峰段 16–21 | 3.521 | 3.578 | **+1.6%** | +0.16 | 0.88（n.s.） |
| 谷期 22–7 | 2.011 | 2.107 | +4.8% | +0.20 | 0.84（n.s.） |
| 峰值功率 | 3537 | 3793 | +7.2% | +0.52 | 0.61（n.s.） |

## 4. 解读

1. **无剂量-反应**：峰谷价差 2.4×→6.7×（峰率 0.5→1.2，**7× 差**）**不改变**峰/总/谷 → agents **对价格不敏感**；
2. **与 TOU null 一致**（R114：n=15 峰 −3.2% n.s.）→ 不仅"无效应"，且"**无价格梯度效应**"；
3. **机制**：LLM agents 主要响应**显式指令/结构信号**（如 ac_tax 的设备+窗口、holiday 的停留），
   **非**数值价格弹性（cf. Wang 2021"习惯主导"）；
4. **功效**：即使真有效应，也低于平台下限（R058）。

## 5. 论文更新

- `paper/README.md`：`tou` 行补注"**价差敏感性 null**（7× 价差无剂量-反应，R180）"。

## 6. Validity

- same-era 配对、n=15；单住户、单世界、单日。
- 限制：仅调峰率（谷率固定）；更高价差未测。

## 7. token

- 约 **120 次调用**。
