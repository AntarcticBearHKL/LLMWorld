# -*- coding: utf-8 -*-
"""PersonaSampler - randomly samples virtual personas from the MatrAIx synthetic persona library.

Usage:
    from sampler import PersonaSampler
    ps = PersonaSampler()                     # auto-discovers MatrAIx_Persona_Synthetic/ data
    persona = ps.sample_persona()             # sample 1 random virtual persona (dict, 330 dimensions)
    people = ps.sample(3)                     # sample 3
    ps.sample_persona(seed=7)                 # fixed seed for reproducibility
    ps.sample(2, conditions={'Risk tolerance': 'Risk-seeking'})  # conditional sampling

Zero third-party dependencies (stdlib only). Sampling strategy: pick a random chunk ->
pick a random row -> retry with condition filtering, without loading all 400k rows.
"""
import csv
import glob
import json
import os
import random
import threading

# Parsed chunk cache: avoids re-reading the same CSV chunk during parallel sampling
# (10k rows per chunk)
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
        """Read and cache all rows of one chunk (thread-safe)."""
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
        """Sample n random virtual personas. conditions: {column name (English): value} -
        all must match to accept. Returns list[dict]."""
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
        """Sample 1 random virtual persona, return dict (330-dimension label -> value)."""
        rows = self.sample(1, seed=seed, conditions=conditions)
        return rows[0] if rows else None

    def to_persona(self, row):
        """Convert a raw record into a structured persona (Chinese keys) for injection
        into LLMWorld."""
        return {self.zh(k): v for k, v in row.items()}

    def sample_persona_text(self, seed=None, conditions=None, mode='core'):
        """Sample 1 random virtual persona and render it as a long Chinese description
        string (ready to place directly into an LLM prompt).
        mode: 'core' (notable traits only, ~700 chars) | 'full' (all dimensions)."""
        from persona_render import PersonaRenderer
        p = self.sample_persona(seed=seed, conditions=conditions)
        if not p:
            return None
        return PersonaRenderer(self.data_dir).render(p, mode=mode)


if __name__ == '__main__':
    ps = PersonaSampler()
    print('chunks:', ps.chunk_count(), '| dimensions:', len(ps.columns))
    p = ps.sample_persona(seed=42)
    print('--- sampled virtual persona (excerpt) ---')
    for k in ['Dominant trait', 'Risk tolerance', 'Decision style', 'Core value',
              'Sleep schedule', 'Work schedule', 'Commute mode', 'Household size',
              'Attitude: Renewable energy', 'Attitude: Electric vehicles',
              'Schwartz Security', 'Big Five Self-Discipline', 'Economic motivation']:
        if k in p:
            print('  %-32s = %s' % (k, p[k]))
    print('Chinese example:', ps.to_persona({k: p[k] for k in list(p)[:4]}))
