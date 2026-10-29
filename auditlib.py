"""Small, dependency-free input and report helpers for a synthetic portfolio demo."""
import csv
import hashlib
import json
import math
from pathlib import Path


def read_csv(path, required):
    with open(path, newline='', encoding='utf-8-sig') as stream:
        reader = csv.DictReader(stream, strict=True)
        fields = reader.fieldnames or []
        if len(fields) != len(set(fields)):
            raise ValueError('duplicate CSV headers')
        missing = set(required) - set(fields)
        if missing:
            raise ValueError('missing columns: ' + ', '.join(sorted(missing)))
        rows = []
        for line, row in enumerate(reader, 2):
            if None in row or any(v is None for v in row.values()):
                raise ValueError(f'CSV row {line}: wrong number of fields')
            clean = {k: v.strip() for k, v in row.items()}
            if any(not clean[k] for k in required):
                raise ValueError(f'CSV row {line}: required field is blank')
            rows.append(clean)
        if not rows:
            raise ValueError('CSV must contain at least one data row')
        return rows


def number(value, name, minimum=None, positive=False):
    if isinstance(value, bool):
        raise ValueError(f'{name}: boolean is not a number')
    try:
        x = float(value)
    except (TypeError, ValueError):
        raise ValueError(f'{name}: expected a number') from None
    if not math.isfinite(x):
        raise ValueError(f'{name}: must be finite')
    if positive and x <= 0:
        raise ValueError(f'{name}: must be greater than zero')
    if minimum is not None and x < minimum:
        raise ValueError(f'{name}: must be at least {minimum}')
    return x


def unique(rows, fields):
    seen = set()
    for row in rows:
        key = tuple(row[k] for k in fields)
        if key in seen:
            raise ValueError('duplicate key: ' + ', '.join(map(str, key)))
        seen.add(key)


def load_config(path, required):
    with open(path, encoding='utf-8') as stream:
        value = json.load(stream)
    if not isinstance(value, dict) or set(value) != set(required):
        raise ValueError('configuration must have exactly: ' + ', '.join(required))
    return value


def evidence(paths):
    return [{'file': Path(p).name, 'sha256': hashlib.sha256(Path(p).read_bytes()).hexdigest()}
            for p in paths]


def cell(value):
    return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '&#124;').replace('\n', ' ')


def write_reports(folder, report, markdown):
    # Serialize before touching output files so non-finite derived values fail cleanly.
    encoded = json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
    path = Path(folder)
    path.mkdir(parents=True, exist_ok=True)
    (path / 'report.json').write_text(encoded, encoding='utf-8')
    (path / 'report.md').write_text(markdown, encoding='utf-8')
