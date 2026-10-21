"""Qualify the additive immutable-label lookup cache; no emulated execution."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'build/verification/ryu49k-vine-abi-component-a'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

original = HERE / 'verify_cpu.py'
cached = HERE / 'verify_cpu_label_cache_b.py'
a = original.read_text(encoding='utf-8')
b = cached.read_text(encoding='utf-8')
assert b.count('from functools import cache\n') == 1
assert b.count('@cache\n') == 1
assert b.replace('from functools import cache\n', '', 1).replace('@cache\n', '', 1) == a
reports = [HERE / x / 'report.json' for x in ['root-smoke-a', 'root-cache-smoke-b']]
values = [json.loads(p.read_text(encoding='utf-8')) for p in reports]
assert values[0]['script_sha256'] == sha(original)
assert values[1]['script_sha256'] == sha(cached)
for v in values:
    del v['script_sha256']
assert values[0] == values[1]
assert all(x['passed'] == 56 for x in values[0]['cases'].values())
result = {
    'status': 'PASS_EXACT_ADDITIVE_LOOKUP_CACHE_AND_112_SMOKE_REPORTS',
    'original_sha256': sha(original),
    'cached_sha256': sha(cached),
    'only_source_change': 'functools.cache on immutable labels(Image) metadata lookup',
    'case_generation_model_assertions_unchanged': True,
    'smoke_reports': [{'path': str(p), 'sha256': sha(p)} for p in reports],
    'all_report_fields_except_script_sha256_literal_equal': True,
    'scope': 'Smoke overlaps the full case set; no extra unique cases or native proof.',
}
(HERE / 'label-cache-smoke-receipt-b.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result))
