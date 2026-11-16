"""Observe the known-incomplete current DK Jr repair in the root Mesen queue."""
from pathlib import Path
import json

import replay_dkjr_pipe5_depart_defense_1116 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

C = F.C
OUT = C.R/'build/smb2-flag-native-1113'
GRANT = C.R/'docs/qa/allocations/dkjr-footer-current-private-route-root-1116.json'


def run_case(F, grant_path):
    C = F.C
    g = json.loads(grant_path.read_bytes())
    assert g['private_staging_and_native_authorized'] and not g['Downloads_delivery_authorized']
    assert C.H(Path(C.__file__).read_bytes()) == g['composer_SHA256']
    assert C.H(Path(F.__file__).read_bytes()) == g['factory_SHA256']
    official = C.BT.ROM
    before = check(official)
    parent = official.read_bytes()
    assert C.H(parent) == C.PIN == g['parent_SHA256']
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    target = OUT/'candidate.nes'
    assert target.read_bytes() == parent
    raw, composition = C.proposal(parent)
    assert C.H(raw) == C.CANDIDATE == g['candidate_SHA256'] and C.inverse(raw) == parent
    assert composition['owned_bytes'] == g['owned_bytes'] == 383
    assert composition['changed_bytes'] == g['changed_bytes'] == 281
    assert composition['all_unowned_current91dc_exact']
    text = F.controller(raw)
    assert C.H(text.encode()) == g['Lua_SHA256']
    Storage.preflight(private_root=OUT, reserved_bytes=0, reserved_files=0, fresh=True)
    require_free_workspace(C.R, target, allow_interactive=True)
    try:
        target.write_bytes(raw)
        assert check(target)['ROM_sha256'] == C.CANDIDATE
        script = OUT/'controller.lua'
        script.write_bytes(text.encode())
        q = run(script, target, OUT/'capture', C.CANDIDATE, 240,
                extra_env={'SMB_DKJR_FAST_ROUTE': '1'})
        assert not q['images'] and q['outputs_written'] == 0
        assert q['script_SHA256'] == g['Lua_SHA256'] and target.read_bytes() == raw
        r = q['receipt']
        assert not r.get('script_RAM_writes', r.get('game_state_writes', False))
        report = {k: v for k, v in q.items() if k not in ('receipt', 'images', 'capture_preflight')}
        report['receipt'] = {k: v for k, v in r.items() if k not in ('events', 'carries', 'trace', 'samples')}
        report['event_tail'] = r.get('events', [])[-8:]
        report['carries'] = {k: dict(count=v.get('count'), first=v.get('first'), last=v.get('last'))
                             for k, v in r.get('carries', {}).items()}
        report['private_diagnostic_only'] = True
        report['actual_Downloads_unchanged'] = True
        print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
        # A recorded negative is an expected diagnostic outcome, never a pass.
    finally:
        assert official.read_bytes() == parent and check(official) == before
        target.write_bytes(parent)
        assert target.read_bytes() == parent
    return report


if __name__ == '__main__':
    run_case(F, GRANT)
