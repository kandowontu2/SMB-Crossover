"""Replay Prince pipe controls through the real MMC5 menu and stage."""

import argparse
import json

import check_prince_pipe_controls_1123 as Replay
import compose_prince_pipe_play_1124 as Build
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_sonic_current_empty_cadence_1122 import SHARED
from run_stdout_mesen_1110 import run


RECEIPTS = {
    'ordinary': 'bd89980d91523ce91c98997b1a2c5a9f23ba8ba01ec0ff5a66a70b31b9296888',
    'mixed': '2ae620db984f43ba7a3ec1df27c8be86c3a77a0a646d0bd8b70821a8f628954f',
    'fourth': '74cf97e103a0b25a2f6ddb5e07f89312c766e85ab8a3cd4fcf402b334faf7ac9',
    'stage': 'b078d33853f3dc872d9416ae462ac79165cb176be44d50ce646cd0859ad83e6a',
}


FIRST_PIPE = """
local function probeTick(s)
 local age=commits-changedAt
 local left,right=capFeet(s,448,176)
 local standing=(left or right) and s.action~=10 and s.mode~=2 and s.mode~=6
 local dir=returning and 2 or 1
 if not probe.initial then probe.initial=probeState(s) end
 if progress=='usability-up' and age<=64 and #probe.samples<140 then
  probe.samples[#probe.samples+1]=probeState(s)
 end
 if progress=='usability-approach' then
  if returning and s.x<498 or not returning and s.x>=426 then
   probe.contact=probeState(s);switch('usability-brake',0)
  end
 elseif progress=='usability-brake' and idle(s) and floor(s) then
  probe.brake=probeState(s);switch('usability-up',approachPad(dir))
 elseif progress=='usability-up' and s.action==10 and not probe.pause then
  probe.first_climb=probeState(s);probe.pause=true;switch('usability-release',0)
 elseif progress=='usability-release' and age>=12 then
  probe.resume=probeState(s);switch('usability-up',approachPad(dir))
 elseif progress=='usability-up' and probe.first_climb and
   (standing or s.action==10 and idle(s) and s.y<145) then
  switch('usability-land',0)
 elseif progress=='usability-land' and standing and idle(s) then
  probe.cap=probeState(s);switch('usability-deck',0)
 elseif progress=='usability-deck' then
  if not standing then
   final=probeState(s);finish(false,'Pipe top lost support while waiting');return
  end
  if age>=20 and idle(s) then
   probe.rest=probeState(s);probe.previous_x=s.x;switch('usability-walk',dir)
  end
 elseif progress=='usability-walk' then
  local delta=s.x-probe.previous_x
  probe.previous_x=s.x
  probe.min_dx=math.min(delta,probe.min_dx or delta)
  probe.max_dx=math.max(delta,probe.max_dx or delta)
  if (returning and s.x<=429 or not returning and s.x>=496) and floor(s) and support(s) then
   final=probeState(s)
   local passed=s.hp==probe.initial.hp and s.lives==probe.initial.lives
    and (returning and probe.min_dx>=-16 and probe.max_dx<=4
      or not returning and probe.min_dx>=-4 and probe.max_dx<=16)
   if passed and not returning then
    returning=true
    probe.outbound={contact=probe.contact,brake=probe.brake,first_climb=probe.first_climb,
     resume=probe.resume,cap=probe.cap,rest=probe.rest,landing=final}
    probe.pause=false;probe.first_climb=nil;probe.cap=nil
    probe.min_dx=nil;probe.max_dx=nil
    switch('usability-approach',2);return
   end
   finish(passed,'Walk, Up climb, release, stand and walk off both directions');return
  end
 end
 if age>=140 then
  final=probeState(s);finish(false,'Timed out in '..progress);return
 end
end
"""


def cap_geometry(raw, entry):
    from py65.devices.mpu6502 import MPU

    (_, _, _, private), _, _, _ = Build.Pipe.extract(raw)
    cap = 0x300 + 0xD0 + 112 + 9
    defaults = {0x75: 147, 0x5C: 3, 0xBD: 112, 0xA4: 1,
                0xC084: 146, 0xC60F: 155, 0xC610: 3, 0xC616: 1,
                0xC618: 1, 0x95D9: 0xD0, cap: 0x10, cap + 1: 0x11, 0x015A: 0x60}
    fixtures = (
        ('both feet', {}, None),
        ('left foot', {0x75: 168}, None),
        ('right foot', {0x75: 136}, None),
        ('projected two pixels below cap', {0xBD: 114}, None),
        ('beyond the right edge', {0x75: 175}, 0xA7AB),
        ('air column', {cap: 0, cap + 1: 0}, 0xA7AB),
        ('ordinary floor', {cap: 0x54, cap + 1: 0x54}, 0xA7AB),
        ('pipe shaft', {cap: 0x14, cap + 1: 0x15}, 0xA7AB),
        ('covered cap', {cap - 16: 0x54, cap + 1 - 16: 0x54}, 0xA7AB),
        ('foot four pixels below cap', {0xC084: 148}, 0xA7AB),
        ('existing fall', {0xC616: 7}, 0xA7C2),
    )
    for name, changes, destination in fixtures:
        memory = bytearray(65536)
        memory[0xA000:0xA000 + len(private)] = private
        attributes = 16 + 127 * 8192 + (0xEF36 & 8191)
        memory[0xEF36:0xF036] = raw[attributes:attributes + 256]
        for address, value in (defaults | changes).items():
            memory[address] = value
        cpu = MPU(memory=memory, pc=entry)
        cpu.x, cpu.y, cpu.sp = 51, 93, 224
        cpu.stPushWord(0x5AFF)
        calls = []
        for _ in range(250):
            if cpu.pc == 0x5B00:
                break
            if cpu.pc == 0x015A:
                assert cpu.a == 3
                calls.append(memory[0x16C] | memory[0x16D] << 8)
            assert memory[cpu.pc], (name, hex(cpu.pc))
            cpu.step()
        else:
            raise AssertionError((name, hex(cpu.pc)))
        assert (cpu.x, cpu.y, cpu.sp) == (51, 93, 224), name
        assert calls == ([destination] if destination else []), (name, calls)
    return len(fixtures)


def first_pipe(raw, mixed=False):
    text = Replay.controller(raw, 9)
    start = text.index('local function probeTick(s)')
    end = text.index('local function laterTick(s)', start)
    buttons = 'return 136|dir' if mixed else 'return 8'
    local = f'local returning=false\nlocal function approachPad(dir) {buttons} end\n'
    text = text[:start] + local + FIRST_PIPE + text[end:]
    Replay.Original.LuaRuntime().compile(text)
    return text


def script_for(name, raw, baseline):
    if name == 'stage':
        return Replay.stage_controller(raw, baseline, Build.static_extents(raw))
    if name == 'fourth':
        text = Replay.later_pipe_controller(raw, 4, baseline, Build.static_extents(raw))
        text = text.replace('if audit.pipe==3 then pad=0 end', 'pad=0', 1)
        old = ' local floorClear=audit.pipe~=3'
        assert text.count(old) == 1
        text = text.replace(old, ''' if audit.cap and commits-audit.cap.commit==20 then
  audit.rest=s
  if not (leftFoot or rightFoot) or not idle(s) then
   final=s;finish(false,'Fourth pipe top lost support while waiting');return
  end
  pad=1
 end
 local floorClear=audit.pipe~=3''', 1)
        Replay.Original.LuaRuntime().compile(text)
        return text
    return first_pipe(raw, mixed=name == 'mixed')


def native(raw, baseline, names, install=False):
    rom = Replay.ROM
    installed = rom.read_bytes()
    assert installed == baseline
    candidate, script = SHARED / 'candidate.nes', SHARED / 'controller.lua'
    assert set(SHARED.iterdir()) == {candidate, script} and candidate.read_bytes() == installed
    assert check(rom)['ROM_sha256'] == Build.H(installed)
    if install:
        assert tuple(names) == tuple(RECEIPTS), 'Run every qualified replay for Downloads delivery'
    require_free_workspace(Replay.Original.R, rom, allow_interactive=True)
    script_before = script.read_bytes()
    delivered = False
    results = {}
    try:
        candidate.write_bytes(raw)
        if install:
            rom.write_bytes(raw)
            guard = check(rom)
            assert guard['ROM_sha256'] == Build.H(raw)
        for name in names:
            script.write_bytes(script_for(name, raw, baseline).encode())
            result = run(script, rom if install else candidate, SHARED / 'capture', Build.H(raw),
                         320 if name == 'stage' else 135, variant=3, long_no_capture=True)
            assert not result['images'] and result['outputs_written'] == 0
            receipt = result['receipt']
            report = {key: receipt[key] for key in ('passed', 'reason', 'terminal')}
            if name in ('ordinary', 'mixed'):
                probe = receipt['later_route']['usability']
                report['controls'] = {key: probe[key] for key in
                                      ('contact', 'brake', 'first_climb', 'resume', 'cap',
                                       'rest', 'outbound', 'min_dx', 'max_dx') if key in probe}
                if not receipt['passed']:
                    report['samples'] = [[s['commit'], s['x'], s['y'], s['action'], s['mode'],
                                          s['pose'], s['source_pad']] for s in probe['samples'][::8]]
            elif name == 'fourth':
                report['controls'] = receipt['later_route']['pipe_audit']
            elif name == 'stage':
                report.update({key: receipt[key] for key in
                               ('grounded_1_2_completed_returns', 'persistent_sword') if key in receipt})
            report['receipt_SHA256'] = result['receipt_SHA256']
            results[name] = report
            print(json.dumps({name: compact(report)}, ensure_ascii=True), flush=True)
            if install:
                assert report['passed'] and report['receipt_SHA256'] == RECEIPTS[name], name
        if install:
            assert rom.read_bytes() == raw and check(rom)['ROM_sha256'] == Build.H(raw)
            delivered = True
            print(f'Delivered {rom}', flush=True)
        return results
    finally:
        if install and not delivered:
            rom.write_bytes(installed)
        if not delivered:
            candidate.write_bytes(installed)
        script.write_bytes(script_before)


def compact(value):
    if isinstance(value, dict):
        if 'x' in value and 'y' in value:
            return {key: value[key] for key in ('x', 'y', 'hp', 'lives', 'commit', 'action',
                                                'mode', 'facing', 'wall_timer') if key in value}
        return {key: compact(item) for key, item in value.items()
                if key not in ('after_cap', 'tiles', 'corrections')}
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tests', nargs='+', choices=tuple(RECEIPTS))
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    parent = Replay.ROM.read_bytes()
    rom, info = Build.compose(parent)
    assert Build.inverse(rom) == parent
    info['cap_fixtures'] = cap_geometry(rom, info['support'])
    print(json.dumps(dict(ROM=Build.H(rom), **info)), flush=True)
    checks = native(rom, parent, args.tests, args.install)
    raise SystemExit(0 if all(item['passed'] for item in checks.values()) else 1)
