"""Provisional private G2 plus installed Link helper; no main admission."""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-bill-axis-link-eu'
G = V / 'agent49-bill-head-axis-g'
DQ = V / 'root49-body-victory-union-dq'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    main_path = R / 'build/checkpoints/roster-audit-v49-link-watch-el/manifest.json'
    assert sha(main_path) == '7cf7f1ebf96f21184e5b9b7d2eff5a832038862a1e057f19f7a00018fb0f92e4'
    main_state = json.loads(main_path.read_text())
    assert all(sha(R / n) == h for n, h in main_state['source_hashes'].items())
    dq = json.loads((DQ / 'report.json').read_text())
    assert sha(DQ / 'report.json') == '40b361bb28db5f1e923c8079d1256bddfd622714ddd46ec44f9110f3039536a7'
    g2 = json.loads((G / 'build-g2.json').read_text())
    expected = dict(dq['source_hashes'])
    assert set(g2['source_inputs']) == {'src/bill_source_body.s', 'src/collision.s',
        'src/megaman_environment.s', 'src/roster.s'}
    expected.update(g2['source_inputs'])
    assert len(expected) == 442
    assert all(sha(G / 'source-g' / n) == h for n, h in expected.items())
    g_roms = dict(mmc3='2e91031f1c0d01a30640d75c16f8e993f4a0f2b82926cae23ad92d1a63769959',
        mmc5='9ba614e261a6e86e643eb821b2f22a7ef8fa26d81efa1cb8e8059debc812de9f')
    assert all(sha(G / 'source-g/build' / f'smb-crossover-{k}.nes') == h for k, h in g_roms.items())
    helper = 'src/guest_victory_control.s'
    assert main_state['source_hashes'][helper] == '12454f9e7c249ae27fc2caf9fae9225f9bc565db2dce4adac8515f9f3fcf39f1'
    assert expected[helper] != main_state['source_hashes'][helper]
    H.mkdir(exist_ok=False)
    source = H / 'source'
    for n in expected:
        target = source / n
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(G / 'source-g' / n, target)
    shutil.copyfile(R / helper, source / helper)
    hashes = dict(expected)
    hashes[helper] = sha(source / helper)
    for n, h in dq['generated_inputs'].items():
        old = DQ / 'source/build/generated' / n
        assert sha(old) == h
        target = source / 'build/generated' / n
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(old, target)
    driver = H / 'build-driver.py'
    content = (DQ / 'build-driver.py').read_text()
    needle = 'ROOT = Path(' + repr(str(DQ / 'source')) + ')'
    assert content.count(needle) == 1
    driver.write_text(content.replace(needle, 'ROOT = Path(' + repr(str(source)) + ')'))
    parser = V / 'agent49g-samus-crouch-fix-proposal-b/image.py'
    assert sha(parser) == '54fef35b891a96d5d0e36ca6cdeec9ee90b990666395714bc32e80cd1cabb0fb'
    spec = importlib.util.spec_from_file_location('eu_image', parser)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    report = dict(status='BUILDING_PRIVATE_PROVISIONAL_EU_G2_PLUS_EL_HELPER',
        script_sha256=sha(__file__), actual_main_EL_sha256=sha(main_path),
        g2_input_report_sha256=sha(G / 'build-g2.json'), g2_source_hashes=expected,
        source_hashes=hashes, source_files=len(hashes), generated_inputs=dq['generated_inputs'],
        source_changes_from_G2=[helper], G2_correctness_ordinary_cost_freeze_pending=True,
        native_combined_rebind_pending=True, main_changed=False,
        accepted_release=False, goal_complete=False, builds=[])

    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    baselines = dict(mmc3='0511c6844d0e9fa61f4b4fbc34e6f9c67d8247d3ca964ebbb0c9c2718cdc5146',
        mmc5='34858561f4825dcc96cdd5fd46872f9230890c93af95351720c8536155f5cbbd')
    for base in (False, True):
        for mapper in ('mmc3', 'mmc5'):
            tag = mapper + ('-baseline' if base else '')
            log = H / (tag + '-build.log')
            with log.open('wb') as stream:
                rc = subprocess.run([sys.executable, str(driver), '--mapper', mapper] +
                    (['--baseline'] if base else []), cwd=R, stdout=stream,
                    stderr=subprocess.STDOUT).returncode
            row = dict(mapper=mapper, baseline=base, exit=rc, log_sha256=sha(log))
            report['builds'].append(row)
            save()
            assert rc == 0, log
            stem = source / 'build' / ('smb-crossover-' + tag)
            row['artifacts'] = {ext: sha(stem.with_suffix('.' + ext)) for ext in ('nes', 'lbl', 'map', 'dbg')}
            if base:
                assert row['artifacts']['nes'] == baselines[mapper]
                row['baseline_exact_CG'] = True
            else:
                old = module.Image(G / 'source-g/build' / f'smb-crossover-{mapper}.nes')
                new = module.Image(stem.with_suffix('.nes'))
                assert old.ram == new.ram
                segment = lambda im, n: next(s for s in im.segs.values() if s['name'] == n)
                a, b = segment(old, 'RYU_COLD'), segment(new, 'RYU_COLD')
                assert a['size'] == 681 and b['size'] == 741
                assert a['start'] == b['start'] and a['ooffs'] == b['ooffs']
                start = old.hook('GuestVictoryGuestControl')['rom_offset']
                stop = b['ooffs'] + b['size']
                assert old.raw[:start] == new.raw[:start] and old.raw[stop:] == new.raw[stop:]
                assert segment(old, 'PLAYER')['size'] == segment(new, 'PLAYER')['size'] == 8140
                row.update(all_G2_RAM_exact=True, all_G2_PLAYER_code_exact=True,
                    sole_ROM_delta_rare_helper=True, RYU_COLD_growth=60,
                    G2_ROM_sha256=g_roms[mapper], PLAYER_growth=0)
            save()
    assert all(sha(source / n) == h for n, h in hashes.items())
    assert all(sha(G / 'source-g' / n) == h for n, h in expected.items())
    assert all(sha(R / n) == h for n, h in main_state['source_hashes'].items())
    report['status'] = 'PASS_PRIVATE_PROVISIONAL_EU_FOUR_BUILDS_G2_PLUS_SOLE_EL_HELPER_PENDING_FREEZE_AND_NATIVE'
    save()
    print(report['status'], sha(H / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
