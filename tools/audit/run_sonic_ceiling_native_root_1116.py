"""Root's two-file queue: exact complete Sonic ceiling candidate or Downloads."""
import argparse
import importlib
import json
from pathlib import Path
import compose_sonic_ceiling_complete_1327_1116 as C
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT = C.R/'build/smb2-flag-native-1113'
FACTORIES = {'replay_sonic_ceiling_life_a2d9_1116',
             'replay_sonic_ceiling_full11_a2d9_1116'}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--downloads', action='store_true')
    p.add_argument('--full', action='store_true')
    a = p.parse_args()
    prefix = 'sonic-ceiling-full-' if a.full else 'sonic-ceiling-'
    name = prefix+('delivery' if a.downloads else 'private')+'-root-1116.json'
    grant = C.R/'docs/qa/allocations'/name
    g = json.loads(grant.read_bytes())
    grant_hash = C.H(grant.read_bytes())
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
        assert C.H(before) == C.PIN == g['parent_SHA256']
        raw, composition = C.proposal(before)
        assert C.inverse(raw) == before and composition['all_unowned_bytes_exact']
        assert (composition['owned_bytes'], composition['changed_bytes']) == (94, 91)
        rom = target
    Storage.preflight(private_root=OUT, fresh=True)
    require_free_workspace(C.R, rom, allow_interactive=True)
    try:
        if not a.downloads:
            target.write_bytes(raw)
        assert target.read_bytes() == raw and check(rom)['ROM_sha256'] == C.CANDIDATE
        for case in g['cases']:
            assert case['factory_module'] in FACTORIES and case['form'] in ('sonic', 'super')
            f = importlib.import_module(case['factory_module'])
            assert C.H(Path(f.__file__).read_bytes()) == case['factory_SHA256']
            text = f.controller(raw, case['form'])
            assert C.H(text.encode()) == case['Lua_SHA256']
            script = OUT/'controller.lua'
            script.write_bytes(text.encode())
            q = run(script, rom, OUT/'capture', C.CANDIDATE, 180)
            assert official.read_bytes() == before and check(official) == guard
            assert target.read_bytes() == raw and not q['images'] and q['outputs_written'] == 0
            assert q['script_SHA256'] == case['Lua_SHA256']
            report = {k: v for k, v in q.items() if k not in ('images', 'capture_preflight')}
            report.update(kind=case['kind'], form=case['form'], actual_Downloads=a.downloads,
                          grant_SHA256=grant_hash)
            if a.downloads:
                report['exact_private_receipt_match'] = q['receipt_SHA256'] == case['private_native_receipt_SHA256']
            print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
            assert q['passed'], 'Retain actual native negative before any revision'
            if a.downloads:
                assert report['exact_private_receipt_match']
    finally:
        if not a.downloads:
            target.write_bytes(before)
        assert target.read_bytes() == before
        assert official.read_bytes() == before and check(official) == guard


if __name__ == '__main__':
    main()
