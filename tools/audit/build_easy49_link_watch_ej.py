"""Privately merge only frozen EasyLink WATCH helper D onto stable EC, without Bill F/N."""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-link-watch-ej'
D = V / 'agent-lsr-victory-repair-d'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ep = V / 'root49-victory-only-ec/report.json'
    ec = json.loads(ep.read_text())
    assert ec['status'] == 'PASS_C_ONLY_FOUR_BUILDS_EXACT_FROZEN_C_BOTH_BASELINES_CG'
    mp = R / 'build/checkpoints/roster-audit-v49-victory-ec/manifest.json'
    assert sha(mp) == '1618a568e0d14e8681efd0dbfc84d68bec1636bfb34703e3c5b9eddea73759d1'
    main_state = json.loads(mp.read_text())
    assert ec['source_hashes'] == main_state['source_hashes']
    assert all(sha(R / n) == h for n, h in ec['source_hashes'].items())
    fp = D / 'implementation-freeze.json'
    assert sha(fp) == '101980b5961adf0d69b9f46dc74cd068b2a5619e681b36a96fd6c7edd845baed'
    f = json.loads(fp.read_text())
    for n, h in f['files'].items():
        assert sha(D / n) == h, n
    assert sha(D / 'review.json') == f['review_sha256']
    review = json.loads((D / 'review.json').read_text())
    for n, h in review['source_contract']['primary_anchors'].items():
        assert sha(R / n) == h, n
    assert set(f['after_files']) == {'src/guest_victory_control.s'}
    target_name = 'src/guest_victory_control.s'
    assert ec['source_hashes'][target_name] == f['parent_source_files'][target_name]
    H.mkdir(exist_ok=False)
    source = H / 'source'
    hashes = dict(ec['source_hashes'])
    for n, h in hashes.items():
        old = ep.parent / 'source' / n
        assert sha(old) == h
        target = source / n
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(old, target)
    after = D / 'after' / target_name
    assert sha(after) == f['after_files'][target_name] == '12454f9e7c249ae27fc2caf9fae9225f9bc565db2dce4adac8515f9f3fcf39f1'
    shutil.copyfile(after, source / target_name)
    hashes[target_name] = sha(after)
    frozen_c = json.loads((V / 'agent-lsr-victory-repair-c/build-report.json').read_text())
    for n, h in frozen_c['generated_input_hashes'].items():
        old = ep.parent / 'source/build/generated' / n
        assert sha(old) == h
        target = source / 'build/generated' / n
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(old, target)
    driver = H / 'build-driver.py'
    text = (ep.parent / 'build-driver.py').read_text()
    needle = 'ROOT = Path(' + repr(str(ep.parent / 'source')) + ')'
    assert text.count(needle) == 1
    driver.write_text(text.replace(needle, 'ROOT = Path(' + repr(str(source)) + ')'))
    result = dict(status='BUILDING_EJ_EC_PLUS_SOLE_D_HELPER', script_sha256=sha(__file__),
        EC_manifest_sha256=sha(mp), EC_report_sha256=sha(ep), D_freeze_sha256=sha(fp),
        D_review_sha256=sha(D / 'review.json'), D_frozen_files_verified=len(f['files']),
        source_hashes=hashes, source_files=441, builds=[], main_changed=False,
        inherited_rejected_Bill_changes=False, accepted_release=False, goal_complete=False)
    def save():
        (H / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
    save()
    spec = importlib.util.spec_from_file_location('ejimage', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for base in (False, True):
        for mapper in ('mmc3', 'mmc5'):
            tag = mapper + ('-baseline' if base else '')
            log = H / (tag + '-build.log')
            with log.open('wb') as stream:
                rc = subprocess.run([sys.executable, str(driver), '--mapper', mapper] + (['--baseline'] if base else []),
                                    cwd=R, stdout=stream, stderr=subprocess.STDOUT).returncode
            row = dict(mapper=mapper, baseline=base, exit=rc, log_sha256=sha(log))
            result['builds'].append(row)
            save()
            assert rc == 0, log
            stem = source / 'build' / ('smb-crossover-' + tag)
            row['artifacts'] = {ext: sha(stem.with_suffix('.' + ext)) for ext in ('nes', 'lbl', 'map', 'dbg')}
            old_row = next(x for x in ec['builds'] if x['mapper'] == mapper and x['baseline'] == base)
            if base:
                assert row['artifacts']['nes'] == old_row['artifacts']['nes']
                row['baseline_exact_CG_EC'] = True
            else:
                old = module.Image(ep.parent / 'source/build' / f'smb-crossover-{mapper}.nes')
                new = module.Image(stem.with_suffix('.nes'))
                assert old.ram == new.ram
                seg = lambda im, n: next(s for s in im.segs.values() if s['name'] == n)
                a, b = seg(old, 'RYU_COLD'), seg(new, 'RYU_COLD')
                assert a['size'] == 681 and b['size'] == 741
                assert a['start'] == b['start'] and a['ooffs'] == b['ooffs']
                start = old.hook('GuestVictoryGuestControl')['rom_offset']
                stop = b['ooffs'] + b['size']
                assert old.raw[:start] == new.raw[:start] and old.raw[stop:] == new.raw[stop:]
                assert seg(old, 'PLAYER')['size'] == seg(new, 'PLAYER')['size'] == 8132
                row.update(RAM_exact=len(old.ram), PLAYER_growth=0, RYU_COLD_growth=60,
                           only_ROM_delta_inside_rare_helper=True, inherited_rejected_Bill_changes=False)
            save()
    assert all(sha(source / n) == h for n, h in hashes.items())
    assert all(sha(R / n) == h for n, h in main_state['source_hashes'].items())
    result['status'] = 'PASS_PRIVATE_EJ_FOUR_BUILDS_SOLE_EASYLINK_HELPER_ON_EC_NATIVE_REBIND_PENDING'
    save()
    print(result['status'], sha(H / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
