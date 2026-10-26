"""Independently preserve the uninstalled native-music multiply optimization."""
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
    ready = S / 'multiply-ready-v1'
    assert sha(ready / 'receipt.json') == 'b94d37e9a96588511791782a40872a051ecdbeac65c84ec09993c4082df9bfb2'
    receipt = json.loads((ready / 'receipt.json').read_text())
    assert receipt['frozen'] and receipt['source_CPU_qualified_only']
    assert not receipt['accepted'] and not receipt['native_run']
    assert sha(ROOT / 'build/smb-crossover-mmc5-expanded.nes') == receipt['accepted_production_parent_sha256']
    assert sha(ready / 'candidate.nes') == receipt['candidate_ROM_sha256']
    donor = S / 'ready-dispatch-v1'
    assert sha(donor / 'candidate.nes') == receipt['donor_a983_sha256']
    before = (donor / 'candidate.nes').read_bytes()
    after = (ready / 'candidate.nes').read_bytes()
    assert len(before) == len(after)
    changed = {i for i, (a, b) in enumerate(zip(before, after)) if a != b}
    base = 16 + 63 * 8192
    allowed = set(range(base + 0x125, base + 0x173)) | set(range(base + 0xcbd, base + 0xcc1))
    assert before[base + 0x125:base + 0x200] == bytes([255]) * 219
    assert len(changed) == 79 and changed <= allowed
    assert {(i - 16) // 8192 for i in changed} == {63}
    frozen = json.loads((S / 'current-baseline-v1/frozen-source.json').read_text())['source_files']
    assert all(sha(ROOT / name) == value for name, value in frozen.items())
    assert sha(ready / 'source.zip') == receipt['source_zip_sha256']
    assert sha(ready / 'report.txt') == receipt['report_sha256']
    assert sha(ready / 'review-versus-a983.patch') == receipt['review_patch_sha256']
    expected_changes = {'src/tmnt-native.inc', 'src/tmnt_audio.s', 'src/tmnt_audio_multiply.s'}
    with zipfile.ZipFile(ready / 'source.zip') as z, zipfile.ZipFile(donor / 'source.zip') as previous:
        assert len(z.namelist()) == len(set(z.namelist())) == 657
        assert set(z.namelist()) - set(previous.namelist()) == {'src/tmnt_audio_multiply.s'}
        assert not set(previous.namelist()) - set(z.namelist())
        actual = {n for n in z.namelist() if n not in previous.namelist() or z.read(n) != previous.read(n)}
        assert actual == expected_changes
        for name in z.namelist():
            assert z.read(name) == (ready / 'source' / name).read_bytes()
        for name, row in receipt['changed_source_versus_donor'].items():
            assert hashlib.sha256(z.read(name)).hexdigest() == row['after_sha256']
    for row in receipt['proofs'].values():
        assert sha(Path(row['path'])) == row['sha256']
        proof = json.loads(Path(row['path']).read_text())
        assert proof.get('passed'), row['path']
    tools = {'tools/audit/' + name: value for name, value in receipt['tools'].items()}
    assert all(sha(ROOT / name) == value for name, value in tools.items())
    tools[Path(__file__).relative_to(ROOT).as_posix()] = sha(Path(__file__))
    out = ROOT / 'docs/qa/checkpoints/2026-10-25/tmnt-multiply-2f61-source'
    out.mkdir(parents=True, exist_ok=False)
    for name in ['receipt.json', 'report.txt', 'review-versus-a983.patch',
                 'changed-source-versus-a983.json', 'changed-source-versus-50b5.json']:
        shutil.copyfile(ready / name, out / name)
    for name in expected_changes:
        target = out / 'changed-source' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ready / 'source' / name, target)
    manifest = dict(goal_complete=False, production_changes=False, adopted=False,
                    candidate_ROM_sha256=receipt['candidate_ROM_sha256'],
                    installed_ROM_sha256=receipt['accepted_production_parent_sha256'],
                    independently_verified_ROM_delta_bytes=79, changed_bank=63,
                    independently_verified_source_archive_files=657,
                    frozen_ROOT_production_inputs_unchanged=len(frozen),
                    external_packet=ready.as_posix(), tools=tools,
                    files={p.relative_to(out).as_posix(): sha(p) for p in out.rglob('*') if p.is_file()},
                    limits='Source/CPU qualification only. The earlier eight native draw losses '
                           'remain open. This candidate has no native cadence or release approval.')
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(dict(checkpoint=out.as_posix(), verified=True, production_changes=False)))


if __name__ == '__main__':
    main()
