"""Root single-queue private DK Jr entry validation with two RAM-only PNGs."""
from pathlib import Path
import json

import replay_dkjr_entry_images_root_1116 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

C = F.C
OUT = C.R/'build/smb2-flag-native-1113'
GRANT = C.R/'docs/qa/allocations/dkjr-entry-private-root-1116.json'


def main():
    g = json.loads(GRANT.read_bytes())
    assert g['private_staging_and_native_authorized'] and not g['Downloads_delivery_authorized']
    assert isinstance(g['source_IRQ_receipt_SHA256'], str) and len(g['source_IRQ_receipt_SHA256']) == 64
    assert g['root_full_source_receipt_SHA256'] == '83da446ed50d0117591c19b005dab74110745cc4ce1aa317f1b58f31dd9762ae'
    assert C.H(Path(C.__file__).read_bytes()) == g['composer_SHA256']
    assert C.H(Path(F.__file__).read_bytes()) == g['factory_SHA256']
    official = C.BT.ROM
    parent = official.read_bytes()
    before = check(official)
    assert C.H(parent) == C.Parent.PIN == g['public_parent_SHA256']
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    target = OUT/'candidate.nes'
    assert target.read_bytes() == parent
    alpha, _ = C.Parent.proposal(parent)
    raw, composition = C.proposal(alpha)
    assert C.H(raw) == C.CANDIDATE == g['candidate_SHA256']
    assert C.inverse(raw) == alpha and C.Parent.inverse(alpha) == parent
    assert (composition['owned_bytes'], composition['changed_bytes']) == (1086, 863)
    assert composition['all_unowned_a3fb_bytes_exact']
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
        assert q['outputs_written'] == 0 and len(q['images']) <= 2
        assert all(p['bytes'] <= 65536 for p in q['images'])
        assert q['script_SHA256'] == g['Lua_SHA256'] and target.read_bytes() == raw
        r = q['receipt']
        assert not r.get('script_RAM_writes', r.get('game_state_writes', False))
        report = {k: v for k, v in q.items() if k not in ('receipt', 'images', 'capture_preflight')}
        report['receipt'] = {k: v for k, v in r.items() if k not in ('events', 'carries', 'trace', 'samples')}
        report['event_tail'] = r.get('events', [])[-8:]
        report['carries'] = {k: dict(count=v.get('count'), first=v.get('first'), last=v.get('last'))
                             for k, v in r.get('carries', {}).items()}
        report['images'] = [{k: v for k, v in p.items() if k != 'base64'} for p in q['images']]
        report['private_candidate_only'] = True
        report['actual_Downloads_unchanged'] = True
        print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
        for p in q['images']:
            print('IMAGE '+json.dumps(p, separators=(',', ':')), flush=True)
        if not q['passed']:
            raise SystemExit(1)
        assert len(q['images']) == 2 and r['original_work_grounded_returns'] >= 25
    finally:
        assert official.read_bytes() == parent and check(official) == before
        target.write_bytes(parent)
        assert target.read_bytes() == parent


if __name__ == '__main__':
    main()
