"""Checkpoint two immutable private audio studies, without installing either."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
CURRENT = '50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
read = lambda path: json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def checkpoint(name, study, receipts, copies, reports, extra_tools=()):
    out = ROOT / 'docs/qa/checkpoints/2026-10-25' / name
    assert not out.exists()
    tools, external = {}, {}
    for rel, expected in receipts.items():
        path = study / rel
        assert sha(path) == expected
        obj = read(path)
        assert obj['passed'] and not obj['accepted']
        external[path.as_posix()] = expected
        for rel_tool, value in obj.get('frozen_tools', {}).items():
            assert sha(ROOT / rel_tool) == value
            tools[rel_tool] = value
        for tool, value in obj.get('owned_tools', {}).items():
            rel_tool = 'tools/audit/' + tool
            assert sha(ROOT / rel_tool) == value
            tools[rel_tool] = value
        for rel_proof, value in obj.get('receipts', {}).items():
            assert sha(study / rel_proof) == value
            external[(study / rel_proof).as_posix()] = value
    for rel, expected in reports.items():
        assert sha(ROOT / rel) == expected
    for rel in extra_tools:
        tools[rel] = sha(ROOT / rel)
    out.mkdir(parents=True)
    for target, original in copies.items():
        path = study / original
        shutil.copyfile(path, out / target)
        external[path.as_posix()] = sha(path)
    write(out / 'manifest.json', dict(
        goal_complete=False, production_changes=False, adoption_qualified=False,
        installed_ROM_sha256=CURRENT, external_archive=study.as_posix(),
        files={p.name: sha(p) for p in out.iterdir() if p.is_file()},
        reports=reports, tools=tools, external_receipts=external,
        scope='Private study checkpoint only. See immutable source and later native reports '
              'in chronological order; source-ready is not native or release acceptance.'))
    return out.as_posix()


def main():
    assert sha(ROOT / 'build/smb-crossover-mmc5-expanded.nes') == CURRENT
    tmnt = D / 'tmnt-native-storage-current50b5-v1'
    review = D / 'root-tmnt-storage-review-v1/proof.json'
    assert read(review)['passed'] and read(review)['exact_fresh_build']
    first = checkpoint('tmnt-storage-8e2-source', tmnt,
        {'ready-v1/receipt.json': 'db0b2c00a82d4459ae8349dd84220a2421c74bd82b2b8263ace1c5aed903b47d'},
        {'receipt.json': 'ready-v1/receipt.json',
         'changed-source.json': 'ready-v1/changed-source.json',
         'implementation.patch': 'ready-v1/review.patch'},
        {'docs/qa/tmnt-native-storage-2026-10-25.txt':
         '90d4306594e5b6283f512d8f42b54ac1baefa09c4890556f927fa5820683de06'},
        ['tools/audit/review_tmnt_storage_packet_v1.py',
         'tools/audit/checkpoint_private_audio_studies_v1.py'])
    out = Path(first)
    shutil.copyfile(review, out / 'ROOT-source-review.json')
    manifest = read(out / 'manifest.json')
    manifest['files']['ROOT-source-review.json'] = sha(review)
    manifest['external_receipts'][review.as_posix()] = sha(review)
    write(out / 'manifest.json', manifest)

    cv3 = D / 'cv3-remaining-resident-v4'
    second = checkpoint('cv3-resident-0802-held', cv3,
        {'readiness-v1/readiness.json': '78099fd25537b52088ed2afa62724b5731f73181406e78f65dd2289d7e1b4d13',
         'native-final-held-v1/receipt.json': 'c360874c54b15e1fc1a746530e9351fc71a9337f7927ac878adcfbacb62e792a'},
        {'source-readiness.json': 'readiness-v1/readiness.json',
         'native-HELD.json': 'native-final-held-v1/receipt.json',
         'implementation.patch': 'qualified-v1/implementation.patch',
         'deadline-attribution.json': 'deadline-attribution-v1/proof.json'},
        {'docs/qa/cv3-remaining-sfx-resident-source-2026-10-25.txt':
         'f73730334e6f2bab8890de29bebc0f0acbefcd3a0df09a986557670e7dda063e',
         'docs/qa/cv3-remaining-sfx-resident-native-2026-10-25.txt':
         '2dd5c80c036b5af7078a294159b53e97009c23099b15cd9b0ef62b6912d7d0cc'},
        ['tools/audit/checkpoint_private_audio_studies_v1.py'])
    print(json.dumps(dict(checkpoints=[first, second], production_changes=False,
                          adoption_qualified=False, goal_complete=False)))


if __name__ == '__main__':
    main()
