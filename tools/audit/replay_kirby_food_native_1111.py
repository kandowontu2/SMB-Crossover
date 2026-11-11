"""Replay both earned Kirby food pickups on the installed nightly in Mesen."""

import argparse
import json
from pathlib import Path

import check_kirby_natural_food_1111 as Cpu
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import R, run


BASE = R / 'tools/playthroughs/kirby_current_inhale_stdout_1110_v3.lua'
TAIL = R / 'tools/playthroughs/kirby_food_native_1111.lua'


def controller(raw):
    authority = Cpu.Authority
    assert authority.sha(authority.AUTHORITY) == authority.AUTHORITY_ROM
    assert authority.sha(authority.AUTHORITY.with_suffix('.dbg')) == authority.AUTHORITY_DBG
    bundle = authority.scoped_load(authority.AUTHORITY)
    source = BASE.read_text(encoding='utf-8')
    config, source = source.split('\n', 1)
    ram = {name: Cpu.Host.address(bundle, name) for name in
           ('PowerUpType', 'KbFoodKind', 'KbHeal', 'KbFloat', 'FrameCounter',
            'EnemyMetasprite', 'Enemy_SprAttrib')}
    hooks = {}
    for name, symbol in (('birth', 'UnionPwrUpCore'), ('heal', 'KbHealPickup'),
                         ('injury', 'KbInjuryStart'), ('draw', 'DrawPowerUp::Exit')):
        at = Cpu.Host.location(bundle, symbol)
        assert raw[at:at+4] == bundle['raw'][at:at+4], symbol
        hooks[name] = dict(pc=Cpu.Host.address(bundle, symbol), offset=at-16, bytes=list(raw[at:at+4]))
    at = Cpu.Host.location(bundle, 'DrawPowerUp::PowerUpGfxTable')
    assert raw[at:at+2] == bundle['raw'][at:at+2] == bytes((0x41, 0x40))
    common = source[source.index('local function r('):source.index('local function finish(')]
    bindings = source[source.index('local function guarded('):source.index("hook('init'")]
    frontend = source[source.index('local function wait('):source.index('emu.addEventCallback(')]
    parts = (config, 'C.hooks=' + authority.lua(hooks), 'C.foodGfx=' + authority.lua(list(raw[at:at+2])),
             'for key,value in pairs(' + authority.lua(ram) + ') do C.ram[key]=value end',
             TAIL.read_text(encoding='utf-8').replace('-- COMMON', common)
             .replace('-- BINDINGS', bindings).replace('-- FRONTEND', frontend))
    return '\n'.join(parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expected', default=Cpu.STEVE_MOVE_PIN)
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(R / 'build') and output != R / 'build'
    assert check(Cpu.ROM)['ROM_sha256'] == args.expected
    output.mkdir(exist_ok=True)
    script = output / 'controller.lua'
    script.write_text(controller(Cpu.ROM.read_bytes()), encoding='utf-8', newline='\n')
    result = run(script, Cpu.ROM, output / 'capture', args.expected, 120)
    print(json.dumps(result, sort_keys=True), flush=True)
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
