"""Root two-file native queue: exact Rogue missile fix preserving Mini/Sonic."""
import argparse
import json
from pathlib import Path
import compose_rogue_missile_9826_1116 as C
import replay_rogue_missile_cb95_1116 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT = C.R/'build/smb2-flag-native-1113'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--downloads', action='store_true')
    a = p.parse_args()
    name = 'rogue-missile-cb95-'+('delivery' if a.downloads else 'private')+'-root-1116.json'
    grant = C.R/'docs/qa/allocations'/name
    g = json.loads(grant.read_bytes())
    assert C.H(Path(C.__file__).read_bytes()) == g['composer_SHA256']
    assert C.H(Path(F.__file__).read_bytes()) == g['factory_SHA256']
    assert g['candidate_SHA256'] == C.CANDIDATE
    assert {q.name for q in OUT.iterdir() if q.is_file()} == {'candidate.nes', 'controller.lua'}
    before = C.ROM.read_bytes()
    guard = check(C.ROM)
    assert not guard['matching_patch_files']
    target = OUT/'candidate.nes'
    assert target.read_bytes() == before
    if a.downloads:
        assert g['actual_Downloads_native_authorized'] and C.H(before) == C.CANDIDATE
        raw, rom = before, C.ROM
    else:
        assert g['private_staging_and_native_authorized'] and not g['Downloads_replacement_authorized']
        assert C.H(before) == C.PARENT == g['parent_SHA256']
        raw, proof = C.proposal(before)
        assert C.inverse(raw) == before and proof['all_unowned_bytes_exact']
        assert proof['protected'] == ['Mini20', 'Sonic94']
        assert (proof['owned_bytes'], proof['changed_bytes']) == (2, 1)
        rom = target
    Storage.preflight(private_root=OUT, fresh=True)
    require_free_workspace(C.R, rom, allow_interactive=True)
    try:
        if not a.downloads:
            target.write_bytes(raw)
        assert target.read_bytes() == raw and check(rom)['ROM_sha256'] == C.CANDIDATE
        for case in g['cases']:
            assert case['kind'] in ('missile', 'full')
            text = F.controller(raw, case['kind'])
            assert C.H(text.encode()) == case['Lua_SHA256']
            script = OUT/'controller.lua'
            script.write_bytes(text.encode())
            q = run(script, rom, OUT/'capture', C.CANDIDATE, 180)
            assert C.ROM.read_bytes() == before and check(C.ROM) == guard
            assert target.read_bytes() == raw and not q['images'] and q['outputs_written'] == 0
            report = {k: v for k, v in q.items() if k not in ('images', 'capture_preflight')}
            report.update(kind=case['kind'], actual_Downloads=a.downloads,
                          grant_SHA256=C.H(grant.read_bytes()))
            if a.downloads:
                report['exact_private_receipt_match'] = q['receipt_SHA256'] == case['private_native_receipt_SHA256']
            print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
            assert q['passed'], 'Retain native negative before changing controls or code'
            if a.downloads:
                assert report['exact_private_receipt_match']
    finally:
        if not a.downloads:
            target.write_bytes(before)
        assert target.read_bytes() == before and C.ROM.read_bytes() == before
        assert check(C.ROM) == guard


if __name__ == '__main__':
    main()
