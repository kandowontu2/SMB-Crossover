"""Private root-queue L/Star tests of the exact34-byte life repair."""
import json
from pathlib import Path

import compose_metal_life_snapshot_root_1116 as C
import replay_metal_life_00bb_1116 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT = C.R/'build/smb2-flag-native-1113'
GRANT = C.R/'docs/qa/allocations/metal-life-private-root-1116.json'


def compact(r):
    result = {k: v for k, v in r.items() if k not in ('trace', 'samples', 'events', 'M', 'stock')}
    for name in ('M', 'stock'):
        if name in r:
            result[name] = {k: v for k, v in r[name].items()
                            if k not in ('pipe_proof', 'gap_proof', 'accepted_head', 'head_samples')}
    return result


def main():
    g = json.loads(GRANT.read_bytes())
    assert g['private_staging_and_native_authorized'] and not g['Downloads_delivery_authorized']
    assert C.H(Path(C.__file__).read_bytes()) == g['composer_SHA256']
    assert C.H(Path(F.__file__).read_bytes()) == g['factory_SHA256']
    official = C.Plan.Current.ROM
    parent = official.read_bytes()
    before = check(official)
    assert C.H(parent) == C.PIN == g['parent_SHA256']
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    target = OUT/'candidate.nes'
    assert target.read_bytes() == parent
    raw, composition = C.proposal(parent)
    assert C.H(raw) == C.CANDIDATE == F.PIN == g['candidate_SHA256'] and C.inverse(raw) == parent
    assert (composition['owned_bytes'], composition['changed_bytes']) == (34, 30)
    assert composition['all_unowned_current7c0f_bytes_exact']
    Storage.preflight(private_root=OUT, reserved_bytes=0, reserved_files=0, fresh=True)
    require_free_workspace(C.R, target, allow_interactive=True)
    try:
        target.write_bytes(raw)
        assert check(target)['ROM_sha256'] == C.CANDIDATE
        for kind in ('oneup', 'star'):
            text = F.controller(raw, kind)
            assert C.H(text.encode()) == g['Lua_SHA256'][kind]
            script = OUT/'controller.lua'
            script.write_bytes(text.encode())
            q = run(script, target, OUT/'capture', C.CANDIDATE, 240)
            assert not q['images'] and q['outputs_written'] == 0
            assert q['script_SHA256'] == g['Lua_SHA256'][kind] and target.read_bytes() == raw
            r = q['receipt']
            report = {k: v for k, v in q.items() if k not in ('receipt', 'images', 'capture_preflight')}
            report.update(kind=kind, receipt=compact(r), private_only=True, actual_Downloads_unchanged=True)
            print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
            assert q['passed'], 'Retain native negative; no qualification claim'
            assert not r.get('game_state_writes', False)
            if kind == 'oneup':
                assert r['terminal']['armor'] == 128 and r['terminal']['lives'] == 3
                assert not r.get('stock', {}).get('earned_life_constructor')
    finally:
        assert official.read_bytes() == parent and check(official) == before
        target.write_bytes(parent)
        assert target.read_bytes() == parent


if __name__ == '__main__':
    main()
