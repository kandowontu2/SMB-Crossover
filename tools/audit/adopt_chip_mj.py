"""Install the Chip/Dale packet only after every MG baseline hash matches."""
from pathlib import Path
import hashlib
import json
import shutil

R = Path(__file__).resolve().parents[2]
D = R / 'build/verification/chip-dale-candidate-agent'
O = R / 'build/verification/chip-adoption-mj'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not O.exists(), 'Preserve the prior adoption evidence'
    manifest = json.loads((D / 'incremental-merge-manifest.json').read_text())
    changes = manifest['changes']
    for item in changes:
        target = R / item['path']
        actual = sha(target) if target.exists() else None
        assert actual == item['before_SHA256'], item['path']
        assert sha(D / 'merge-staging' / item['path']) == item['after_SHA256'], item['path']
    O.mkdir(parents=True)
    for item in changes:
        target = R / item['path']
        if target.exists():
            backup = O / 'before' / item['path']
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(target, backup)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(D / 'merge-staging' / item['path'], target)
    receipt = dict(baseline='kirby-roster-mg',
                   packet_sha256=sha(D / 'incremental-merge-manifest.json'),
                   expected_ROM_sha256=manifest['candidate_ROM_SHA256'],
                   changes=changes, all_before_and_after_hashes_verified=True,
                   qualification='All shared files exactly matched MG before replacement; no newer edits overwritten.')
    (O / 'adoption.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(adopted_files=len(changes), evidence=str(O))))


if __name__ == '__main__':
    main()
