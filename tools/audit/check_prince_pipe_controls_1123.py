"""Observe the first pipe on the current MMC5 ROM with ordinary inputs."""

import argparse
from functools import lru_cache
import inspect
import json
from types import SimpleNamespace
from unittest.mock import patch

import check_prince_natural_sword_1113 as Game
import compose_bub_epoch_1123 as BubbleBobble
import compose_prince_oneup_lift_1123 as Lift
import compose_prince_pipe_approach_1123 as Trial
import compose_prince_ground_approach_1123 as Ground
import compose_prince_reverse_ledge_1123 as Reverse
import replay_prince_pipe_direct_1114 as Direct
import replay_prince_pipe_usability_1114 as Original


ROM, H = Original.ROM, Lift.H
PIPE_RECEIPT = '1f4cda2e7d069cb35dc72c3ff2b4370742e5847385cc89700c0fb0483e312002'
STAGE_RECEIPT = '18752d751a3fef60d7e4ed38932db77b53d553c3120273dff355d974c39c2e15'
GROUND_PIPE_RECEIPT = '5bad9c624f6db272377f93cccc24f4266c1b789e111cccb4e9aee2f2587296e6'
GROUND_STAGE_RECEIPT = 'fde5119f518de8ba421d0d26636af19b94e570d39cad30f2226b96192abecd25'
REVERSE_PIPE_RECEIPT = '252b1fde2ac609cc2aa5bd2a84f8e8be3f66fc52f117f5959174a87f0399d24e'
REVERSE_STAGE_RECEIPT = '71a2887007382456ba516b5e30630f52b73082b949dc588ae710652fd8767bbb'


@lru_cache(maxsize=2)
def packet(raw):
    if H(raw) in (BubbleBobble.PARENT, BubbleBobble.CANDIDATE):
        return Lift.extract(raw)
    return Trial.extract(raw)


def authenticate(raw):
    return dict(cookie=packet(raw)[2].hex(), ROM_SHA256=H(raw))


def rebind(function, **names):
    scope = dict(function.__globals__, **names)
    exec(compile(inspect.getsource(function), __file__, 'exec'), scope)
    return scope[function.__name__]


def controller(raw, pad, trace=False, return_left=False):
    factory = rebind(Original.controller, authenticate=authenticate, PIN=H(raw))
    text = rebind(Direct.controller, Frozen=SimpleNamespace(controller=factory))(raw, pad=pad, hold=300)
    assert text.count('hold_commits=300,') == 1
    text = text.replace('hold_commits=300,', 'hold_commits=360,', 1)
    old = '''  if age>=probe.hold_commits then
   final=probeState(s);probe.terminal=final
   finish(true,'Bounded ordinary pipe usability observation')
  end'''
    new = '''  if not probe.crossing and s.y<=145 and support(s) and s.x+10>=448 and s.mode~=2 and s.mode~=6 then
   probe.crossing=probeState(s)
  end
  if probe.crossing and s.x>=496 and floor(s) then
   final=probeState(s);probe.terminal=final
   finish(true,'First pipe crossed from a continuous approach');return
  end
  if age>=probe.hold_commits then
   final=probeState(s);probe.terminal=final
   finish(false,'First pipe did not clear from a continuous approach')
  end'''
    assert text.count(old) == 1
    text = text.replace(old, new)
    if return_left:
        old = '''   final=probeState(s);probe.terminal=final
   finish(true,'First pipe crossed from a continuous approach');return'''
        new = '''   probe.right_clear=probeState(s)
   switch('usability-return',10);return'''
        assert text.count(old) == 1
        text = text.replace(old, new, 1)
        old = 'local function laterTick(s)probeTick(s)end'
        guard = '''local function returnTick(s)
 local age=commits-changedAt
 if not probe.left_climb and s.action==10 and s.x>=463 and s.x<=490 then
  probe.left_climb=probeState(s)
 end
 if probe.left_climb and not probe.left_cap and s.y<=145 and s.x<=480 and s.x+13>=448 and support(s) and s.mode~=2 and s.mode~=6 then
  probe.left_cap=probeState(s)
 end
 if probe.left_cap and s.x<=433 and floor(s) then
  final=probeState(s);probe.terminal=final
  finish(true,'First pipe crossed from both sides with continuous input');return
 end
 if age>=390 then
  final=probeState(s);probe.terminal=final
  finish(false,'Return climb did not clear the right pipe face')
 end
end
'''
        assert text.count(old) == 1
        text = text.replace(old, guard + old)
        old = "if progress:sub(1,10)=='usability-'then probeTick(s);return end"
        new = "if progress=='usability-return'then returnTick(s);return end\n  " + old
        assert text.count(old) == 1
        text = text.replace(old, new, 1)
    if trace:
        old = 'local s=probeState(state());s.side=read(3)'
        new = '''local s=probeState(state());s.side=read(3)
 s.collision={tile=read(6),tile_y=read(5)+32,probe_x=read(8),buffer=read(9)+256*read(10),
  x_speed=read(0x57),y_speed=read(0x8e),prior_foot=source(0x86)+256*source(0x87),
  prior_x=source(0xa7)+256*source(0xa8),scroll=s.scroll}
 local function floorAt(x)
  return read(0x300+((x>>8)&1)*0xd0+((x&255)>>4)+read(5))
 end
 s.collision.under_body=floorAt(s.x+7)
 s.collision.behind=floorAt(s.x-2)
 s.collision.ahead=floorAt(s.x+16)'''
        assert text.count(old) == 1
        text = text.replace(old, new)
        marker = 'local function laterTick(s)probeTick(s)end'
        witness = '''
probe.ground_queries={}
observe(0xa04e,1,function()
 local s=state()
 if s.x<480 or s.x>563 or #probe.ground_queries>=48 then return end
 probe.ground_queries[#probe.ground_queries+1]={commit=s.commit,x=s.x,y=s.y,mode=s.mode,
  phase=source(0x2c),current_foot=s.foot,prior_foot=source(0x86)+256*source(0x87),
  current_high=source(0x85),area=read(0x753),query_y=source(0x136b,3)}
end)
'''
        assert text.count(marker) == 1
        text = text.replace(marker, marker + '\n' + witness)
        if return_left:
            witness = '''
probe.ledge_queries={outbound={},returning={}}
local ledgeQuery,ledgePoint
observe(0xbde5,3,function()
 local s=state()
 if s.x<420 or s.x>493 or source(0x40a)~=8 then return end
 local cpu=emu.getState();local sp=cpu['cpu.sp']
 local ret=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535
 if ret~=0xa487 and ret~=0xa493 and ret~=0xa4bd and ret~=0xa51e and ret~=0xa52a and ret~=0xa556 then return end
 local rows=probe.ledge_queries[progress=='usability-return' and 'returning' or 'outbound']
 if #rows>=18 then return end
 ledgeQuery={x=s.x,y=s.y,facing=s.facing,foot=s.foot,commit=s.commit,ret=ret,
  raw_x=source(0x78)+256*source(0x79),source_x=source(0x60f)+256*source(0x610),
  grid=source(0x4b1),query_y=cpu['cpu.y'],action=s.action,points={}}
 rows[#rows+1]=ledgeQuery
end)
observe(0xb310,3,function()
 if not ledgeQuery then return end
 ledgePoint={x=source(0x1369,3)+256*source(0x136a,3),y=source(0x136b,3)}
 ledgeQuery.points[#ledgeQuery.points+1]=ledgePoint
end)
observe(0xb352,3,function()
 if not ledgePoint then return end
 local cpu=emu.getState()
 ledgePoint.tile=cpu['cpu.a'];ledgePoint.solid=(cpu['cpu.ps']&1)~=0;ledgePoint=nil
end)
for _,pc in ipairs({0xa487,0xa493,0xa4bd,0xa51e,0xa52a,0xa556})do
 observe(pc,3,function()
  if not ledgeQuery or ledgeQuery.ret~=pc then return end
  local cpu=emu.getState()
  ledgeQuery.material=cpu['cpu.a'];ledgeQuery.surface=source(0x7f)+256*source(0x80)
  ledgeQuery=nil
 end)
end
'''
            text = text.replace(marker, marker + '\n' + witness, 1)
    Original.LuaRuntime().compile(text)
    return text


def source(raw, pad, return_left=False):
    current_packet = SimpleNamespace(extract=packet, COOKIE=Lift.Packet.COOKIE)
    with patch.object(Game, 'proof_parent', packet), patch.object(Game, 'Replay', SimpleNamespace(Packet=current_packet)):
        model, opening = Game.cold(raw)
    text = controller(raw, pad, return_left=return_left)
    loads = json.loads
    receipts = []

    def capture(*args, **kwargs):
        result = loads(*args, **kwargs)
        if 'later_route' in result:
            receipts.append(result)
        return result

    with patch.object(Game, 'controller', lambda raw: text), patch.object(Game.json, 'loads', capture):
        proof = Game.route(model, raw, 2300)
    assert len(receipts) == 1, proof
    return summary(receipts[0], pad)


def stage_controller(raw, baseline):
    import compose_donkey_side_early_1123 as DonkeyEarly
    import compose_donkey_side_shortcut_1123 as Donkey
    import compose_karnov_side_route_1123 as Karnov
    import compose_kirby_spiny_sound_1123 as Kirby
    import compose_prince_side_current_1123 as Prince
    import run_prince_epoch_native_1123 as Stage

    if H(baseline) == Ground.CANDIDATE:
        baseline = Ground.inverse(baseline)
    if H(baseline) == Trial.CANDIDATE:
        baseline = Trial.inverse(baseline)
    anchor = baseline
    for undo in (BubbleBobble, Karnov, Kirby, DonkeyEarly, Donkey, Prince):
        anchor = undo.inverse(anchor)
    text = Stage.controllers(anchor, baseline, ('stage',))['stage']
    assert H(baseline) in text
    text = text.replace(H(baseline), H(raw))
    old_cookie, new_cookie = packet(baseline)[2].hex(), packet(raw)[2].hex()
    assert text.count(old_cookie) == 1
    text = text.replace(old_cookie, new_cookie, 1)
    # Check the changed controls gate at the same first-draw publication
    # witness as the already retained source and graphics extents.
    prefix = 'local candidateStaticExtents='
    line = next(row for row in text.splitlines() if row.startswith(prefix))
    start = Trial.GATE - 0xA000
    contents = packet(raw)[0]
    regions = [(3, start, contents[0][start:start + len(Trial.OLD_GATE)])]
    if H(raw) in (Ground.CANDIDATE, Reverse.CANDIDATE):
        start = Ground.NATIVE_FLOOR - 0xC800
        regions.append((2, start + 0x800, contents[1][start:start + Ground.NATIVE_FLOOR_SIZE]))
    if H(raw) == Reverse.CANDIDATE:
        start = Reverse.GATE - 0xA000
        regions.append((3, start, contents[0][start:start + len(Reverse.OLD_GATE)]))
        regions.append((1, Reverse.PRIVATE_SIZE, contents[3][Reverse.PRIVATE_SIZE:]))
    rows = Original.LuaRuntime().eval(line[len(prefix):])
    extents = []
    for i in range(1, len(rows) + 1):
        row = rows[i]
        bytes_read = row['bytes']
        data = [bytes_read[j] for j in range(1, len(bytes_read) + 1)]
        for bank, offset, expected in regions:
            if row['bank'] != bank:
                continue
            overlap = max(row['offset'], offset), min(row['offset'] + len(data), offset + len(expected))
            for address in range(*overlap):
                data[address - row['offset']] = expected[address - offset]
        extents.append(dict(bank=row['bank'], offset=row['offset'], bytes=data))
    for bank, offset, expected in regions:
        extents.append(dict(bank=bank, offset=offset, bytes=list(expected)))
    assert text.count(line) == 1
    text = text.replace(line, prefix + Stage.Route.R.P.Base.lua(extents), 1)
    if H(raw) in (Ground.CANDIDATE, Reverse.CANDIDATE):
        old = "'Actual16a static extent before first renderer'"
        new = "string.format('Static extent bank %d offset %04X expected %02X',row.bank,row.offset+i-1,value)"
        assert text.count(old) == 1
        text = text.replace(old, new, 1)
    Original.LuaRuntime().compile(text)
    return text


def summary(receipt, pad):
    probe = receipt['later_route']['usability']
    def compact(state):
        fields = ('x', 'y', 'hp', 'lives', 'commit', 'action', 'pose', 'mode', 'nativeInput',
                  'source_pad', 'foot', 'query_x', 'query_raw', 'wall_timer', 'side', 'collision')
        return {key: state[key] for key in fields if key in state} if state else None

    return dict(pad=pad, passed=receipt['passed'], reason=receipt['reason'], ground_queries=probe.get('ground_queries'),
                ledge_queries=probe.get('ledge_queries'),
                approach=compact(probe.get('release')), hang=probe['hang'], cap=compact(probe.get('crossing')),
                right_clear=compact(probe.get('right_clear')), left_climb=compact(probe.get('left_climb')),
                left_cap=compact(probe.get('left_cap')),
                terminal=compact(receipt['terminal']), max_x=max((s['x'] for s in probe['samples']), default=None),
                walls=[compact(s) for s in probe['walls'][:4]], samples=[compact(s) for s in probe['samples'][::6]])


def native(raw, pad, trial, stage=False, install=False, trace=False, return_left=False):
    from run_stdout_mesen_1110 import run
    from run_sonic_current_empty_cadence_1122 import SHARED
    from mesen_session_guard_v1 import require_free_workspace
    from nightly_patch_guard_v1 import check

    installed = ROM.read_bytes()
    guard = check(ROM)
    candidate, script = SHARED / 'candidate.nes', SHARED / 'controller.lua'
    assert set(SHARED.iterdir()) == {candidate, script} and candidate.read_bytes() == installed
    require_free_workspace(Original.R, ROM, allow_interactive=True)
    script_before = script.read_bytes()
    replaced = delivered = False

    def replay(path, stage):
        text = stage_controller(raw, installed) if stage else controller(raw, pad, trace, return_left)
        script.write_bytes(text.encode())
        result = run(script, path, SHARED / 'capture', H(raw), 320 if stage else 135,
                     variant=3, long_no_capture=True)
        assert not result['images'] and result['outputs_written'] == 0
        return result

    try:
        path = candidate if trial else ROM
        if install:
            assert trial and pad == 9 and not stage
            tests = {
                Trial.CANDIDATE: (Trial, PIPE_RECEIPT, STAGE_RECEIPT),
                Ground.CANDIDATE: (Ground, GROUND_PIPE_RECEIPT, GROUND_STAGE_RECEIPT),
                Reverse.CANDIDATE: (Reverse, REVERSE_PIPE_RECEIPT, REVERSE_STAGE_RECEIPT),
            }
            recipe, pipe_receipt, stage_receipt = tests[H(raw)]
            trace = recipe is Ground
            return_left = recipe is Reverse
            assert H(raw) == recipe.CANDIDATE and recipe.inverse(raw) == installed
            assert not guard['matching_patch_files']
            candidate.write_bytes(raw)
            replaced = True
            ROM.write_bytes(raw)
            assert check(ROM)['ROM_sha256'] == recipe.CANDIDATE
            for full, expected in ((False, pipe_receipt), (True, stage_receipt)):
                result = replay(ROM, full)
                assert result['passed'] and result['receipt_SHA256'] == expected
                print('Downloads', 'full stage' if full else 'first pipe', expected, flush=True)
            assert ROM.read_bytes() == raw and not check(ROM)['matching_patch_files']
            delivered = True
            return dict(installed=str(ROM), ROM=H(raw), pipe_receipt=pipe_receipt, stage_receipt=stage_receipt)
        if trial:
            candidate.write_bytes(raw)
        result = replay(path, stage)
        receipt = result['receipt']
        if stage:
            keys = ('passed', 'reason', 'phase', 'terminal', 'physical_frames', 'commits',
                    'grounded_1_2_completed_returns', 'persistent_sword')
            report = {key: receipt[key] for key in keys if key in receipt}
        else:
            report = summary(receipt, pad)
        report.update(ROM=H(raw), receipt_SHA256=result['receipt_SHA256'], script_SHA256=result['script_SHA256'])
        return report
    finally:
        if replaced and not delivered:
            ROM.write_bytes(installed)
        if trial and not delivered:
            candidate.write_bytes(installed)
        script.write_bytes(script_before)
        assert check(ROM)['ROM_sha256'] == H(raw if delivered else installed)
        assert candidate.read_bytes() == (raw if delivered else installed)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pads', nargs='+', type=int, choices=(9, 129, 137))
    parser.add_argument('--trial', action='store_true')
    parser.add_argument('--native', action='store_true')
    parser.add_argument('--stage', action='store_true')
    parser.add_argument('--install', action='store_true')
    parser.add_argument('--trace', action='store_true')
    parser.add_argument('--ground', action='store_true')
    parser.add_argument('--reverse', action='store_true')
    parser.add_argument('--return-left', action='store_true')
    args = parser.parse_args()
    assert not args.stage or (args.native and args.trial and len(args.pads) == 1)
    assert not args.install or (args.native and args.trial and args.pads == [9])
    assert not args.trace or (args.native and not args.install and not args.stage)
    assert not args.ground or args.trial
    assert not args.reverse or (args.trial and not args.ground)
    assert not args.return_left or (args.pads == [9] and not args.install and not args.stage)
    raw = ROM.read_bytes()
    if args.trial:
        recipe = Reverse if args.reverse else Ground if args.ground else Trial
        raw = recipe.compose(raw)
    print(H(raw), flush=True)
    for pad in args.pads:
        if args.native:
            result = native(raw, pad, args.trial, args.stage, args.install, args.trace, args.return_left)
        else:
            result = source(raw, pad, args.return_left)
        print(json.dumps(result, separators=(',', ':')), flush=True)
