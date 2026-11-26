"""Exercise the opening coin block and early pipe climb landings in MMC5."""

import argparse
import json

import check_prince_pipe_play_1124 as Pipes
import compose_prince_ledge_landing_1124 as Build


INSTALL_TESTS = ('224', '405', 'ordinary', 'fourth', 'stage')


LEDGE_ROUTE = """
local ledge={left=@LEFT@,top=@TOP@,trace={}}
late.ledge=ledge
local function ledgeState(s)
 s.before=source(0x86)+256*source(0x87)
 s.source_x=source(0x60f)+256*source(0x610)
 s.align=source(0x7d)+256*source(0x7e)
 s.material=source(0x9f)
 s.surface=source(0x7f)+256*source(0x80)
 s.point_x=source(0x1369,3)+256*source(0x136a,3)
 s.point_y=source(0x136b,3)
 s.tile=tile(ledge.left,ledge.top)
 s.feet={tile(s.x+2,ledge.top),tile(s.x+13,ledge.top)}
 s.coins=read(0x75e)
 return s
end
local function onLedge(s)
 local function foot(x)
  return x>=ledge.left and x<ledge.left+@WIDTH@ and solid(x,ledge.top)
 end
 return math.abs(s.y+32-ledge.top)<=1 and support(s) and (foot(s.x+2) or foot(s.x+13))
end
local function ledgeTick(s)
 local age=commits-changedAt
 if age>=250 then final=ledgeState(s);finish(false,'Timeout in '..progress);return end
 if progress=='ledge-approach' and s.x>=@BRAKE@ then
  ledge.brake=ledgeState(s);switch('ledge-settle',0)
 elseif progress=='ledge-settle' and idle(s) and floor(s) then
  ledge.approach=ledgeState(s);switch('ledge-climb',8)
 elseif progress=='ledge-climb' then
  if s.action==10 and not ledge.climb then
   ledge.climb=ledgeState(s)
   pad=0
  end
  if ledge.climb and (s.action~=10 or commits-ledge.climb.commit>=54) and #ledge.trace<64 then
   ledge.trace[#ledge.trace+1]=ledgeState(s)
  end
  if ledge.climb and s.action==49 then
   ledge.recovery_y=math.max(ledge.recovery_y or s.y,s.y)
  end
  if ledge.climb and s.action~=10 and onLedge(s) and idle(s) then
   ledge.stand=ledgeState(s);switch('ledge-rest',0)
  elseif ledge.climb and commits-ledge.climb.commit>=60 and floor(s) then
   final=ledgeState(s);finish(false,'Prince fell to the ground after climbing');return
  end
 elseif progress=='ledge-rest' then
  if not onLedge(s) then
   final=ledgeState(s);finish(false,'Prince slipped off after climbing');return
  end
  if age>=20 then final=ledgeState(s);finish(true,'Stable ledge landing');return end
 end
end
"""


def ledge_controller(raw, brake, reverse=False):
    pipe = brake >= 400
    text = Pipes.Replay.controller(raw, 9)
    before = 'local function laterTick(s)'
    assert text.count(before) == 1
    route = LEDGE_ROUTE.replace('@BRAKE@', str(brake))
    if reverse:
        route = route.replace(f's.x>={brake}', f's.x<={brake} and s.facing==0')
    for token, value in zip(('@LEFT@', '@TOP@', '@WIDTH@'), (448, 176, 32) if pipe else (256, 144, 16)):
        route = route.replace(token, str(value))
    text = text.replace(before, route + before, 1)
    before = "  if progress:sub(1,10)=='usability-'then"
    assert text.count(before) == 1
    text = text.replace(before, "  if progress:sub(1,6)=='ledge-'then ledgeTick(s);return end\n" + before, 1)
    if pipe:
        before = "switch('usability-approach',1)"
        assert text.count(before) == 2
        text = text.replace(before, "switch('ledge-approach',1)")
    elif reverse:
        before = "if s.x>=400 then switch('usability-approach',1) else switch('approach',1) end"
        assert text.count(before) == 1
        text = text.replace(before, "switch('ledge-approach',2)", 1)
    else:
        before = "    switch('approach',1)"
        assert text.count(before) == 1
        text = text.replace(before, "    switch('ledge-approach',1)", 1)
    Pipes.Replay.Original.LuaRuntime().compile(text)
    return text


def check_support(raw):
    from py65.devices.mpu6502 import MPU

    (_, _, _, private), _, _, _ = Build.Pipe.extract(raw)
    _, _, _, labels, _ = Build.worker(raw)
    x = 243
    tile = 0x300 + 0xD0 + 112
    floor = {0x75: x, 0x5C: 0, 0xBD: 112, 0xC084: 145, 0xC086: 145,
             0x95D9: 0xD0, tile: 0xC4, 0xC080: 1}
    cases = (
        ('used block under right foot', {}, True),
        ('used block under left foot', {0x75: 10, 0x5C: 1}, True),
        ('live power-up block', {tile: 0xC1}, True),
        ('pipe cap', {tile: 0x13}, True),
        ('ordinary brick', {tile: 0x51}, True),
        ('lower projection', {0xBD: 114, 0xC084: 147, 0xC086: 146}, True),
        ('unprojected sole', {0xC084: 144, 0xC086: 144}, True),
        ('clear edge', {0x75: 242}, False),
        ('shaft', {tile: 0x15}, False),
        ('coin', {tile: 0xC2}, False),
        ('axe', {tile: 0xC5}, False),
        ('covered block', {tile - 16: 0x51}, False),
        ('deep crossing', {0xC084: 148}, False),
        ('previous sole was airborne', {0xC086: 143}, False),
    )
    for name, changes, expected in cases:
        memory = bytearray(65536)
        memory[0xA000:0xA000 + len(private)] = private
        attr = 16 + 127 * 8192 + (0xEF36 & 8191)
        memory[0xEF36:0xF036] = raw[attr:attr + 256]
        for address, value in (floor | changes).items():
            memory[address] = value
        cpu = MPU(memory=memory, pc=labels['LedgeSupport'])
        cpu.x, cpu.y, cpu.sp = 51, 93, 224
        cpu.stPushWord(0x5AFF)
        for _ in range(225):
            if cpu.pc == 0x5B00:
                break
            cpu.step()
        else:
            raise AssertionError((name, hex(cpu.pc)))
        assert (cpu.x, cpu.y, cpu.sp) == (51, 93, 224), name
        assert cpu.a == (144 if expected else 0), (name, cpu.a)
        assert memory[0xC080] == (0 if expected else 1), name
    return len(cases)


def replay(script, path, raw, test, parent):
    if test in ('ordinary', 'mixed'):
        contents = Pipes.first_pipe(raw, mixed=test == 'mixed')
    elif test in ('stage', 'fourth', 'fourth-return'):
        base = Pipes.Build.inverse(parent)
        if test == 'stage':
            contents = Pipes.Replay.stage_controller(raw, base, Build.static_extents(raw))
        else:
            contents = pipe_four(raw, base, reverse=test == 'fourth-return')
    else:
        contents = ledge_controller(raw, int(test.removeprefix('right-')), test.startswith('right-'))
    script.write_bytes(contents.encode())
    return Pipes.run(script, path, Pipes.SHARED / 'capture', Build.H(raw),
                     320 if test == 'stage' else 135, variant=3, long_no_capture=True)


def pipe_four(raw, base, reverse=False):
    text = Pipes.Replay.later_pipe_controller(raw, 4, base, Build.static_extents(raw))
    text = text.replace('if audit.pipe==3 then pad=0 end', 'pad=0', 1)
    marker = ' local floorClear=audit.pipe~=3'
    assert text.count(marker) == 1
    text = text.replace(marker, """ if audit.cap and commits-audit.cap.commit==20 then
  audit.rest=s
  if not (leftFoot or rightFoot) or not idle(s) then
   final=s;finish(false,'Fourth pipe top lost support while waiting');return
  end
  pad=1
 end
 local floorClear=audit.pipe~=3""", 1)
    if reverse:
        marker = ' audit.approach=audit.approach or s'
        assert text.count(marker) == 1
        text = text.replace(marker, """ if audit.return_start then
  local left,right=capFeet(s,audit.left,audit.top)
  if not audit.return_climb and s.facing==0 and s.action==10 and s.x>=audit.left+16 then
   audit.return_climb=s;pad=0
  end
  if audit.return_climb and (left or right) and idle(s) then
   audit.return_rest=audit.return_rest or s
   if commits-audit.return_rest.commit>=20 then
    final=s;finish(s.hp==audit.return_start.hp and s.lives==initial.lives,'Reverse fourth-pipe landing');return
   end
  else
   audit.return_rest=nil
  end
  if commits-audit.return_start.commit>=400 then final=s;finish(false,'Reverse fourth-pipe timeout') end
  return
 end
""" + marker, 1)
        marker = "  finish(s.hp==audit.approach.hp and s.lives==initial.lives,'Pipe '..audit.pipe..' climbed using Up and Right')"
        assert text.count(marker) == 1
        text = text.replace(marker, '  audit.return_start=s;pad=10;return', 1)
    return text


def native(raw, installed, parent, tests, install=False):
    rom = Pipes.Replay.ROM
    assert Pipes.check(rom)['ROM_sha256'] == Build.H(installed)
    if install:
        assert tuple(tests) == INSTALL_TESTS
    Pipes.require_free_workspace(Pipes.Replay.Original.R, rom, allow_interactive=True)
    candidate, script = Pipes.SHARED / 'candidate.nes', Pipes.SHARED / 'controller.lua'
    assert set(Pipes.SHARED.iterdir()) == {candidate, script} and candidate.read_bytes() == installed
    before = script.read_bytes()
    delivered = False
    try:
        candidate.write_bytes(raw)
        if install:
            rom.write_bytes(raw)
            assert Pipes.check(rom)['ROM_sha256'] == Build.H(raw)
        for test in tests:
            info = replay(script, rom if install or raw == installed else candidate, raw, test, parent)
            assert not info['images'] and not info['outputs_written']
            receipt = info['receipt']
            result = dict(passed=info['passed'], reason=receipt['reason'], terminal=receipt['terminal'],
                          receipt_SHA256=info['receipt_SHA256'])
            ledge = receipt['later_route'].get('ledge')
            if ledge:
                result = report(dict(result, steps=ledge))
            else:
                result['terminal'] = Pipes.compact(result['terminal'])
            print(json.dumps({test: result}), flush=True)
            if install:
                assert result['passed'], test
                if test == '224':
                    assert ledge['approach']['tile'] == 0xC0 and ledge['stand']['tile'] == 0xC4
                    assert result['states']['terminal']['x'] == ledge['stand']['x']
                elif test == '405':
                    assert ledge['recovery_y'] <= ledge['top'] - 30
                elif test == 'stage':
                    assert receipt['grounded_1_2_completed_returns'] >= 25
                    assert receipt['persistent_sword']['Sword'] == 1
        if install:
            assert Pipes.check(rom)['ROM_sha256'] == Build.H(raw) and rom.read_bytes() == raw
            delivered = True
    finally:
        script.write_bytes(before)
        if not delivered:
            candidate.write_bytes(installed)
            if install:
                rom.write_bytes(installed)
    return delivered


def report(result):
    steps = result['steps']
    states = [('approach', steps.get('approach')), ('climb', steps.get('climb')),
              ('stand', steps.get('stand')), ('terminal', result['terminal'])]
    result = {key: result[key] for key in ('passed', 'reason', 'receipt_SHA256')}
    if 'recovery_y' in steps:
        result['max_recovery_y'] = steps['recovery_y']
    result['states'] = {key: Pipes.compact(state) | {field: state[field] for field in ('tile', 'coins') if field in state}
                        for key, state in states if state}
    fields = ('commit', 'x', 'y', 'action', 'mode', 'ground', 'foot', 'before', 'align',
              'source_x', 'point_x', 'point_y', 'material', 'surface', 'tile')
    if not result['passed']:
        trace = steps['trace']
        result['climb_exit'] = [tuple(row[key] for key in fields) for row in trace[::2]] if trace else []
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tests', nargs='+')
    parser.add_argument('--trial', action='store_true')
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    installed = Pipes.Replay.ROM.read_bytes()
    parent = Build.inverse(installed) if Build.H(installed) == Build.CANDIDATE else installed
    rom, used = Build.compose(parent) if args.trial or args.install else (installed, 0)
    if used:
        assert Build.inverse(rom) == parent
        print(json.dumps(dict(ROM_SHA256=Build.H(rom), packet_bytes=used,
                              linked_cases=check_support(rom))), flush=True)
    if native(rom, installed, parent, args.tests, args.install):
        print(f'Delivered {Pipes.Replay.ROM}', flush=True)
