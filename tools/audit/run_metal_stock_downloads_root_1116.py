"""Current Metal native Star or a frozen expected-negative life baseline."""
import argparse
import json
from pathlib import Path

import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run


def main():
    p = argparse.ArgumentParser()
    p.add_argument('kind', choices=('star', 'oneup'))
    kind = p.parse_args().kind
    if kind == 'star':
        import replay_metal_star_cell_7c0f_1116 as F
        name = 'metal-star-downloads-root-1116.json'
    else:
        import replay_metal_native_caps_7c0f_1116 as F
        name = 'metal-oneup-baseline-downloads-root-1116.json'
    out = F.R/'build/smb2-flag-native-1113'
    g = json.loads((F.R/'docs/qa/allocations'/name).read_bytes())
    assert g['native_Mesen_actual_Downloads_authorized'] and not g['ROM_replacement_authorized']
    assert F.digest(Path(F.__file__).read_bytes()) == g['factory_SHA256']
    before = check(F.ROM)
    raw = F.ROM.read_bytes()
    assert F.digest(raw) == F.PIN == g['ROM_SHA256']
    assert {q.name for q in out.iterdir() if q.is_file()} == {'candidate.nes', 'controller.lua'}
    assert (out/'candidate.nes').read_bytes() == raw
    text = F.controller(raw, kind)
    assert F.digest(text.encode()) == g['Lua_SHA256']
    Storage.preflight(private_root=out, reserved_bytes=0, reserved_files=0, fresh=True)
    require_free_workspace(F.R, F.ROM, allow_interactive=True)
    script = out/'controller.lua'
    script.write_bytes(text.encode())
    q = run(script, F.ROM, out/'capture', F.PIN, 240)
    assert F.ROM.read_bytes() == (out/'candidate.nes').read_bytes() == raw and check(F.ROM) == before
    assert q['outputs_written'] == 0 and not q['images'] and q['script_SHA256'] == g['Lua_SHA256']
    r = q['receipt']
    report = {k: v for k, v in q.items() if k not in ('images', 'capture_preflight')}
    report['actual_Downloads'] = True
    if kind == 'oneup':
        s = r.get('stock', {})
        ctor = s.get('earned_life_constructor', {})
        report['expected_failure_confirmed'] = bool(not q['passed'] and s.get('life_credit')
            and ctor.get('before', {}).get('armor') == 128 and ctor.get('after', {}).get('armor') == 0
            and r.get('terminal', {}).get('lives') == 3)
    print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
    if kind == 'star':
        assert q['passed']
    else:
        assert report['expected_failure_confirmed'], 'Do not substitute a different failure for the life-reset baseline'
    assert not r.get('game_state_writes', False)


if __name__ == '__main__':
    main()
