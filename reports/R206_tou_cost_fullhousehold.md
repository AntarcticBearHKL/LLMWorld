# R206 — TOU+cost **全户级**验证（2 成员）：峰 −3.1%（t=−5.57, p=0.0005）

- **轮次**：Round 206
- **日期**：2026-09-12
- **验证层级**：**L2 真调**（world_172148 h002 **全 2 成员**；baseline×9 vs TOU+cost×9；共享 s4-only 时间线；~36 calls）
- **结论**：✅ 全户聚合 **峰 −3.1%（t=−5.57, p=0.0005）**、谷 +3.7%（n.s.）、总 −2.2%（p=0.063）
  → cost-context 移峰**在住户级成立**（非 M1-only 伪影），幅度小于 M1-only。

## 1. 方法（可复现）

```powershell
# 复制 fh_b_1（world_172148 h002 两成员 baseline）的 s1–s3 到各 arm env；共享时间线
python run.py --mode simulate --world world_172148 --house house_0002 --date 2026-09-11 --env "fc_c_$i" --s4-only --workers 1
python run.py --mode simulate --world world_172148 --house house_0002 --date 2026-09-11 --env "fc_b_$i" --policy "tou:0.9,0.18" --cost-context --s4-only --workers 1
python src/analyze/compare_cpp.py --world world_172148 --house house_0002 --date 2026-09-11 --base-prefix fc_c --treat-prefix fc_b --n 9 --tag tou
```

## 2. 结果（n=9，全户聚合）

| 指标 | baseline | TOU+cost | Δ | t | p |
|---|---|---|---|---|---|
| **峰段 16–21** | 3.605 | 3.493 | **−3.1%** | **−5.57** | **0.0005** |
| 谷期 22–7 | 3.056 | 3.169 | +3.7% | +1.08 | 0.31（n.s.） |
| 总电量 | 12.683 | 12.406 | −2.2% | −2.16 | 0.063 |

## 3. 解读
1. **全户级峰显著下降（−3.1%，t=−5.57）** → 效应**非 M1 伪影**；
2. 幅度小于 M1-only（W2 M1 −5.0%）→ 户内**其他成员的刚性负荷**稀释了移峰（占比更低）；
3. **方向一致**（峰↓谷↑总↓），机制成立；
4. 限制：n=9 screen、单户（2 成员）。

## 4. 论文更新
- `paper/experiments/tou.md` / `README.md`：补"全户级 n=9：峰 −3.1%（p=0.0005）"。

## 5. token
- 约 **36 次调用**（2 成员 × 9 × 2 臂）。
