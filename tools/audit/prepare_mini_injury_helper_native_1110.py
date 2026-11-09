"""Prepare a bounded, controller-only Mini helper regression during injury."""

import argparse
import json
from pathlib import Path
import re
import sys

from observe_chip_committed_write import lua
from prepare_selected_native_packet_v1 import R, prepare, sha


POWER = R / 'build/mini-helper-activation-native-1110/native/power/controller.lua'
OBSERVER = R / 'tools/reference/mini_injury_helper_native_1110.lua'
LUA = R / 'build/smb2-final62-observer-lua-deps-v1'
CODE_OFFSET = 16 + 128 * 8192 + 962 * 1024
BOX = "observe_return('MiniHostBox',"
BOX_END = '\nlocal latestDraw,checkedTiles'
CONSTRUCTOR = '-- Observe constructor ingress after the real actor fields are published.'
POWER_ROUTE = '-- Reuse qualified initial enemy avoidance'
PROFILER = '-- This observer is appended to the controller so it can share its phase and'
PRG_HOOK = re.compile(r'\["physical"\]=(\d+),\["memory"\]="nesPrgRom",\["bytes"\]=\{([\d,]+)\}')
KERNEL_HOOK = re.compile(
    r'\{\["name"\]="(Mini\w+)",\["pc"\]=\d+,\["physical"\]=\d+,'
    r'\["memory"\]="nesWorkRam",\["bytes"\]=\{[\d,]+\}\}')


def unique(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def bound_template(path):
    ready_path = path.with_name('ready.json')
    ready = json.loads(ready_path.read_text(encoding='utf-8'))
    assert ready['prepared'] and not ready['emulated_writes'], path
    assert ready['bindings'][str(path.resolve())] == sha(path), path
    return path.read_text(encoding='utf-8'), ready_path, ready


def prg_hook(raw, name, bank, pc):
    at = bank * 8192 + (pc & 8191)
    return dict(name=name, pc=pc, physical=at, memory='nesPrgRom',
                bytes=list(raw[16 + at:20 + at]))


def rebind_kernel(text, kernel, labels):
    def relink(match):
        name = match[1]
        pc = labels[name]
        opcodes = kernel[pc - 0xa000:pc - 0xa000 + 4]
        assert len(opcodes) == 4, name
        return lua(dict(name=name, pc=pc, physical=pc - 0x4000,
                        memory='nesWorkRam', bytes=list(opcodes)))

    return KERNEL_HOOK.sub(relink, text)


def build_controller(raw, kernel, labels, route, power, rom_hash, kernel_hash, hunt_x):
    source = route[:route.index(PROFILER)]
    source = re.sub(r'(\["ROM_sha256"\]=")[0-9a-f]{64}(")',
                    rf'\g<1>{rom_hash}\2', source, count=1)
    source = re.sub(r'(\["kernel_SHA256"\]=")[0-9a-f]{64}(")',
                    rf'\g<1>{kernel_hash}\2', source, count=1)
    assert f'["ROM_sha256"]="{rom_hash}"' in source
    assert f'["kernel_SHA256"]="{kernel_hash}"' in source
    powered_box = power[power.index(BOX):power.index(BOX_END)]
    assert 'c256)==(top&255)' in powered_box
    source = source[:source.index(BOX)] + powered_box + source[source.index(BOX_END):]

    prefix = power[power.index('for k,v in pairs({["PlayerStatus"]'):
                   power.index('local function result(ok,why)')]
    prefix = unique(prefix, 'C.max_frames=9000', 'C.max_frames=4500')
    prefix += 'local injury={native_steps={},post_control={},approach={}}\n'
    source = unique(source, 'local profileFinish\n', prefix + 'local profileFinish\n')
    source = unique(source, '  native_end_handoff=end_native,',
                    '  earned_power=power,injury_helper=injury,native_end_handoff=end_native,')
    epoch = ' if lastEpoch then check(((s.epoch-lastEpoch)&255)==1,'
    source = unique(source, epoch,
        ' if power.reset_epoch or injury.reset_epoch then lastEpoch=nil;'
        'power.reset_epoch=false;injury.reset_epoch=false end\n' + epoch)
    source = unique(source, "shot('mini-active-1-2');audioAssertFinished();result(true);",
                    "check(injury.completed,'Focused native injury result is complete');"
                    "shot('mini-injury-helper');result(true);")
    source = unique(source, "print('PASS Mini actual nonshortcut1-1')",
                    "print('PASS Mini helper scrolls in during native powered injury')")

    constructor = route[route.index(CONSTRUCTOR):route.index('local beforeCameraFinish=')]
    constructor = unique(constructor, 'relative_x=relative}',
        'relative_x=relative,right=camera+255,engine=r("GameEngineSubroutine"),timer=r("TimerControl")}'
        '\n if x==864 then injury.constructor=camera_lift_spawns[x] end')
    earned = power[power.index(POWER_ROUTE):]
    earned = unique(earned, "power_snapshot('earned-powered-body-complete');transition('finish')",
                    "power_snapshot('earned-powered-body-complete')")
    # The powered pickup observer owns input only until its ten actual
    # powered samples pass. The injury observer then delegates to the stage.
    hook_config = dict(hunt_x=hunt_x,
                       force=prg_hook(raw, 'ForceInjury', 126, 0x9771),
                       native_control=prg_hook(raw, 'PlayerInjuryBlink control', 1, 0xa47d),
                       post_control=prg_hook(raw, 'Native pre-enemy phase', 126, 0x83c4))
    assert hook_config['native_control']['bytes'][0] == 0x4c
    assert hook_config['post_control']['bytes'][:3] == [0x20, 0x7b, 0x83]
    result = (source + '\n' + constructor + '\n' + earned + '\nlocal injuryConfig='
              + lua(hook_config) + '\n' + OBSERVER.read_text(encoding='utf-8'))
    result = rebind_kernel(result, kernel, labels)
    assert 'emu.setInput(keys,0)' in result and '0x474f' in result
    assert not any(token in result for token in ('emu.write(', 'emu.reset(', 'emu.loadSavestate('))
    assert len(PRG_HOOK.findall(result)) >= 12
    for physical, values in PRG_HOOK.findall(result):
        at = 16 + int(physical)
        want = bytes(map(int, values.split(',')))
        assert raw[at:at + len(want)] == want, (hex(at), want.hex())
    return result


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--rom', type=Path, required=True)
    cli.add_argument('--kernel', type=Path, required=True)
    cli.add_argument('--controller', type=Path, required=True)
    cli.add_argument('--output', type=Path, required=True)
    cli.add_argument('--validate-only', action='store_true')
    cli.add_argument('--hunt-x', type=int, default=650,
                     help='Begin the right-only side-hit approach after crossing the X608 pipe')
    args = cli.parse_args()
    assert 648 <= args.hunt_x <= 712
    rom, kernel, controller = (p.resolve() for p in (args.rom, args.kernel, args.controller))
    route, route_ready, route_meta = bound_template(controller)
    power, power_ready, _ = bound_template(POWER)
    raw, kernel_bytes = rom.read_bytes(), kernel.read_bytes()
    rom_meta_path = rom.with_suffix('.json')
    rom_meta = json.loads(rom_meta_path.read_text(encoding='utf-8'))
    expected = rom_meta['candidate_SHA256']
    assert sha(rom) == expected
    assert raw[:5] == b'NES\x1a\x40' and not raw[6] & 4
    assert len(kernel_bytes) == 5120 and raw[CODE_OFFSET:CODE_OFFSET+5120] == kernel_bytes
    kernel_hash = sha(kernel)
    assert rom_meta['kernel_SHA256'] == kernel_hash
    kernel_labels = kernel.with_suffix('.lbl')
    labels = {name: int(pc, 16) for pc, name in re.findall(
        r'^al ([0-9A-F]+) \.(\w+)$', kernel_labels.read_text(), re.M)}
    text = build_controller(raw, kernel_bytes, labels, route, power, expected, kernel_hash, args.hunt_x)
    sys.path.insert(0, str(LUA))
    from lupa.lua54 import LuaRuntime

    assert LuaRuntime().eval('function(s) local f,e=load(s); assert(f,e); return true end')(text)
    if args.validate_only:
        print(json.dumps(dict(validated=True, ROM_sha256=expected, controller_bytes=len(text.encode()))))
        return
    refs = {Path(__file__), OBSERVER, controller, route_ready, POWER, power_ready,
            rom_meta_path, kernel, kernel_labels}
    prepare(args.output, rom, text, refs, expected=expected, timeout=180,
            allow_interactive=route_meta['allow_interactive'],
            scope='Actual menu and earned mushroom, first helper crossing, then powered native side injury. '
                  'Requires the X864 native lift to construct while the mode10 camera still leaves it '
                  'offscreen, followed by visible entry during the same injury. Controller input only.')


if __name__ == '__main__':
    main()
