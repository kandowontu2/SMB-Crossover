"""Repeat the tested DK Jr route and both images from actual Downloads."""
from pathlib import Path
import json

import replay_dkjr_entry_images_root_1116 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

C = F.C
OUT = C.R/'build/smb2-flag-native-1113'
GRANT = C.R/'docs/qa/allocations/dkjr-entry-delivery-root-1116.json'


def main():
    g = json.loads(GRANT.read_bytes())
    assert g['Downloads_native_exact_repeat_authorized']
    assert C.H(Path(F.__file__).read_bytes()) == g['factory_SHA256']
    official = Path(g['target'])
    before = check(official)
    raw = official.read_bytes()
    assert C.H(raw) == C.CANDIDATE == g['tested_candidate_SHA256']
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    assert (OUT/'candidate.nes').read_bytes() == raw
    text = F.controller(raw)
    assert C.H(text.encode()) == g['Lua_SHA256']
    Storage.preflight(private_root=OUT, reserved_bytes=0, reserved_files=0, fresh=True)
    require_free_workspace(C.R, official, allow_interactive=True)
    script = OUT/'controller.lua'
    script.write_bytes(text.encode())
    q = run(script, official, OUT/'capture', C.CANDIDATE, 240,
            extra_env={'SMB_DKJR_FAST_ROUTE': '1'})
    assert official.read_bytes() == (OUT/'candidate.nes').read_bytes() == raw and check(official) == before
    assert q['outputs_written'] == 0 and q['script_SHA256'] == g['Lua_SHA256']
    report = {k: v for k, v in q.items() if k not in ('receipt', 'images', 'capture_preflight')}
    r = q['receipt']
    report['receipt'] = {k: v for k, v in r.items() if k not in ('events', 'carries', 'trace', 'samples')}
    report['images'] = [{k: v for k, v in p.items() if k != 'base64'} for p in q['images']]
    report['actual_Downloads'] = True
    report['exact_private_receipt_match'] = q['receipt_SHA256'] == g['private_native_receipt_SHA256']
    report['exact_private_image_match'] = [p['SHA256'] for p in q['images']] == g['private_image_SHA256']
    print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
    assert q['passed'] and report['exact_private_receipt_match'] and report['exact_private_image_match']
    assert len(q['images']) == 2 and r['original_work_grounded_returns'] >= 25
    assert not r.get('script_RAM_writes', r.get('game_state_writes', False))


if __name__ == '__main__':
    main()
