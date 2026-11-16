"""Repeat both tested Metal cases from the exact Downloads launch context."""
from pathlib import Path
import json

import compose_metal_life_snapshot_root_1116 as C
import replay_metal_life_00bb_1116 as F
from run_metal_life_private_root_1116 import compact
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT = C.R/'build/smb2-flag-native-1113'
GRANT = C.R/'docs/qa/allocations/metal-life-delivery-root-1116.json'


def main():
    g = json.loads(GRANT.read_bytes())
    assert g['Downloads_native_exact_repeat_authorized']
    assert C.H(Path(F.__file__).read_bytes()) == g['factory_SHA256']
    official = Path(g['target'])
    before = check(official)
    raw = official.read_bytes()
    assert C.H(raw) == C.CANDIDATE == F.PIN == g['tested_candidate_SHA256']
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    assert (OUT/'candidate.nes').read_bytes() == raw
    Storage.preflight(private_root=OUT, reserved_bytes=0, reserved_files=0, fresh=True)
    require_free_workspace(C.R, official, allow_interactive=True)
    for kind in ('oneup', 'star'):
        text = F.controller(raw, kind)
        assert C.H(text.encode()) == g['Lua_SHA256'][kind]
        script = OUT/'controller.lua'
        script.write_bytes(text.encode())
        q = run(script, official, OUT/'capture', C.CANDIDATE, 240)
        assert official.read_bytes() == (OUT/'candidate.nes').read_bytes() == raw and check(official) == before
        assert not q['images'] and q['outputs_written'] == 0 and q['script_SHA256'] == g['Lua_SHA256'][kind]
        report = {k: v for k, v in q.items() if k not in ('receipt', 'images', 'capture_preflight')}
        report.update(kind=kind, receipt=compact(q['receipt']), actual_Downloads=True,
                      exact_private_receipt_match=q['receipt_SHA256'] == g['private_native_receipt_SHA256'][kind])
        print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
        assert q['passed'] and report['exact_private_receipt_match']
        assert not q['receipt'].get('game_state_writes', False)


if __name__ == '__main__':
    main()
