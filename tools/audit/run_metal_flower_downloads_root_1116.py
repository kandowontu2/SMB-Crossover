"""Verify the genuine Metal weapon pickup and an upgraded native enemy kill."""
from pathlib import Path
import json
import replay_metal_flower_00bb_1116 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run
from run_metal_life_private_root_1116 import compact

OUT = F.R/'build/smb2-flag-native-1113'
GRANT = F.R/'docs/qa/allocations/metal-flower-downloads-root-1116.json'


def main():
    g = json.loads(GRANT.read_bytes())
    assert g['native_Mesen_actual_Downloads_authorized'] and not g['ROM_replacement_authorized']
    assert F.digest(Path(F.__file__).read_bytes()) == g['factory_SHA256']
    raw = F.ROM.read_bytes()
    before = check(F.ROM)
    assert F.digest(raw) == F.PIN == g['ROM_SHA256']
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    assert (OUT/'candidate.nes').read_bytes() == raw
    text = F.controller(raw, 'flower')
    assert F.digest(text.encode()) == g['Lua_SHA256']
    Storage.preflight(private_root=OUT, reserved_bytes=0, reserved_files=0, fresh=True)
    require_free_workspace(F.R, F.ROM, allow_interactive=True)
    script = OUT/'controller.lua'
    script.write_bytes(text.encode())
    q = run(script, F.ROM, OUT/'capture', F.PIN, 240)
    assert F.ROM.read_bytes() == (OUT/'candidate.nes').read_bytes() == raw
    assert check(F.ROM) == before and q['outputs_written'] == 0 and not q['images']
    assert q['script_SHA256'] == g['Lua_SHA256']
    report = {k: v for k, v in q.items() if k not in ('receipt', 'images', 'capture_preflight')}
    report.update(receipt=compact(q['receipt']), kind='flower', actual_Downloads=True)
    print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
    assert q['passed'], 'Retain the native negative before proposing changes'
    assert not q['receipt'].get('game_state_writes', False)


if __name__ == '__main__':
    main()
