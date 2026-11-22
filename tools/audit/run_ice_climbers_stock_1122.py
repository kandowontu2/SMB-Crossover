"""Play the Ice Climbers' authored World 1-1 pickups in the shared Mesen slot."""

import argparse
from hashlib import sha256
import json

from capture_budget import preflight
from check_ff_stdout_controller_source_1110 import LuaRuntime
from current_ice_stock_binding_1122 import ROM, bindings
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from replay_sonic_hidden_life_f7c9_1116 import value
from run_stdout_mesen_1110 import R, run


OUT = R / 'build/smb2-flag-native-1113'
BASE = R / 'tools/playthroughs/ice_climbers_11_v2.lua'
POLICY = R / 'tools/playthroughs/ice_climbers_stock_1122.lua'
OBSERVER = R / 'tools/audit/ice_climbers_stock_observer_1122.lua'
BASE_DIGEST = 'd398f858397db6a357cbd4911fda228a7794d4600b6e687adf102e80e674c2c9'


def controller(raw, form, mode):
    config = dict(bindings(raw, form, '1up' if mode == 'life' else 'star'))
    hook_names = ['GameLoop', 'IcMovement', 'HandlePowerUpCollision', 'PlayerHeadCollision']
    if mode == 'life':
        hook_names.append('LifeCredit')
    config['hooks'] = {name: config['hooks'][name] for name in hook_names}
    original = BASE.read_bytes()
    assert sha256(original).hexdigest() == BASE_DIGEST
    policy = POLICY.read_text(encoding='utf-8')
    config['route'] = mode
    config['base_policy_SHA256'] = BASE_DIGEST
    config['stock_policy_SHA256'] = sha256(policy.encode()).hexdigest()
    lines = (
        'local C=' + value(config),
        'local ICE_STOCK_MODE=' + value(mode),
        'local ICE_STOCK_BASE=(function()\n' + original.decode('utf-8') + '\nend)()',
        'local choose=(function()\n' + policy + '\nend)()',
        OBSERVER.read_text(encoding='utf-8'),
    )
    script = '\n'.join(lines)
    LuaRuntime().compile(script)
    return script


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('flower-star', 'life'))
    parser.add_argument('--form', choices=('popo', 'nana', 'both'), default='both')
    args = parser.parse_args()
    before = check(ROM)
    raw = ROM.read_bytes()
    rom, script = OUT / 'candidate.nes', OUT / 'controller.lua'
    assert {p.name for p in OUT.iterdir()} == {rom.name, script.name}
    assert rom.read_bytes() == raw
    preflight(OUT / 'capture', reserved_files=0)
    require_free_workspace(R, ROM, allow_interactive=True)
    previous = script.read_bytes()
    forms = ('popo', 'nana') if args.form == 'both' else (args.form,)
    failed = []
    try:
        for form in forms:
            script.write_bytes(controller(raw, form, args.mode).encode())
            result = run(script, ROM, OUT / 'capture', before['ROM_sha256'], 155)
            assert result['outputs_written'] == 0 and not result['images']
            receipt = result['receipt']
            summary = {key: receipt[key] for key in (
                'passed', 'reason', 'form', 'route', 'physical_frames', 'difficulty',
                'items', 'head', 'phase', 'terminal', 'tail', 'movement_updates',
            )}
            summary.update(receipt=result['receipt_SHA256'], script=result['script_SHA256'])
            print('ICE STOCK '+json.dumps(summary, separators=(',', ':')), flush=True)
            if not result['passed']:
                failed.append(form)
    finally:
        script.write_bytes(previous)
        assert ROM.read_bytes() == raw and check(ROM) == before
    return bool(failed)


if __name__ == '__main__':
    raise SystemExit(main())
