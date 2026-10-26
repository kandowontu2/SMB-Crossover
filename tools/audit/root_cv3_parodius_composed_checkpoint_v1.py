"""Save the qualified private composition without promoting incomplete native coverage."""
from pathlib import Path
import difflib
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PACK = D / 'cv3-parodius-combined-f35-v1'
OUT = ROOT / 'docs/qa/checkpoints/2026-10-26/cv3-parodius-composed-held'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ready = PACK / 'freeze-v1/readiness-source-only.json'
    assert sha(ready) == '9609d87ad0545251fd19408baa6994ce09cd788f79f734ae336c1983e80d7749'
    qualified = json.loads(ready.read_text())
    bindings = qualified['all_frozen_bindings']
    assert len(bindings) == 3475
    for p, h in bindings.items():
        assert sha(p) == h, p
    assert qualified['passed'] and not qualified['adopted']
    assert sha(PACK / 'candidate.nes') == '4285d35db234ecdaf7c561f721c0aa8798545f9937e933acf5ab3e3f0b642682'
    assert not OUT.exists()
    OUT.mkdir(parents=True)
    catalog = {}

    def copy(p, name):
        p = Path(p)
        q = OUT / name
        q.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, q)
        assert sha(q) == sha(p)
        catalog[name] = dict(source=str(p), sha256=sha(q))

    partition = PACK / 'builds-v1/source-inventory-partitions.json'
    inventory = json.loads(partition.read_text())
    changes = []
    patch = ''
    for row in inventory['primary_source_tool_asset_paths']:
        name = row['path']
        p = PACK / 'source' / name
        assert sha(p) == row['sha256']
        old = ROOT / name
        before = old.read_bytes() if old.exists() else None
        after = p.read_bytes()
        if before == after:
            continue
        assert p.suffix in ['.s', '.cfg'], name
        copy(p, 'source/' + name)
        changes.append(dict(path=name, baseline_sha256=sha(old) if old.exists() else None,
                            candidate_sha256=sha(p)))
        patch += ''.join(difflib.unified_diff(
            before.decode().splitlines(True) if before is not None else [],
            after.decode().splitlines(True),
            fromfile='a/' + name if before is not None else '/dev/null', tofile='b/' + name))
    assert len(changes) == 18
    (OUT / 'implementation-from-current.patch').write_text(patch, newline='\n')
    catalog['implementation-from-current.patch'] = dict(sha256=sha(OUT / 'implementation-from-current.patch'))
    copy(ready, 'source-readiness.json')
    copy(partition, 'source-inventory-partitions.json')
    copy(PACK / 'layout-v2/all-deployable-files.json', 'source-inventory.json')
    copy(PACK / 'layout-v2/first-catalog-failure.json', 'retained-first-catalog-failure.json')
    for row in qualified['source_receipts']:
        p = Path(row['path'])
        assert sha(p) == row['sha256']
        copy(p, 'receipts/' + p.parent.name + '.json')
    for p, h in qualified['frozen_tools'].items():
        assert sha(p) == h
        if Path(p).name.startswith('cv3_parodius_'):
            copy(p, 'frozen-tools/' + Path(p).name)
    copy(qualified['report']['path'], 'report.txt')
    result = dict(
        source_CPU_qualified=True, production_adopted=False, goal_complete=False,
        candidate_ROM_sha256=qualified['candidate']['sha256'],
        installed_baseline_ROM_sha256='50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363',
        ROOT_verified_bindings=len(bindings), changed_source=changes, copied_bindings=catalog,
        limits='Source/CPU composition only: CV3 banks exactly 2cb5, every other bank/header/CHR exactly f35. '
               'One later actual4285 natural-area run reached the pipe and new loaded area, but failed the '
               'required pending-full-HUD/nonempty-Buffer2 overlap. All six terminal receipts are absent; '
               'the aggregate remains FALSE. No donor native result is relabeled4285. No adoption or full-roster verdict.')
    (OUT / 'root-review.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(copied=len(catalog), changes=len(changes), verified=len(bindings), adopted=False)))


if __name__ == '__main__':
    main()
