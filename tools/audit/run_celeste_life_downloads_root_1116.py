"""Run Celeste's frozen stock/earned-dash tests from actual Downloads."""
import argparse
import json
from pathlib import Path
import replay_celeste_head_cell_00bb_1116 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run
from run_metal_life_private_root_1116 import compact

OUT = F.R/'build/smb2-flag-native-1113'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--kind', choices=('oneup', 'star', 'flower'), default='oneup')
    kind = p.parse_args().kind
    factory = F
    if kind == 'flower':
        import replay_celeste_flower_local_dash_00bb_1116 as factory
    grant_name = {'oneup': 'celeste-life-downloads-root-1116.json',
                  'star': 'celeste-star-downloads-root-1116.json',
                  'flower': 'celeste-flower-downloads-root-1116.json'}[kind]
    g = json.loads((F.R/'docs/qa/allocations'/grant_name).read_bytes())
    assert g['actual_Downloads_native_authorized'] and not g['ROM_replacement_authorized']
    assert factory.digest(Path(factory.__file__).read_bytes()) == g['factory_SHA256']
    assert factory.R == F.R and factory.ROM == F.ROM and factory.PIN == F.PIN
    raw = factory.ROM.read_bytes()
    before = check(factory.ROM)
    assert factory.digest(raw) == factory.PIN == g['ROM_SHA256']
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    assert (OUT/'candidate.nes').read_bytes() == raw
    text = factory.controller(raw, kind)
    assert factory.digest(text.encode()) == g['Lua_SHA256']
    Storage.preflight(private_root=OUT, reserved_bytes=0, reserved_files=0, fresh=True)
    require_free_workspace(F.R, F.ROM, allow_interactive=True)
    script = OUT/'controller.lua'
    script.write_bytes(text.encode())
    q = run(script, F.ROM, OUT/'capture', F.PIN, 240)
    assert F.ROM.read_bytes() == (OUT/'candidate.nes').read_bytes() == raw and check(F.ROM) == before
    assert not q['images'] and q['outputs_written'] == 0 and q['script_SHA256'] == g['Lua_SHA256']
    report = {k: v for k, v in q.items() if k not in ('images', 'receipt', 'capture_preflight')}
    report.update(receipt=compact(q['receipt']), actual_Downloads=True)
    print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
    assert q['passed'], 'Retain the actual native negative before changing controls'
    assert not q['receipt']['game_state_writes'] and q['receipt']['gameplay_seeds'] == 0


if __name__ == '__main__':
    main()
