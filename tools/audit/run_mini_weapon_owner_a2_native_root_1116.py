"""Root's existing two-file queue: Mini20 over Sonic, private or Downloads."""
import argparse
import importlib
import json
from pathlib import Path
import compose_mini_weapon_owner_a2_1116 as C
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT = C.R/'build/smb2-flag-native-1113'
FACTORIES = {'replay_mini_weapon_owner_twoshot_a2_1116',
             'replay_mini_weapon_owner_full11_a2_1116'}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--downloads', action='store_true')
    a = p.parse_args()
    name = 'mini-weapon-owner-a2-'+('delivery' if a.downloads else 'private')+'-root-1116.json'
    grant = C.R/'docs/qa/allocations'/name
    g = json.loads(grant.read_bytes())
    assert C.H(Path(C.__file__).read_bytes()) == g['composer_SHA256']
    assert g['candidate_SHA256'] == C.CANDIDATE
    assert {q.name for q in OUT.iterdir() if q.is_file()} == {'candidate.nes', 'controller.lua'}
    official = C.ROM
    before = official.read_bytes()
    guard = check(official)
    assert not guard['matching_patch_files']
    target = OUT/'candidate.nes'
    assert target.read_bytes() == before
    if a.downloads:
        assert g['actual_Downloads_native_authorized']
        assert C.H(before) == C.CANDIDATE
        raw, rom = before, official
    else:
        assert g['private_staging_and_native_authorized'] and not g['Downloads_replacement_authorized']
        assert C.H(before) == C.PARENT == g['parent_SHA256']
        raw, composition = C.proposal(before)
        assert C.inverse(raw) == before and composition['all_unowned_bytes_exact']
        assert composition['Sonic94_preserved']
        assert (composition['owned_bytes'], composition['changed_bytes']) == (20, 20)
        rom = target
    Storage.preflight(private_root=OUT, fresh=True)
    require_free_workspace(C.R, rom, allow_interactive=True)
    try:
        if not a.downloads:
            target.write_bytes(raw)
        assert target.read_bytes() == raw and check(rom)['ROM_sha256'] == C.CANDIDATE
        for case in g['cases']:
            assert case['factory_module'] in FACTORIES and case['kind'] in ('flower', 'full11')
            f = importlib.import_module(case['factory_module'])
            assert C.H(Path(f.__file__).read_bytes()) == case['factory_SHA256']
            text = f.controller(raw, case['kind'])
            assert C.H(text.encode()) == case['Lua_SHA256']
            script = OUT/'controller.lua'
            script.write_bytes(text.encode())
            q = run(script, rom, OUT/'capture', C.CANDIDATE, 180)
            assert official.read_bytes() == before and check(official) == guard
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
        assert target.read_bytes() == before
        assert official.read_bytes() == before and check(official) == guard


if __name__ == '__main__':
    main()
