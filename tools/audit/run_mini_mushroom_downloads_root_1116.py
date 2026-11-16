"""Root single-queue Mini Mushroom test from actual installed Downloads."""
import json
from pathlib import Path
import replay_mini_mushroom_1327_1116 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

OUT = F.R/'build/smb2-flag-native-1113'


def main():
    grant = json.loads((F.R/'docs/qa/allocations/mini-mushroom-downloads-root-1116.json').read_bytes())
    assert grant['actual_Downloads_native_authorized']
    assert not grant['ROM_replacement_or_gameplay_seeds_authorized']
    assert F.H(Path(F.__file__).read_bytes()) == grant['factory_SHA256']
    raw = F.ROM.read_bytes()
    before = check(F.ROM)
    assert F.H(raw) == F.PIN == grant['ROM_SHA256']
    assert not before['matching_patch_files']
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    assert (OUT/'candidate.nes').read_bytes() == raw
    text = F.controller(raw, 'mushroom')
    assert F.H(text.encode()) == grant['Lua_SHA256']
    Storage.preflight(private_root=OUT, fresh=True)
    require_free_workspace(F.R, F.ROM, allow_interactive=True)
    script = OUT/'controller.lua'
    script.write_bytes(text.encode())
    q = run(script, F.ROM, OUT/'capture', F.PIN, 180)
    assert F.ROM.read_bytes() == (OUT/'candidate.nes').read_bytes() == raw
    assert check(F.ROM) == before and not q['images'] and q['outputs_written'] == 0
    assert q['script_SHA256'] == grant['Lua_SHA256']
    report = {k: v for k, v in q.items() if k not in ('images', 'capture_preflight')}
    report['actual_Downloads'] = True
    print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
    assert q['passed'], 'Retain actual native negative before changing controls'
    r = q['receipt']
    assert not r['game_state_writes'] and r['gameplay_seeds'] == 0
    assert r['item']['power_updates'] == r['item']['private_power_entries'] == 60
    assert r['item']['resumed_steps'] == r['item']['resumed_moves'] == 25


if __name__ == '__main__':
    main()
