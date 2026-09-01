import csv
import glob
import json
import os
import random


class PersonaReader:
    def __init__(self, data_dir=None):
        self.data_dir = data_dir or os.path.dirname(os.path.abspath(__file__))
        self._chunks = sorted(glob.glob(os.path.join(self.data_dir, 'synthetic_*.csv')))
        if not self._chunks:
            raise FileNotFoundError('no synthetic_*.csv found in %s' % self.data_dir)
        self._map = self._load_dimension_map()
        with open(self._chunks[0], encoding='utf-8-sig') as f:
            self.columns = next(csv.reader(f))
        self._col_index = {c: i for i, c in enumerate(self.columns)}

    def _load_dimension_map(self):
        p = os.path.join(self.data_dir, 'dimension_map.json')
        if not os.path.exists(p):
            return {}
        with open(p, encoding='utf-8') as f:
            entries = json.load(f)
        return {e['label']: e['zh'] for e in entries}

    def zh(self, label):
        return self._map.get(label, label)

    def zh_columns(self):
        return [self.zh(c) for c in self.columns]

    def chunk_count(self):
        return len(self._chunks)

    def chunk_paths(self):
        return list(self._chunks)

    def load_chunk(self, n):
        if not 1 <= n <= len(self._chunks):
            raise IndexError('chunk index out of range 1..%d' % len(self._chunks))
        with open(self._chunks[n - 1], encoding='utf-8-sig') as f:
            return list(csv.DictReader(f))

    def load_all(self):
        rows = []
        for i in range(1, len(self._chunks) + 1):
            rows.extend(self.load_chunk(i))
        return rows

    def filter(self, conditions, chunks=None):
        out = []
        for n in (chunks or range(1, len(self._chunks) + 1)):
            for row in self.load_chunk(n):
                if all(row.get(k) == v for k, v in conditions.items()):
                    out.append(row)
        return out

    def sample(self, n, seed=None, conditions=None):
        pool = self.filter(conditions) if conditions else self.load_all()
        rng = random.Random(seed)
        if n >= len(pool):
            return pool
        return rng.sample(pool, n)

    def iter_chunks(self):
        for i in range(1, len(self._chunks) + 1):
            yield self.load_chunk(i)

    def to_csv(self, rows, path, columns=None):
        cols = columns or (list(rows[0].keys()) if rows else self.columns)
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)


if __name__ == '__main__':
    r = PersonaReader()
    print('chunks:', r.chunk_count(), '| columns:', len(r.columns))
    rows = r.load_chunk(1)
    print('chunk1 rows:', len(rows))
    print('sample persona:', {k: rows[0][k] for k in ['Age bracket', 'Region', 'Dominant trait', 'Risk tolerance', 'Sleep schedule'] if k in rows[0]})
    print('zh sample:', {c: r.zh(c) for c in ['Age bracket', 'Sleep schedule', 'Dominant trait']})
