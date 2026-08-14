# -*- coding: utf-8 -*-
"""PersonaSampler - 从 MatrAIx 合成人格库随机抽样虚拟人格。

用法:
    from sampler import PersonaSampler
    ps = PersonaSampler()                     # 自动发现 MatrAIx_Persona_Synthetic/ 数据
    persona = ps.sample_persona()             # 随机抽 1 个虚拟人格 (dict, 330 维)
    people = ps.sample(3)                     # 随机抽 3 个
    ps.sample_persona(seed=7)                 # 固定种子可复现
    ps.sample(2, conditions={'Risk tolerance': 'Risk-seeking'})  # 带条件抽样

零第三方依赖 (stdlib only)。抽样策略: 随机选分片 -> 随机取行 -> 条件过滤重试,
无需加载全量 40 万条。
"""
import csv
import glob
import json
import os
import random
import threading

# 已解析 chunk 缓存：并行抽样时避免重复读取同一 CSV 分片（每分片 1 万行）
_chunk_cache = {}
_chunk_cache_lock = threading.Lock()
_CHUNK_CACHE_MAX = 10


class PersonaSampler:
    def __init__(self, data_dir=None, seed=None):
        self.data_dir = data_dir or os.path.dirname(os.path.abspath(__file__))
        self._chunks = sorted(glob.glob(os.path.join(self.data_dir, 'synthetic_*.csv')))
        if not self._chunks:
            raise FileNotFoundError('no synthetic_*.csv found in %s' % self.data_dir)
        self._rng = random.Random(seed)
        with open(self._chunks[0], encoding='utf-8-sig') as f:
            self.columns = next(csv.reader(f))
        self._map = self._load_dimension_map()

    def _load_chunk_rows(self, path):
        """读取并缓存一个分片的全部行（线程安全）。"""
        with _chunk_cache_lock:
            rows = _chunk_cache.get(path)
        if rows is None:
            with open(path, encoding='utf-8-sig') as f:
                rows = list(csv.DictReader(f))
            with _chunk_cache_lock:
                if len(_chunk_cache) >= _CHUNK_CACHE_MAX:
                    _chunk_cache.pop(next(iter(_chunk_cache)))
                _chunk_cache[path] = rows
        return rows

    def _load_dimension_map(self):
        p = os.path.join(self.data_dir, 'dimension_map.json')
        if not os.path.exists(p):
            return {}
        with open(p, encoding='utf-8') as f:
            return {e['label']: e['zh'] for e in json.load(f)}

    def zh(self, label):
        return self._map.get(label, label)

    def zh_columns(self):
        return [self.zh(c) for c in self.columns]

    def chunk_count(self):
        return len(self._chunks)

    def _random_row(self):
        path = self._chunks[self._rng.randrange(len(self._chunks))]
        rows = self._load_chunk_rows(path)
        return rows[self._rng.randrange(len(rows))]

    def sample(self, n=1, seed=None, conditions=None, max_attempts=2000):
        """随机抽 n 个虚拟人格。conditions: {列名(英文): 值} 全部匹配才收下。
        返回 list[dict]。"""
        rng = random.Random(seed) if seed is not None else self._rng
        out = []
        attempts = 0
        while len(out) < n:
            attempts += 1
            if attempts > max_attempts:
                break
            path = self._chunks[rng.randrange(len(self._chunks))]
            rows = self._load_chunk_rows(path)
            row = rows[rng.randrange(len(rows))]
            if conditions and not all(row.get(k) == v for k, v in conditions.items()):
                continue
            out.append(row)
        return out

    def sample_persona(self, seed=None, conditions=None):
        """随机抽 1 个虚拟人格，返回 dict（330 维 label -> value）。"""
        rows = self.sample(1, seed=seed, conditions=conditions)
        return rows[0] if rows else None

    def to_persona(self, row):
        """把一条原始记录转成便于注入 LLMWorld 的结构化人格（中文键）。"""
        return {self.zh(k): v for k, v in row.items()}

    def sample_persona_text(self, seed=None, conditions=None, mode='core'):
        """随机抽 1 个虚拟人格并渲染成中文描述长字符串（可直接放入 LLM prompt）。
        mode: 'core'（仅显著特征，~700 字）| 'full'（全量维度）。"""
        from persona_render import PersonaRenderer
        p = self.sample_persona(seed=seed, conditions=conditions)
        if not p:
            return None
        return PersonaRenderer(self.data_dir).render(p, mode=mode)


if __name__ == '__main__':
    ps = PersonaSampler()
    print('chunks:', ps.chunk_count(), '| 维度数:', len(ps.columns))
    p = ps.sample_persona(seed=42)
    print('--- 抽样虚拟人格（节选）---')
    for k in ['Dominant trait', 'Risk tolerance', 'Decision style', 'Core value',
              'Sleep schedule', 'Work schedule', 'Commute mode', 'Household size',
              'Attitude: Renewable energy', 'Attitude: Electric vehicles',
              'Schwartz Security', 'Big Five Self-Discipline', 'Economic motivation']:
        if k in p:
            print('  %-32s = %s' % (k, p[k]))
    print('中文示例:', ps.to_persona({k: p[k] for k in list(p)[:4]}))
