"""Admit actual-EJ Link WATCH checks and install its sole helper over EC."""
from pathlib import Path
import datetime
import gzip
import hashlib
import json
import shutil
import zipfile

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-link-watch-ej'
N = V / 'agent-lsr-victory-repair-ej-checks-a'
C = R / 'build/checkpoints/roster-audit-v49-link-watch-el'
P = R / 'build/checkpoints/roster-audit-v49-victory-ec/manifest.json'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not C.exists()
    pins = {
        P: '1618a568e0d14e8681efd0dbfc84d68bec1636bfb34703e3c5b9eddea73759d1',
        H / 'report.json': 'f4a24deaafce07dfad43c720196518156186109ba9e83bcd3d83e8243a5e0caf',
        N / 'freeze.json': '92e80a61805cecdb4981b3b12429a219df5d66a251ce5e997f8aadce3a85078a',
        V / 'agent-lsr-victory-repair-d/implementation-freeze.json': '101980b5961adf0d69b9f46dc74cd068b2a5619e681b36a96fd6c7edd845baed',
        V / 'agent49-du-bill-route-a/incident-freeze-f.json': '5248dd822c9871781bd51e3db0417271a0dcefb86065e3adf8f01c0a44747b3f',
    }
    for p, h in pins.items():
        assert sha(p) == h, p
    old = json.loads(P.read_text())
    before = old['source_hashes']
    assert len(before) == 441 and all(sha(R / n) == h for n, h in before.items())
    for row in old['builds']:
        assert all(sha(R / a['path']) == a['sha256'] for a in row['artifacts'].values())
    d = json.loads((H / 'report.json').read_text())
    assert d['status'] == 'PASS_PRIVATE_EJ_FOUR_BUILDS_SOLE_EASYLINK_HELPER_ON_EC_NATIVE_REBIND_PENDING'
    after = d['source_hashes']
    assert len(after) == 441 and set(after) == set(before)
    changed = {n: dict(before=before[n], after=h) for n, h in after.items() if before[n] != h}
    assert set(changed) == {'src/guest_victory_control.s'}
    assert not (R / 'src/bill_source_body.s').exists()
    assert all(sha(H / 'source' / n) == h for n, h in after.items())
    freeze = json.loads((N / 'freeze.json').read_text())
    for n, h in freeze['files'].items():
        assert sha(N / n) == h, n
    review = json.loads((N / 'review.json').read_text())
    assert sha(N / 'review.json') == freeze['review_sha256']
    assert review['native']['total_cases'] == 616 and review['native']['all_mappers']
    assert review['compiled']['actual_EC_vs_EJ_calls'] == 1000
    assert review['compiled']['all_nonstack_RAM_and_ordered_writes_including_SMC_exact']
    assert review['compiled']['ordinary_delta'] == review['compiled']['Mario_Luigi_delta'] == 0
    assert review['no_rejected_Bill_layer_in_EJ']
    for row in d['builds']:
        assert row['exit'] == 0
        stem = H / 'source/build' / ('smb-crossover-' + row['mapper'] + ('-baseline' if row['baseline'] else ''))
        assert all(sha(stem.with_suffix('.' + ext)) == h for ext, h in row['artifacts'].items())
        assert row.get('baseline_exact_CG_EC', row.get('only_ROM_delta_inside_rare_helper'))
    admission = dict(status='PASS_ROOT_EJ_REVIEW_616_NATIVE_1000_COMPILED_NO_REJECTED_BILL_LAYER',
        script_sha256=sha(__file__), EJ_report_sha256=sha(H / 'report.json'), native_freeze_sha256=sha(N / 'freeze.json'),
        verified_native_receipt_files=len(freeze['files']), source_files=441,
        native_cases=616, compiled_ABI_cases=1000, main_changed=False,
        source_limits=review['source_limits_retained'], accepted_release=False, goal_complete=False)
    ap = V / 'root49-ej-admission-el.json'
    assert not ap.exists()
    ap.write_text(json.dumps(admission, indent=2) + '\n')
    C.mkdir(parents=True)
    backup = C / 'before-changed-files.zip'
    with zipfile.ZipFile(backup, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n in changed:
            z.write(R / n, n)
    manifest = dict(status='INSTALLING_WORKING_LINK_WATCH_EL', utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        publisher_sha256=sha(__file__), before_source_hashes=before, source_changes=changed,
        backup=dict(path=backup.relative_to(R).as_posix(), sha256=sha(backup)),
        evidence=[dict(path=p.relative_to(R).as_posix(), sha256=sha(p), bytes=p.stat().st_size) for p in list(pins) + [ap]],
        builds=[], behavior='Retain EC castle-stall repair and previous Bill collision behavior. Easy Link now advances the existing source animation clock before automatic movement and animates after the full original background suffix.',
        validation='Both mapper/baseline builds; actual combined616 native source-phase/pose/pause/automatic/release/inventory cases;1000 strict compiled complete-controller cases. Only the rare helper changes; no PLAYER or RAM growth.',
        limits=review['source_limits_retained'], rejected_Bill_F_N_restored=False,
        outstanding='Private Bill source-last-rectangle consumer correction, all13 current-build full routes and upgrades, further lag work and retained final media review remain active.',
        accepted_release=False, goal_complete=False)
    def save():
        (C / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    save()
    for n in changed:
        shutil.copyfile(H / 'source' / n, R / n)
    for mapper in ('mmc3', 'mmc5'):
        row = next(x for x in d['builds'] if x['mapper'] == mapper and not x['baseline'])
        artifacts = {}
        stem = H / 'source/build' / ('smb-crossover-' + mapper)
        for ext in ('nes', 'lbl', 'map', 'dbg'):
            src = stem.with_suffix('.' + ext)
            dst = R / 'build' / src.name
            shutil.copyfile(src, dst)
            assert sha(dst) == row['artifacts'][ext]
            artifacts[ext] = dict(path=dst.relative_to(R).as_posix(), sha256=sha(dst), bytes=dst.stat().st_size)
            if ext == 'dbg':
                compressed = gzip.compress(dst.read_bytes(), mtime=0)
                (C / (dst.name + '.gz')).write_bytes(compressed)
                if dst.with_suffix('.dbg.gz').exists():
                    dst.with_suffix('.dbg.gz').write_bytes(compressed)
            else:
                shutil.copyfile(dst, C / dst.name)
        manifest['builds'].append(dict(mapper=mapper, artifacts=artifacts, byte_exact_native_tested_EJ=True))
        save()
    assert all(sha(R / n) == h for n, h in after.items())
    archive = C / 'source-v49-link-watch-el.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n in sorted(after):
            z.write(R / n, n)
    manifest.update(status='PASS_WORKING_LINK_WATCH_EL_BOTH_MAPPERS', source_hashes=after,
        source_archive=dict(path=archive.relative_to(R).as_posix(), sha256=sha(archive), bytes=archive.stat().st_size))
    save()
    print(manifest['status'], sha(C / 'manifest.json'), flush=True)


if __name__ == '__main__':
    main()
