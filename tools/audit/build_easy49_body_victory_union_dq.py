"""Private four-build union of CG, frozen optimized Bill N, and rare victory C."""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
F = V / 'agent49-bill-source-body-f'
C = V / 'agent-lsr-victory-repair-c'
H = V / 'root49-body-victory-union-dq'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    dg_path = V / 'root49-bill-body-union-dg/report.json'
    assert sha(dg_path) == '3252ea899aa312e7cf8efefeabed360401d32589f468ddb6997dacc7dcb3ad43'
    dg = json.loads(dg_path.read_text())
    nf = F / 'freeze-o.json'
    assert sha(nf) == 'c0ee2a77e4bc72442588cc7618b96ce256d3f5aac725e9662c8e1cdef0d16049'
    n = json.loads(nf.read_text())
    cf = C / 'implementation-freeze.json'
    assert sha(cf) == '3a1d954e4f279fe850c3f5686d9ae03a90cc1d585438164070d2ca4cb68a4462'
    c = json.loads(cf.read_text())
    review = V / 'root49-victory-review-do.json'
    assert sha(review) == 'c859e1e53ce3bc3b443228ae5210b314727c8a7406419bb954f86c8df11a0568'
    nc_path = F / 'source-final-o-catalog.json'
    assert sha(nc_path) == n['source_catalog_sha256']
    nc = json.loads(nc_path.read_text())
    ns = Path(n['source'])
    assert len(nc) == 441 and all(sha(ns / k) == h for k, h in nc.items())
    old_catalog = json.loads((F / 'source-final-f-catalog.json').read_text())
    assert {k for k, h in nc.items() if old_catalog.get(k) != h} == {'src/bill_source_body.s'}
    assert sha(F / n['single_file_overlay']) == nc['src/bill_source_body.s'] == '02c545102a54e821f15fdb7e97db1f1d082b098366799fec5848d700cc61712f'
    receipts_path = F / 'receipt-catalog-o.json'
    assert sha(receipts_path) == n['receipts_sha256']
    receipts = json.loads(receipts_path.read_text())
    for name, row in receipts.items():
        p = F / name
        assert sha(p) == row['sha256'] and p.stat().st_size == row['bytes'], p
    for name, key in [('optimization-review-n.json', 'binary_math_review_sha256'),
                      ('optimization-profile-p.json', 'matched_profile_sha256'),
                      ('optimization-functional-o.json', 'functional_review_sha256'),
                      ('optimization-timing-negative-o.json', 'timing_qualification_sha256'),
                      ('oracle-catalog-o.json', 'source_oracle_catalog_sha256'),
                      ('reproduction-o.json', 'reproduction_sha256')]:
        assert sha(F / name) == n[key], name
    original = dg_path.parent / 'source'
    assert all(sha(original / k) == h for k, h in dg['source_hashes'].items())
    H.mkdir(exist_ok=False)
    source = H / 'source'
    hashes = dict(dg['source_hashes'])
    for name in hashes:
        target = source / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original / name, target)
    shutil.copyfile(F / n['single_file_overlay'], source / 'src/bill_source_body.s')
    hashes['src/bill_source_body.s'] = nc['src/bill_source_body.s']
    for name in ('src/player.s', 'src/game.s', 'src/guest_victory_control.s'):
        if name in c['parent_source_files']:
            assert hashes[name] == c['parent_source_files'][name], name
        else:
            assert name not in hashes
        assert sha(C / 'after' / name) == c['after_files'][name]
        shutil.copyfile(C / 'after' / name, source / name)
        hashes[name] = c['after_files'][name]
    # C appends an include to BY's entrypoint. Preserve F's earlier Bill include.
    parent_entry = (R / 'src/entrypoint.s').read_bytes()
    assert hashlib.sha256(parent_entry).hexdigest() == c['parent_source_files']['src/entrypoint.s']
    after_entry = (C / 'after/src/entrypoint.s').read_bytes()
    assert after_entry.startswith(parent_entry)
    delta = after_entry[len(parent_entry):]
    assert delta.decode().count('.include "guest_victory_control.s"') == 1
    entry_path = source / 'src/entrypoint.s'
    before_entry = entry_path.read_bytes()
    assert before_entry.count(b'.include "bill_source_body.s"') == 1
    entry_path.write_bytes(before_entry + delta)
    hashes['src/entrypoint.s'] = sha(entry_path)
    assert len(hashes) == 442
    generated = dg['generated_inputs']
    for name, digest in generated.items():
        old = original / 'build/generated' / name
        assert sha(old) == digest
        target = source / 'build/generated' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(old, target)
    driver_source = dg_path.parent / 'build-driver.py'
    driver = H / 'build-driver.py'
    text = driver_source.read_text()
    needle = 'ROOT = Path(' + repr(str(original)) + ')'
    assert text.count(needle) == 1
    driver.write_text(text.replace(needle, 'ROOT = Path(' + repr(str(source)) + ')'))
    report = dict(status='PRIVATE_DQ_N_PLUS_RARE_VICTORY_C_BUILDING', script_sha256=sha(__file__),
        DG_report_sha256=sha(dg_path), N_freeze_sha256=sha(nf), C_freeze_sha256=sha(cf),
        C_independent_review_sha256=sha(review), N_receipt_files_verified=len(receipts),
        source_hashes=hashes, source_files=442, generated_inputs=generated,
        driver_sha256=sha(driver), entrypoint_merge='Append exact C include delta to DG/F entrypoint; preserve Bill include.',
        builds=[], main_changed=False, admission_pending=True, accepted_release=False, goal_complete=False)
    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    parser = V / 'agent49g-samus-crouch-fix-proposal-b/image.py'
    assert sha(parser) == '54fef35b891a96d5d0e36ca6cdeec9ee90b990666395714bc32e80cd1cabb0fb'
    spec = importlib.util.spec_from_file_location('union_dq_image', parser)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    baseline = dict(mmc3='0511c6844d0e9fa61f4b4fbc34e6f9c67d8247d3ca964ebbb0c9c2718cdc5146',
                    mmc5='34858561f4825dcc96cdd5fd46872f9230890c93af95351720c8536155f5cbbd')
    cb = json.loads((C / 'build-report.json').read_text())['builds']
    for base in (False, True):
        for mapper in ('mmc3', 'mmc5'):
            tag = mapper + ('-baseline' if base else '')
            log = H / (tag + '-build.log')
            with log.open('wb') as stream:
                rc = subprocess.run([sys.executable, str(driver), '--mapper', mapper] + (['--baseline'] if base else []),
                                    cwd=R, stdout=stream, stderr=subprocess.STDOUT).returncode
            row = dict(mapper=mapper, baseline=base, exit=rc, log_sha256=sha(log))
            report['builds'].append(row)
            save()
            assert rc == 0, log
            stem = source / 'build' / ('smb-crossover-' + tag)
            row['artifacts'] = {ext: sha(stem.with_suffix('.' + ext)) for ext in ('nes', 'lbl', 'map', 'dbg')}
            if base:
                assert row['artifacts']['nes'] == baseline[mapper]
                row['baseline_exact_CG'] = True
            else:
                old = module.Image(ns / 'build' / f'smb-crossover-{mapper}.nes')
                new = module.Image(stem.with_suffix('.nes'))
                control = module.Image(C / 'source/build' / f'smb-crossover-{mapper}.nes')
                assert new.ram == old.ram
                seg = lambda im, name: next(x for x in im.segs.values() if x['name'] == name)
                os, ss = seg(old, 'PLAYER'), seg(new, 'PLAYER')
                oc, sc = seg(old, 'RYU_COLD'), seg(new, 'RYU_COLD')
                assert os['size'] == 8110 and ss['size'] == 8140
                assert oc['size'] == 497 and sc['size'] == 681
                assert seg(new, 'BILL_BODY_COLD')['size'] == 853
                assert ss['start'] == os['start'] and sc['start'] == oc['start']
                allowed = set(next(x for x in cb if x['mapper'] == mapper and not x['baseline'])['rare_call_operand_offsets'])
                for a, b in [(os, ss), (oc, sc)]:
                    allowed.update(range(a['ooffs'] + a['size'], b['ooffs'] + b['size']))
                changed = {i for i, (a, b) in enumerate(zip(old.raw, new.raw)) if a != b}
                assert changed <= allowed, sorted(changed - allowed)
                for name, append in [('PLAYER', 30), ('RYU_COLD', 184)]:
                    a, b = seg(control, name), seg(new, name)
                    assert control.raw[a['ooffs'] + a['size'] - append:a['ooffs'] + a['size']] == new.raw[b['ooffs'] + b['size'] - append:b['ooffs'] + b['size']], name
                free = 8192 - seg(new, 'SMCCODE')['size'] - ss['size']
                assert free == (3 if mapper == 'mmc3' else 19)
                assert new.raw[:16] == old.raw[:16] and new.raw[524304:] == old.raw[524304:]
                row.update(only_delta_from_N_rare_operands_and_exact_C_tails=True, changed_bytes=len(changed),
                           exact_C_PLAYER_tail=30, exact_C_RYU_COLD_tail=184, PLAYER_bytes=8140,
                           PLAYER_bank_free=free, BILL_BODY_COLD_bytes=853,
                           old_RAM_exact=len(old.ram), header_CHR_audio_DPCM_SMC_preserved=True)
            save()
    assert all(sha(source / k) == h for k, h in hashes.items())
    parent = json.loads((R / 'build/checkpoints/roster-audit-v49-easy-hard-by/manifest.json').read_text())
    assert all(sha(R / k) == h for k, h in parent['source_hashes'].items())
    report['status'] = 'PASS_PRIVATE_DQ_FOUR_BUILDS_EXACT_COMPONENT_BYTE_UNION_ADMISSION_PENDING'
    save()
    print(report['status'], sha(H / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
