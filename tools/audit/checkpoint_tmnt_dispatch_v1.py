"""Preserve the frozen TMNT dispatch study; no installation or native approval."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
S = D / 'tmnt-native-storage-current50b5-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ready = S / 'ready-dispatch-v1'
    assert sha(ready / 'receipt.json') == '97a8dd5abe01d8d9217800ed8c1be22ebf050a3dbce04a8ae800d670b754b3a6'
    receipt = json.loads((ready / 'receipt.json').read_text())
    assert receipt['passed'] and not receipt['accepted'] and not receipt['native_run']
    assert sha(ROOT / 'build/smb-crossover-mmc5-expanded.nes') == receipt['parent_ROM_sha256']
    assert sha(ready / 'candidate.nes') == receipt['candidate_ROM_sha256']
    old = (S / 'ready-v1/candidate.nes').read_bytes()
    new = (ready / 'candidate.nes').read_bytes()
    expected = {16 + int(bank)*8192 + offset
                for bank, offsets in receipt['changed_offsets_vs_8e2'].items() for offset in offsets}
    assert len(expected) == 64 and len(old) == len(new)
    assert {i for i, (a, b) in enumerate(zip(old, new)) if a != b} == expected
    frozen = json.loads((S / 'current-baseline-v1/frozen-source.json').read_text())['source_files']
    assert all(sha(ROOT / name) == value for name, value in frozen.items())
    assert sha(ready / 'source.zip') == receipt['source_zip_sha256']
    assert sha(ready / 'report.txt') == receipt['report_sha256']
    assert sha(ready / 'review.patch') == receipt['review_patch_sha256']
    assert sha(ready / 'costs-versus-current50b5.json') == receipt['cost_detail_sha256']
    with zipfile.ZipFile(ready / 'source.zip') as z, zipfile.ZipFile(S / 'ready-v1/source.zip') as before:
        assert len(z.namelist()) == len(set(z.namelist())) == 656
        assert set(z.namelist()) == set(before.namelist())
        changed = [name for name in z.namelist() if z.read(name) != before.read(name)]
        assert changed == ['src/tmnt_audio_resident.s']
        for name in z.namelist():
            expected_hash = receipt['changed_source_files'].get(name, {}).get('after_sha256', frozen.get(name))
            assert hashlib.sha256(z.read(name)).hexdigest() == expected_hash
    for row in receipt['proofs'].values():
        assert sha(Path(row['path'])) == row['sha256']
        assert json.loads(Path(row['path']).read_text())['passed']
    tools = {'tools/audit/' + name: value for name, value in receipt['owned_tools'].items()}
    assert all(sha(ROOT / name) == value for name, value in tools.items())
    tools[Path(__file__).relative_to(ROOT).as_posix()] = sha(Path(__file__))
    out = ROOT / 'docs/qa/checkpoints/2026-10-25/tmnt-dispatch-a983-source'
    out.mkdir(parents=True, exist_ok=False)
    for name, original in {'receipt.json': 'receipt.json', 'changed-source.json': 'changed-source.json',
                           'implementation.patch': 'review.patch', 'source-report.txt': 'report.txt',
                           'costs-versus-50b5.json': 'costs-versus-current50b5.json'}.items():
        shutil.copyfile(ready / original, out / name)
    result = dict(goal_complete=False, production_changes=False, adoption_qualified=False,
                  installed_ROM_sha256=receipt['parent_ROM_sha256'],
                  candidate_ROM_sha256=receipt['candidate_ROM_sha256'],
                  external_packet=ready.as_posix(), source_archive_files=656,
                  independent_delta_bytes_vs_8e2=64, independent_changed_source_vs_8e2=changed,
                  frozen_ROOT_inputs_unchanged=650,
                  files={p.name: sha(p) for p in out.iterdir()}, tools=tools,
                  external_proofs=receipt['proofs'],
                  scope='Immutable source/CPU readiness checkpoint. Subsequent native results '
                        'have their own receipts; this source packet grants no cadence or release approval.')
    (out / 'manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(checkpoint=out.as_posix(), source_review_passed=True,
                          production_changes=False, adoption_qualified=False)))


if __name__ == '__main__':
    main()
