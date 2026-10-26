"""One explicitly granted one-profile LuigiEasy flower/use component; no retry or settings changes."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p, z):
    p.write_text(json.dumps(z, indent=2) + '\n', encoding='utf-8')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--packet', type=Path, required=True)
    p.add_argument('--expected-readiness-sha256', required=True)
    p.add_argument('--native-grant', action='store_true', required=True)
    a = p.parse_args()
    ready = a.packet / 'readiness.json'
    assert sha(ready) == a.expected_readiness_sha256
    q = json.loads(ready.read_text())
    assert [c['name'] for c in q['profiles']] == ['luigi-easy'] and q['native_workers'] == 1
    assert q['profiles'][0]['character'] == 8 and q['profiles'][0]['variant'] == 1 and q['profiles'][0]['mode'] == 0
    assert not (a.packet / 'launch.json').exists(), 'No retry'
    for path, h in q['bindings'].items():
        assert sha(path) == h, ('Bound dependency drift', path)
    launch = dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  readiness_sha256=sha(ready), native_grant_explicit=True, retries=0)
    with (a.packet / 'launch.json').open('x', encoding='utf-8') as f:
        json.dump(launch, f, indent=2)
    results = []
    for c in q['profiles']:
        for path, h in q['bindings'].items():
            assert sha(path) == h, ('Bound dependency drift', path)
        fixture = Path(c['fixture'])
        assert not (fixture / 'result.json').exists(), 'No retry'
        with (fixture / 'native-host.log').open('x', encoding='utf-8') as log:
            z = subprocess.run(c['command'], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        result = json.loads((fixture / 'result.json').read_text()) if (fixture / 'result.json').exists() else {}
        item = json.loads((fixture / 'flower-component.json').read_text()) if (fixture / 'flower-component.json').exists() else {}
        chr_result = json.loads((fixture / 'chr-commit.json').read_text()) if (fixture / 'chr-commit.json').exists() else {}
        for n in ['worker_settings', 'user_settings']:
            assert sha(q['environment'][n]) == q['environment'][n + '_sha256'], 'Settings drift'
        passed = z.returncode == 0 and result.get('component_complete') is True and result.get('deaths') == 0
        passed = passed and item.get('passed') is True and item.get('actual_mode') == 0 and chr_result.get('passed') is True
        row = dict(name=c['name'], passed=bool(passed), exit=z.returncode, result=result,
                   component=item, CHR=chr_result, retries=0,
                   scope='One current-ROM real mushroom/laterflower and fireball target contact, not fullroute/item roster')
        put(fixture / 'native-receipt.json', row)
        results.append(row)
        put(a.packet / 'native-progress.json', dict(results=results))
        print(json.dumps(dict(name=c['name'], passed=bool(passed), exit=z.returncode)), flush=True)
        # A failing new controller/observer requires review, not automatic
        # enumeration under a potentially invalid shared fixture.
        if not passed:
            break
    proof = dict(passed=len(results) == 1 and all(r['passed'] for r in results),
                 ROM_sha256=q['ROM_sha256'], profiles_run=len(results), profiles=results,
                 native_worker_released=True, every_item_or_route_claim=False)
    put(a.packet / 'native-proof.json', proof)
    return 0 if proof['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
