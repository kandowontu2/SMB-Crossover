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
import compose_prince_pipe_cap_support_1123 as CapSupport
import replay_prince_pipe_direct_1114 as Direct
import replay_prince_pipe_usability_1114 as Original


ROM, H = Original.ROM, Lift.H
PIPE_RECEIPT = '1f4cda2e7d069cb35dc72c3ff2b4370742e5847385cc89700c0fb0483e312002'
STAGE_RECEIPT = '18752d751a3fef60d7e4ed38932db77b53d553c3120273dff355d974c39c2e15'
GROUND_PIPE_RECEIPT = '5bad9c624f6db272377f93cccc24f4266c1b789e111cccb4e9aee2f2587296e6'
GROUND_STAGE_RECEIPT = 'fde5119f518de8ba421d0d26636af19b94e570d39cad30f2226b96192abecd25'
REVERSE_PIPE_RECEIPT = '252b1fde2ac609cc2aa5bd2a84f8e8be3f66fc52f117f5959174a87f0399d24e'
REVERSE_STAGE_RECEIPT = '71a2887007382456ba516b5e30630f52b73082b949dc588ae710652fd8767bbb'
CAP_FIRST_RECEIPT = '16561b3f933afbb4a89d1c4f226fe0639854ffb3daae64febe7f121db7ee5e0c'
CAP_FOURTH_RECEIPT = '99ba6419b77fc75d21ea5b31917e169ecbd002a68d01c2c5babf708cc8930b4b'
CAP_STAGE_RECEIPT = 'fb473e00f40bfc0bd26e273f2716e4139263b27e63f0d20d7a3f0c04e7d463a8'


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


def pipe_audit(text, target, marker):
    left, top = {2: (608, 160), 3: (736, 144), 4: (912, 144)}[target]
    before = 'local function laterTick(s)'
    assert text.count(before) == 1 and text.count(marker) == 1
    watch = f'''local audit={{pipe={target},left={left},top={top}}}
late.pipe_audit=audit
local function auditPipe(s)
 audit.approach=audit.approach or s
 if s.action==10 and s.x>=audit.left-20 and s.x<audit.left+32 then audit.climb=audit.climb or s end
 local leftFoot,rightFoot=capFeet(s,audit.left,audit.top)
 if audit.climb and (leftFoot or rightFoot) and not audit.cap then
  audit.cap=s
  if audit.pipe==3 then pad=0 end
 end
 if audit.cap and audit.pipe==4 and (commits-audit.cap.commit)%4==0 then
  audit.after_cap=audit.after_cap or {{}}
  if #audit.after_cap<28 then
   audit.after_cap[#audit.after_cap+1]={{x=s.x,y=s.y,action=s.action,ground=s.ground,mode=s.mode,hp=s.hp}}
  end
 end
 local floorClear=audit.pipe~=3 and s.x>=audit.left+32 and floor(s) and support(s)
 local steadyCap=audit.pipe==3 and (leftFoot or rightFoot) and idle(s) and audit.cap
  and commits-audit.cap.commit>=25
 if audit.cap and (floorClear or steadyCap) then
  audit.exit=s;final=s
  finish(s.hp==audit.approach.hp and s.lives==initial.lives,'Pipe '..audit.pipe..' climbed using Up and Right')
 elseif (not audit.cap and s.x>=audit.left+48) or commits-changedAt>=650 then
  final=s;finish(false,'Did not verify held Up and Right at pipe '..audit.pipe)
 end
end
'''
    return text.replace(before, watch + before, 1)


def controller(raw, pad, trace=False, return_left=False, second_pipe=False):
    assert not (return_left and second_pipe)
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
    if second_pipe:
        old = "   finish(true,'First pipe crossed from a continuous approach');return"
        new = "   switch('audit-approach',9);return"
        assert text.count(old) == 1
        text = text.replace(old, new, 1)
        marker = "  if progress:sub(1,10)=='usability-'then"
        pos = text.index(marker)
        text = text[:pos] + "  if progress=='audit-approach' then auditPipe(s);return end\n" + text[pos:]
        text = pipe_audit(text, 2, "  if progress=='audit-approach' then auditPipe(s);return end")
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


def pipe_reference(raw):
    import check_shared_result_copy_1123 as SharedResult

    return SharedResult.inverse(raw) if H(raw) in SharedResult.CANDIDATES.values() else raw


def stage_controller(raw, baseline, extra_extents=()):
    import compose_donkey_side_early_1123 as DonkeyEarly
    import compose_donkey_side_shortcut_1123 as Donkey
    import compose_karnov_side_route_1123 as Karnov
    import compose_kirby_spiny_sound_1123 as Kirby
    import compose_prince_side_current_1123 as Prince
    import run_prince_epoch_native_1123 as Stage

    baseline = pipe_reference(baseline)
    if H(baseline) == CapSupport.CANDIDATE:
        baseline = CapSupport.inverse(baseline)
    if H(baseline) == Reverse.CANDIDATE:
        baseline = Reverse.inverse(baseline)
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
    if H(raw) in (Ground.CANDIDATE, Reverse.CANDIDATE) or extra_extents:
        start = Ground.NATIVE_FLOOR - 0xC800
        regions.append((2, start + 0x800, contents[1][start:start + Ground.NATIVE_FLOOR_SIZE]))
    if H(raw) == Reverse.CANDIDATE or extra_extents:
        start = Reverse.GATE - 0xA000
        regions.append((3, start, contents[0][start:start + len(Reverse.OLD_GATE)]))
        regions.append((1, Reverse.PRIVATE_SIZE, contents[3][Reverse.PRIVATE_SIZE:]))
    regions.extend(extra_extents)
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


def later_pipe_controller(raw, target, baseline=None, extra_extents=()):
    assert target in (3, 4)
    if baseline is None:
        baseline = raw
    baseline = pipe_reference(baseline)
    if H(baseline) == CapSupport.CANDIDATE:
        baseline = CapSupport.inverse(baseline)
    text = stage_controller(raw, Reverse.inverse(baseline), extra_extents)
    finish = "local function finish(passed,reason)\n  if passed then "
    assert text.count(finish) == 1
    text = text.replace(finish, '''local function finish(passed,reason)
  if passed and progress=='audit-approach' then
    assert(newPacketVerified,'Actual Prince packet readback before the pipe')
  elseif passed then ''', 1)
    check = '  local enemy=enemyNear(s.x)\n  firstEnemy=firstEnemy or enemy'
    assert text.count(check) == 1
    if target == 3:
        check_point = "progress=='later-approach' and laterPipe==2 and s.x>=690 and s.x<736"
    else:
        check_point = "progress=='third-running-flight' and ((s.x>=897 and idle(s)) or s.mode==2 or s.mode==6)"
    marker = "  if progress=='audit-approach' then auditPipe(s);return end"
    text = text.replace(check, f'''  if {check_point} then switch('audit-approach',9) end
{marker}
{check}''', 1)
    text = pipe_audit(text, target, marker)
    if target == 4:
        text += '''
local function auditActive()
 local audit=late.pipe_audit
 return audit.cap and commits-audit.cap.commit<=40 and audit or nil
end
local function xCorrection(addr,value)
 local audit=auditActive()
 if not audit then return end
 local field=addr==0x75 and 'export' or 'source'
 local old=addr==0x75 and read(addr) or source(0x60f)
 if math.abs(old-value)<8 then return end
 local s=state();local cpu=emu.getState();local pc=cpu['cpu.pc'];local mapped=emu.convertAddress(pc)
 local sp=cpu['cpu.sp'];local caller=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535
 audit.corrections=audit.corrections or {}
 if #audit.corrections>=24 then return end
 audit.corrections[#audit.corrections+1]={x=s.x,y=s.y,pc=pc,physical=mapped and mapped.address,field=field,
  commit=commits,old=old,value=value,foot=s.foot,previous=source(0x86)+256*source(0x87),
  tile=read(6),row=read(5),probeX=read(8),side=read(3),backing=read(0x7da1),
  sourceX=source(0x60f)+256*source(0x610),action=s.action,mode=s.mode,grid=source(0x4b1),
  rawX=source(0x78)+256*source(0x79),pointY=source(0x136b,3),caller=caller,
  cellX=source(0x7d)+256*source(0x7e),surface=source(0x7f)+256*source(0x80),
  alignX=source(0xa1),material=source(0x9f),index=source(0x7b),gridBase=source(0x7a)}
end
emu.addMemoryCallback(guarded(xCorrection),emu.callbackType.write,0x75)
emu.addMemoryCallback(guarded(xCorrection),emu.callbackType.write,0xc60f)
observe(0xb352,3,function()
 local audit=auditActive()
 if not audit or commits-audit.cap.commit<21 then return end
 local cpu=emu.getState()
 audit.tiles=audit.tiles or {}
 if #audit.tiles>=36 then return end
 audit.tiles[#audit.tiles+1]={commit=commits,x=source(0x1369,3)+256*source(0x136a,3),
  y=source(0x136b,3),tile=cpu['cpu.a'],grid=source(0x4b1),
  material=source(0x9f),solid=cpu['cpu.ps']&1}
end)
'''
    Original.LuaRuntime().compile(text)
    return text


def summary(receipt, pad):
    probe = receipt['later_route']['usability']
    def compact(state):
        fields = ('x', 'y', 'hp', 'lives', 'commit', 'action', 'pose', 'mode', 'nativeInput',
                  'source_pad', 'foot', 'query_x', 'query_raw', 'wall_timer', 'side', 'collision')
        return {key: state[key] for key in fields if key in state} if state else None

    return dict(pad=pad, passed=receipt['passed'], reason=receipt['reason'],
                ground_queries=probe.get('ground_queries'),
                ledge_queries=probe.get('ledge_queries'),
                approach=compact(probe.get('release')), hang=probe['hang'], cap=compact(probe.get('crossing')),
                right_clear=compact(probe.get('right_clear')), left_climb=compact(probe.get('left_climb')),
                left_cap=compact(probe.get('left_cap')),
                terminal=compact(receipt['terminal']), max_x=max((s['x'] for s in probe['samples']), default=None),
                walls=[compact(s) for s in probe['walls'][:4]], samples=[compact(s) for s in probe['samples'][::6]])


def native(raw, pad, trial, stage=False, install=False, trace=False, return_left=False, pipe=None):
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
    cap_reference = pipe_reference(raw)
    extra_extents = CapSupport.static_extents(cap_reference) if H(cap_reference) == CapSupport.CANDIDATE else ()
    replaced = delivered = False

    def replay(path, stage, target_pipe=None):
        if target_pipe in (3, 4):
            text = later_pipe_controller(raw, target_pipe, installed, extra_extents)
        elif stage:
            text = stage_controller(raw, installed, extra_extents)
        else:
            text = controller(raw, pad, trace, return_left, second_pipe=target_pipe == 2)
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
                CapSupport.CANDIDATE: (CapSupport, CAP_FIRST_RECEIPT, CAP_STAGE_RECEIPT),
            }
            recipe, pipe_receipt, stage_receipt = tests[H(raw)]
            trace = recipe is Ground
            return_left = recipe in (Reverse, CapSupport)
            assert H(raw) == recipe.CANDIDATE and recipe.inverse(raw) == installed
            assert not guard['matching_patch_files']
            candidate.write_bytes(raw)
            replaced = True
            ROM.write_bytes(raw)
            assert check(ROM)['ROM_sha256'] == recipe.CANDIDATE
            runs = [('first pipe', False, None, pipe_receipt), ('full stage', True, None, stage_receipt)]
            if recipe is CapSupport:
                runs.insert(1, ('fourth pipe', False, 4, CAP_FOURTH_RECEIPT))
            for label, full, target, expected in runs:
                result = replay(ROM, full, target)
                assert result['passed'] and result['receipt_SHA256'] == expected
                print('Downloads', label, expected, flush=True)
            assert ROM.read_bytes() == raw and not check(ROM)['matching_patch_files']
            delivered = True
            return dict(installed=str(ROM), ROM=H(raw), receipts={label: digest for label, _, _, digest in runs})
        if trial:
            candidate.write_bytes(raw)
        result = replay(path, stage, pipe)
        receipt = result['receipt']
        if pipe:
            report = dict(passed=receipt['passed'], reason=receipt['reason'],
                          witness=receipt['later_route'].get('pipe_audit'), terminal=receipt.get('terminal'))
        elif stage:
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
    parser.add_argument('--cap-support', action='store_true')
    parser.add_argument('--return-left', action='store_true')
    parser.add_argument('--pipe', type=int, choices=(2, 3, 4))
    args = parser.parse_args()
    assert not args.stage or (args.native and args.trial and len(args.pads) == 1)
    assert not args.install or (args.native and args.trial and args.pads == [9])
    assert not args.trace or (args.native and not args.install and not args.stage)
    assert not args.ground or args.trial
    assert not args.reverse or (args.trial and not args.ground)
    assert not args.cap_support or (args.trial and not args.ground and not args.reverse)
    assert not args.return_left or (args.pads == [9] and not args.install and not args.stage)
    assert not args.pipe or (args.native and args.pads == [9] and not args.install
                             and not args.stage and not args.return_left)
    raw = ROM.read_bytes()
    if args.trial:
        recipe = CapSupport if args.cap_support else Reverse if args.reverse else Ground if args.ground else Trial
        raw = recipe.compose(raw)
    print(H(raw), flush=True)
    for pad in args.pads:
        if args.native:
            result = native(raw, pad, args.trial, args.stage, args.install,
                            args.trace, args.return_left, args.pipe)
        else:
            result = source(raw, pad, args.return_left)
        print(json.dumps(result, separators=(',', ':')), flush=True)
