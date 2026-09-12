# R171 — TOU + 实时反馈（IHD）组合：**方向为"移峰"但均 n.s.**（无 Jessoe ×3 放大）

- **轮次**：Round 171
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（world_838587 h002 M1；baseline×15 + `--policy "tou,in_home_display"`×15；~120 calls）
- **结论**：⚪ **null（方向一致、功效不足）**：峰段 **−6.8%（t=−0.70, n.s.）**、谷期 **+10.5%（n.s.）**、
  总电量 +6.7%（n.s.）→ 呈**移峰方向**（峰↓谷↑），但**未出现** Faruqui/Jessoe 的 TOU+IHD 放大（10–30%）。

---

## 1. 目标

guide §4.2 / Jessoe & Rapson (2012)：实时反馈（IHD）应**放大**价格响应（弹性 ×3），TOU+IHD 削峰从 3–6%
升至 **10–30%**（Faruqui & Sergici 2010）。检验组合是否强于 TOU 单独（R114 null：峰 −3.2%）。

## 2. 方法（可复现）

```powershell
foreach ($i in 1..15) {
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "ihd_b_$i" --workers 1
  python run.py --mode simulate --world world_838587 --house house_0002 --member 0 --date 2026-09-11 --env "ihd_t_$i" --policy "tou,in_home_display" --workers 1
}
python src/analyze/compare_cpp.py --world world_838587 --house house_0002 --date 2026-09-11 --base-prefix ihd_b --treat-prefix ihd_t --n 15 --tag "tou+in_home_display"
```

## 3. 结果（n=15，配对 t，df=14）

| 指标 | baseline | tou+IHD | Δ | t | p |
|---|---|---|---|---|---|
| 总电量 | 8.383 | 8.945 | +6.7% | +1.23 | 0.24（n.s.） |
| 峰段 16–21 | 3.522 | 3.282 | **−6.8%** | −0.70 | 0.50（n.s.） |
| 谷期 22–7 | 1.822 | 2.013 | **+10.5%** | +0.43 | 0.67（n.s.） |
| 峰值功率 | 3677 | 4079 | +11.0% | +1.22 | 0.24（n.s.） |

## 4. 解读

1. **方向正确、幅度未定**：峰 **−6.8%**、谷 **+10.5%** → 典型**移峰方向**（峰↓谷↑），幅度落在
   Faruqui 纯 TOU 区间（3–6%）附近；但**均 n.s.**（噪声地板 CV≈12%，R057/R058 → 该量级不可判）；
2. **未见 ×3 放大**（Jessoe）：组合未把峰削到 10–30%；仅与纯 TOU 同量级（甚至更弱于纯 TOU 的 −3.2% 方向）;
3. **对比 R114（TOU 单臂）**：单臂峰 −3.2% / 总 +5.4%；组合峰 −6.8% / 总 +6.7% → **名义上略有增强**，
   但在功效地板内**不可区分**；
4. **结论**：该平台**无法分辨文献尺度（3–6%）的 TOU/IHD 效应**（R058 已证），组合与单臂同为 null。

## 5. 论文更新

- `paper/README.md`：`in_home_display` 行补注"TOU+IHD 组合亦 null（峰 −6.8% n.s.，无 ×3 放大）"。

## 6. Validity

- same-era 配对、n=15；单住户、单世界、单日。
- 限制：文献尺度效应低于平台可测下限（R058）；组合顺序/措辞未变体测试。

## 7. token

- 约 **120 次调用**（baseline×15 + combo×15）。
