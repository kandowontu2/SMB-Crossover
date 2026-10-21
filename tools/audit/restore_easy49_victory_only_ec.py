"""Revert Bill's confirmed pipe regression while retaining tested rare victory C."""
from pathlib import Path
import datetime
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
F = V / 'agent-lsr-victory-repair-c'
H = V / 'root49-victory-only-ec'
C = R / 'build/checkpoints/roster-audit-v49-victory-ec'
P = R / 'build/checkpoints/roster-audit-v49-body-victory-du/manifest.json'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not H.exists() and not C.exists()
    assert sha(P) == 'd518efb726559ac120ec4517a73e045e674ec9219a0317884efb8be2ddeeb477'
    old = json.loads(P.read_text())
    assert all(sha(R / n) == h for n, h in old['source_hashes'].items())
    for row in old['builds']:
        assert all(sha(R / a['path']) == a['sha256'] for a in row['artifacts'].values())
    fp = F / 'implementation-freeze.json'
    assert sha(fp) == '3a1d954e4f279fe850c3f5686d9ae03a90cc1d585438164070d2ca4cb68a4462'
    frozen = json.loads(fp.read_text())
    source_hashes = frozen['source_catalog']
    assert len(source_hashes) == 441
    assert all(sha(F / 'source' / n) == h for n, h in source_hashes.items())
    C.mkdir(parents=True)
    H.mkdir()
    source = H / 'source'
    for n in source_hashes:
        target = source / n
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(F / 'source' / n, target)
    br = json.loads((F / 'build-report.json').read_text())
    for n, h in br['generated_input_hashes'].items():
        p = F / 'source/build/generated' / n
        assert sha(p) == h
        target = source / 'build/generated' / n
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, target)
    driver_parent = V / 'root49-bill-body-union-dg/build-driver.py'
    driver_text = driver_parent.read_text()
    original = V / 'root49-bill-body-union-dg/source'
    needle = 'ROOT = Path(' + repr(str(original)) + ')'
    assert driver_text.count(needle) == 1
    driver = H / 'build-driver.py'
    driver.write_text(driver_text.replace(needle, 'ROOT = Path(' + repr(str(source)) + ')'))
    report = dict(status='BUILDING_C_ONLY_REGRESSION_REVERT', script_sha256=sha(__file__),
                  parent_DU_manifest_sha256=sha(P), exact_C_freeze_sha256=sha(fp),
                  source_hashes=source_hashes, builds=[], main_changed=False)
    def save_report():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save_report()
    baseline = dict(mmc3='0511c6844d0e9fa61f4b4fbc34e6f9c67d8247d3ca964ebbb0c9c2718cdc5146',
                    mmc5='34858561f4825dcc96cdd5fd46872f9230890c93af95351720c8536155f5cbbd')
    for base in (False, True):
        for mapper in ('mmc3', 'mmc5'):
            tag = mapper + ('-baseline' if base else '')
            log = H / (tag + '-build.log')
            with log.open('wb') as stream:
                rc = subprocess.run([sys.executable, str(driver), '--mapper', mapper] + (['--baseline'] if base else []),
                                    cwd=R, stdout=stream, stderr=subprocess.STDOUT).returncode
            row = dict(mapper=mapper, baseline=base, exit=rc, log_sha256=sha(log))
            report['builds'].append(row)
            save_report()
            assert rc == 0, log
            stem = source / 'build' / ('smb-crossover-' + tag)
            row['artifacts'] = {ext: sha(stem.with_suffix('.' + ext)) for ext in ('nes', 'lbl', 'map', 'dbg')}
            expected = baseline[mapper] if base else next(x for x in br['builds'] if x['mapper'] == mapper and not x['baseline'])['artifacts']['nes']['sha256']
            assert row['artifacts']['nes'] == expected
            row['exact_frozen_C_or_CG_baseline'] = True
            save_report()
    assert all(sha(source / n) == h for n, h in source_hashes.items())
    report['status'] = 'PASS_C_ONLY_FOUR_BUILDS_EXACT_FROZEN_C_BOTH_BASELINES_CG'
    save_report()
    before = old['source_hashes']
    changes = {n: dict(before=before.get(n), after=source_hashes.get(n))
               for n in set(before) | set(source_hashes) if before.get(n) != source_hashes.get(n)}
    assert len(changes) == 9
    removed = set(before) - set(source_hashes)
    assert removed == {'src/bill_source_body.s'}
    backup = C / 'before-changed-files.zip'
    with zipfile.ZipFile(backup, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n in sorted(changes):
            assert sha(R / n) == before[n]
            z.write(R / n, n)
    with zipfile.ZipFile(backup) as z:
        for n in changes:
            assert hashlib.sha256(z.read(n)).hexdigest() == before[n]
    refs = [P, fp, H / 'report.json', V / 'root49-victory-review-do.json',
            F / 'persistent-controls/freeze.json', F / 'budget-qualification.json']
    manifest = dict(status='INSTALLING_WORKING_VICTORY_EC_REVERT_CONFIRMED_BILL_HEAD_AXIS_REGRESSION',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), publisher_sha256=sha(__file__),
        source_changes=changes, before_source_hashes=before, builds=[],
        backup=dict(path=backup.relative_to(R).as_posix(), sha256=sha(backup)),
        evidence=[dict(path=p.relative_to(R).as_posix(), sha256=sha(p), bytes=p.stat().st_size) for p in refs],
        reason='Ordinary fresh Bill Right+A beside pipe: new full-width head query chooses pipe side cell despite source prior-right<=tile-left; native head-first NYSpd cancels jump. F/N body and cell fixtures did not establish source consumer/axis resolution. Revert all Bill F/N runtime hunks; retain frozen rare-victory C.',
        behavior='Exact frozen C441 source and both native-tested C ROMs. Original BY Bill movement/head behavior restored; rare guest castle walk repair retained. EasyLink separate WATCH animation and complete projectile/form parity remain pending.',
        qualification='DU/DQ/F/N and every negative/source/capture artifact remain retained. This is a working regression revert, not all13 route/arsenal/final-recording acceptance.',
        accepted_release=False, goal_complete=False)
    def save():
        (C / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    save()
    for n in sorted(changes):
        target = R / n
        if n in removed:
            # Only our exact, just-backed-up added source file is removed.
            assert target.resolve().parent == (R / 'src').resolve() and sha(target) == before[n]
            target.unlink()
        else:
            shutil.copyfile(source / n, target)
    for mapper in ('mmc3', 'mmc5'):
        row = next(x for x in report['builds'] if x['mapper'] == mapper and not x['baseline'])
        stem = source / 'build' / ('smb-crossover-' + mapper)
        artifacts = {}
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
        manifest['builds'].append(dict(mapper=mapper, artifacts=artifacts, byte_exact_native_tested_C=True))
        save()
    assert all(sha(R / n) == h for n, h in source_hashes.items())
    archive = C / 'source-v49-victory-ec.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n in sorted(source_hashes):
            z.write(R / n, n)
    manifest.update(status='PASS_WORKING_VICTORY_EC_BILL_REGRESSION_REVERTED_BOTH_MAPPERS',
        source_hashes=source_hashes, source_archive=dict(path=archive.relative_to(R).as_posix(), sha256=sha(archive), bytes=archive.stat().st_size))
    save()
    print(manifest['status'], sha(C / 'manifest.json'), flush=True)


if __name__ == '__main__':
    main()
