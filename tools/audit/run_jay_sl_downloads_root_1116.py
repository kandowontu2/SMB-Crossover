"""Run strict ordinary Jay Star/life controllers from actual Downloads."""
from pathlib import Path
import json

import replay_jay_natural_sl_00bb_1116 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

J = F.J
OUT = J.R/'build/smb2-flag-native-1113'
GRANT = J.R/'docs/qa/allocations/jay-sl-downloads-root-1116.json'


def main():
    g = json.loads(GRANT.read_bytes())
    assert g['actual_Downloads_native_authorized'] and not g['ROM_replacement_authorized']
    assert J.H(Path(F.__file__).read_bytes()) == g['factory_SHA256']
    official = J.ROM
    raw = official.read_bytes()
    before = check(official)
    assert J.H(raw) == J.PIN == g['ROM_SHA256']
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    assert (OUT/'candidate.nes').read_bytes() == raw
    Storage.preflight(private_root=OUT, reserved_bytes=0, reserved_files=0, fresh=True)
    require_free_workspace(J.R, official, allow_interactive=True)
    for kind in ('life', 'star'):
        text = F.controller(raw, kind)
        assert J.H(text.encode()) == g['Lua_SHA256'][kind]
        script = OUT/'controller.lua'
        script.write_bytes(text.encode())
        q = run(script, official, OUT/'capture', J.PIN, 240)
        assert official.read_bytes() == (OUT/'candidate.nes').read_bytes() == raw
        assert check(official) == before
        assert q['outputs_written'] == 0 and not q['images']
        assert q['script_SHA256'] == g['Lua_SHA256'][kind]
        report = {k: v for k, v in q.items() if k not in ('images', 'capture_preflight')}
        report.update(actual_Downloads=True, kind=kind)
        print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
        assert q['passed'], 'Retain the exact native negative before any new proposal'
        r = q['receipt']
        assert r['controller_only'] and r['no_gameplay_or_actor_or_health_seeds']
        assert r['no_fullstage_or_cadence_claim'] and r['pending'] == 0


if __name__ == '__main__':
    main()
