"""Freeze HR inputs for a private Crossover helper-platform implementation."""
from pathlib import Path
import hashlib
import json
import shutil
import sys

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / 'tools'))
from workspace_storage import locate
O = R / 'build/verification/crossover-helpers-jb'
C = O / 'source'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    parent = R / 'build/checkpoints/ryu-overlap-hr/manifest.json'
    p = json.loads(parent.read_text())
    assert {m: sha(R / f'build/smb-crossover-{m}.nes') for m in ('mmc3', 'mmc5')} == p['ROMs']
    audit = R / 'docs/qa/level-layout-audit-2026-10-22.md'
    assert sha(audit) == '1432919b6cebb61cbc190ebaf63f5ede4404bb5ac4678a1c31e6b5e82351b9ec'
    seed = json.loads(locate(R / 'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json').read_text())
    names = set(seed['source_hashes']) | {q.relative_to(R).as_posix() for q in (R / 'src').rglob('*') if q.is_file()}
    C.mkdir(parents=True)
    for name in names:
        dest = C / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(R / name, dest)
    for name in seed['generated11']:
        dest = C / 'build/generated' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(R / 'build/generated' / name, dest)
    result = dict(parent=str(parent.relative_to(R)), parent_sha256=sha(parent),
        ROMs=p['ROMs'], audit_sha256=sha(audit),
        full_list_presented_before_changes=True,
        source_before={n: sha(R / n) for n in sorted(names)},
        ownership={'physical_bank_18': 'AE6E..BBFF helper engine/data, after unchanged Contra audio',
                   'SRAM': '736A..73FF alignment gap before XgLzHistory; preserve every old address'},
        game_installed=False, goal_complete=False)
    (O / 'preparation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(C)


if __name__ == '__main__':
    main()
