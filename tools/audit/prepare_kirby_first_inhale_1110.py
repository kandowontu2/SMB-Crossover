"""Bind a controller-only first-enemy Kirby test to the published 29aa ROM."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

from prepare_kirby_contacts_current_1108_v1 import (
    AUTHORITY, AUTHORITY_DBG, AUTHORITY_ROM, LUA_DEPS, SLOT, address, location,
    lua, menu_routes, scoped_load,
)
from prepare_selected_native_packet_v1 import R, prepare, sha


ROM = R / 'build/mini-shared-game-loop-tail-native-1110/candidate.nes'
PIN = '29aa4f8df07425dfe6dcdaaa431421c78347adbca5979c332edce69c79367cf5'
CONTROLLER = R / 'tools/playthroughs/kirby_first_inhale_1110.lua'
LEVEL = R / 'src/level_tiles.s'
STREAM = bytes.fromhex('1ec2006b068b8663b70f05030623064bb7bb005bb7fb373bb70f0b1b37ff')
RAM = '''CrossoverTitleDrawn CrossoverMenuState CrossoverMenuIndex CrossoverBehaviorVersion
CheatStartLevel CheatInvincible DisableScreenFlag OperMode OperMode_Task GameEngineSubroutine
WorldNumber LevelNumber AreaType AreaAddrsLOffset NumberofLives TimerControl KbVariant KbHealth
KbCopy KbMouth KbMouthCopy KbAction KbActionAge KbFresh KbFloat KbHurt InjuryTimer PlayerFacingDir
Player_PageLoc Player_X_Position Player_Y_Position Player_State ScreenRight_PageLoc ScreenRight_X_Pos
SavedJoypadBits Enemy_Flag Enemy_ID Enemy_State Enemy_PageLoc Enemy_X_Position Enemy_Y_Position
Enemy_Y_HighPos'''.split()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert sha(ROM) == PIN and sha(AUTHORITY) == AUTHORITY_ROM
    assert sha(AUTHORITY.with_suffix('.dbg')) == AUTHORITY_DBG
    source, target = scoped_load(AUTHORITY), scoped_load(ROM)
    raw = target['raw']
    assert raw.count(STREAM) == 1 and raw.find(STREAM) == 19023
    level = LEVEL.read_text().split('E_GroundArea6:\n', 1)[1].split('\n\n', 1)[0]
    assert bytes.fromhex(' '.join(part[1:] for part in level.replace(',', ' ').split()
                                  if part.startswith('$'))) == STREAM
    ram = {name: address(source, name) for name in RAM}
    for name, value in ram.items():
        if name in target['syms']:
            assert address(target, name) == value, name

    owners = {}
    for name in ('KbWeapons', 'KbBodyContact', 'KbMovement', 'KbInputs', 'KbInjuryStart'):
        at = location(source, name)
        size = int(source['syms'][name]['size'], 0)
        data = raw[at:at + size]
        assert size > 0 and data == source['raw'][at:at + size], name
        owners[name] = dict(offset=at, size=size, sha256=hashlib.sha256(data).hexdigest())

    def hook(name, count, delta=0):
        at = location(source, name) + delta
        data = raw[at:at + count]
        assert data == source['raw'][at:at + count], name
        return dict(pc=address(source, name) + delta, offset=at - 16, bytes=list(data))

    capture, next_slot = (location(source, f'KbWeapons::{label}')
                          for label in ('Capture', 'PullNext'))
    erase = address(source, 'EraseEnemyObject')
    call = bytes([0x20, erase & 255, erase >> 8])
    leaf = raw[capture:next_slot]
    assert leaf.count(call) == 1
    after_erase = leaf.index(call) + len(call)
    hooks = dict(init=hook('InitGoomba', 6), inhale=hook('KbWeapons::Inhale', 9),
                 capture=hook('KbWeapons::Capture', 13), erased=hook('KbWeapons::Capture', 5, after_erase),
                 injury=hook('KbInjuryStart', 3))
    source['raw'] = raw
    edges, routes = menu_routes(source, 0)
    assert SLOT == 12
    navigation = [routes[i][0] if routes[i] else '' for i in sorted(edges)]
    text = 'local C=' + lua(dict(sha=PIN, ram=ram, hooks=hooks, menu=navigation, slot=SLOT)) + '\n'
    text += CONTROLLER.read_text(encoding='utf-8')
    for banned in ('emu.write', 'emu.setState', 'emu.loadSavestate'):
        assert banned not in text, banned
    sys.path.insert(0, str(LUA_DEPS))
    from lupa.lua54 import LuaRuntime
    ok, error = LuaRuntime(unpack_returned_tuples=True).eval(
        'function(s) local f,e=load(s); return f~=nil,e end')(text)
    assert ok, error
    prepare(args.output, ROM, text, [Path(__file__), CONTROLLER, LEVEL, AUTHORITY,
                                    AUTHORITY.with_suffix('.dbg')], expected=PIN,
            timeout=160, allow_interactive=True,
            scope='Easy Kirby 1-1. Natural first Goomba constructor, fresh forward inhale, '
                  'actual capture and erase with full health and both lives. Prepared only.')
    ready = args.output / 'ready.json'
    receipt = json.loads(ready.read_text())
    receipt.update(menu_direction_cases=len(edges) * 4, menu_route_from_zero=routes[0],
                   exact_owners=owners, hooks=hooks, original_enemy_stream_offset=19023,
                   original_enemy_stream=STREAM.hex(), natural_first_goomba_x=352,
                   authored_green_koopa_x=1712, authored_red_koopa=False)
    ready.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
