"""Run frozen Jay status/size cases in root's existing two-file queue."""
import argparse
import importlib
import json
from pathlib import Path

import compose_jay_status_size_publication_00bb_1116 as C
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT = C.R/'build/smb2-flag-native-1113'
FACTORIES = {'replay_jay_status_size_flower_1327_1116',
             'replay_jay_status_size_sl_1327_1116',
             'replay_jay_status_size_full11_1327_1116'}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--downloads', action='store_true')
    a = p.parse_args()
    name = 'jay-status-delivery-root-1116.json' if a.downloads else 'jay-status-private-root-1116.json'
    g = json.loads((C.R/'docs/qa/allocations'/name).read_bytes())
    assert C.H(Path(C.__file__).read_bytes()) == g['composer_SHA256']
    assert g['candidate_SHA256'] == C.CANDIDATE
    assert {q.name for q in OUT.iterdir() if q.is_file()} == {'candidate.nes', 'controller.lua'}
    official = C.Plan.ROM
    before = official.read_bytes()
    guard = check(official)
    target = OUT/'candidate.nes'
    assert target.read_bytes() == before
    if a.downloads:
        assert g['actual_Downloads_native_repeat_authorized']
        assert C.H(before) == C.CANDIDATE
        raw, rom = before, official
    else:
        assert g['private_staging_and_native_authorized'] and not g['Downloads_replacement_authorized']
        assert C.H(before) == C.PIN == g['parent_SHA256']
        raw, composition = C.proposal(before)
        assert C.inverse(raw) == before and composition['all_unowned_00bb_and34Metal_bytes_exact']
        assert (composition['owned_bytes'], composition['changed_bytes']) == (116, 72)
        rom = target
    Storage.preflight(private_root=OUT, reserved_bytes=0, reserved_files=0, fresh=True)
    require_free_workspace(C.R, rom, allow_interactive=True)
    try:
        if not a.downloads:
            target.write_bytes(raw)
        assert target.read_bytes() == raw and check(rom)['ROM_sha256'] == C.CANDIDATE
        for case in g['cases']:
            module, kind = case['factory_module'], case['kind']
            assert module in FACTORIES and kind in ('flower', 'life', 'star', 'full11')
            f = importlib.import_module(module)
            assert C.H(Path(f.__file__).read_bytes()) == case['factory_SHA256']
            text = f.controller(raw, kind)
            assert C.H(text.encode()) == case['Lua_SHA256']
            script = OUT/'controller.lua'
            script.write_bytes(text.encode())
            q = run(script, rom, OUT/'capture', C.CANDIDATE, 180)
            assert official.read_bytes() == before and check(official) == guard
            assert target.read_bytes() == raw and not q['images'] and q['outputs_written'] == 0
            assert q['script_SHA256'] == case['Lua_SHA256']
            report = {k: v for k, v in q.items() if k not in ('images', 'capture_preflight')}
            report.update(kind=kind, actual_Downloads=a.downloads)
            if a.downloads:
                report['exact_private_receipt_match'] = q['receipt_SHA256'] == case['private_native_receipt_SHA256']
            print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
            assert q['passed'], 'Retain the native negative before changing the proposal'
            if a.downloads:
                assert report['exact_private_receipt_match']
    finally:
        assert official.read_bytes() == before and check(official) == guard
        if not a.downloads:
            target.write_bytes(before)
        assert target.read_bytes() == before


if __name__ == '__main__':
    main()
