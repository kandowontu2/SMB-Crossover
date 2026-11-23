"""Bounded exact3af5 accepted-head checks; no files, ROM install or Mesen.

The gameplay probe starts through the real menu/cold path and uses only
ordinary pads. Unit mounts and interrupt injections are separately declared.
"""
import argparse
from collections import Counter
from pathlib import Path
import json
from unittest.mock import patch

import compose_dkjr_head_bridge_current_1123 as C
import check_dkjr_head_bridge_1113 as Previous
import check_dkjr_sonic_dispatch_1123 as Q
import check_dkjr_side_epoch_fast_1123 as Verify
from check_mini_funded_actor_1108_v3 import registers, live_stack

N, W, B, H = Q.N, Q.W, Q.B, C.H


def point(cpu):
    return (cpu.memory.rawtags[(cpu.pc-0x8000)//8192] if cpu.pc >= 0x8000 else -1, cpu.pc)


def state(m):
    r = m.ram[2]
    return dict(x=N.get(m, 'Player_X_Position')+256*N.get(m, 'Player_PageLoc'),
        y=N.get(m, 'Player_Y_Position'), source=r[0x6b], prior=r[0x6c],
        facing=r[0x6d], direction=r[0x54], pose=r[0x71], age=r[0x7e],
        fraction=r[0x7f], engine=N.get(m, 'GameEngineSubroutine'),
        lives=N.get(m, 'NumberofLives'), status=N.get(m, 'PlayerStatus'),
        camera=N.get(m, 'ScreenLeft_X_Pos')+256*N.get(m, 'ScreenLeft_PageLoc'),
        held=r[0x14], source_origin=r[0x76], hurt=r[0x68])


def actor(m, i):
    return dict(slot=i, id=N.get(m, 'Enemy_ID', i), flag=N.get(m, 'Enemy_Flag', i),
        state=N.get(m, 'Enemy_State', i),
        x=N.get(m, 'Enemy_X_Position', i)+256*N.get(m, 'Enemy_PageLoc', i),
        y=N.get(m, 'Enemy_Y_Position', i))


def actors(m):
    return [actor(m, i) for i in range(6) if N.get(m, 'Enemy_Flag', i)]


def platform(m):
    return next((a for a in actors(m) if a['id'] == 37 and a['x'] == 416), None)


def cold(raw):
    m = Q.enter(raw, 'DK')
    for age in range(300):
        if (tuple(N.get(m, n) for n in ('OperMode', 'OperMode_Task', 'GameEngineSubroutine')) == (1, 3, 8)
                and m.ram[2][0x8fe] == 2):
            break
        B.main_step(m, 0)
    else:
        raise AssertionError('Ordinary cold readiness bound')
    assert N.get(m, 'WorldNumber') == N.get(m, 'LevelNumber') == 0
    assert N.get(m, 'CheatInvincible') == N.get(m, 'CheatStartLevel') == 0
    assert all(bytes(m.ram[b][0x1fe0:0x1ff0]) == raw[C.COOKIE_AT:C.COOKIE_AT+16] for b in (2, 3))
    assert state(m)['x'] == 40 and state(m)['lives'] == 2 and m.ram[2][0x8fe] == 2, state(m)
    return m, age


def access_prefix(raw):
    """Frozen ordinary approach, native416 boarding and left-edge launch."""
    m, opening = cold(raw)
    hold = rearm = 0
    phase, first416, events = 'approach', None, []
    for tick in range(1600):
        v, p = state(m), platform(m)
        ground = v['source'] == 1 and N.get(m, 'Player_State') == 0
        assert v['lives'] == 2 and v['source'] != 5 and v['engine'] != 11, (phase, tick, v)
        assert not any(a['id'] == 37 and a['x'] == 336 for a in actors(m)), 'Private336 helper forbidden'
        if p and first416 is None:
            first416 = dict(update=tick, hero=v, actor=p)
        if p and v['x'] >= 426 and v['y'] < 176 and v['y']+32 == p['y'] and v['source'] == 1:
            break
        if v['x'] >= 426:
            phase = 'board'
        if phase == 'approach':
            near = any(a['flag'] == 1 and a['id'] in (2, 6) and not a['state'] & 32
                and a['y'] >= 172 and 8 <= a['x']-v['x'] <= 30 for a in actors(m))
            if ground and tick >= rearm and near:
                hold, rearm = tick+8, tick+47
                events.append(dict(event='ordinary-enemy-hop', update=tick, hero=v, actors=actors(m)))
            pad = 1 | (128 if tick < hold else 0)
        else:
            if p and ground and tick >= rearm and 192 <= p['y'] <= 208:
                hold, rearm = tick+8, tick+47
                events.append(dict(event='board-hop', update=tick, hero=v, actor=p))
            pad = 128 if tick < hold else 0
        B.main_step(m, pad)
    else:
        raise AssertionError(('Approach bound', state(m), platform(m)))
    boarded = dict(update=tick, hero=state(m), actor=platform(m))
    for moved in range(60):
        if state(m)['x'] <= 401:
            break
        B.main_step(m, 2)
        assert state(m)['lives'] == 2 and state(m)['source'] != 5
    else:
        raise AssertionError('Left staging bound')
    prior = None
    for waited in range(400):
        p, v = platform(m), state(m)
        if p and v['source'] == 1 and v['y']+32 == p['y'] and 174 <= p['y'] <= 180 and prior is not None and p['y'] < prior:
            break
        prior = p['y'] if p else None
        B.main_step(m, 0)
    else:
        raise AssertionError(('Existing416 launch window', state(m), platform(m)))
    assert state(m)['pose'] == 0 and not state(m)['held'] & 128
    return m, dict(opening_Main=opening, first416=first416, boarded=boarded,
        left_updates=moved, wait_updates=waited, launch=dict(hero=state(m), actor=platform(m)), events=events)


def contact_route(raw, *, collect_cuts=False):
    m, prefix = access_prefix(raw)
    candidate = H(raw) == C.CANDIDATE
    program = C.program(C.inverse(raw) if candidate else raw)
    labels = program['symbols']
    cuts, counts, curve, head_records = {}, Counter(), [], []
    minimum, source_pending, effect_pending = 255, None, None
    effect_pc, effect_tag = labels['NativeHeadEffect'], labels['NativeHeadBank'] | 128
    phase, move, clock = 0xb8f0, 0xa2e8, 0xaf2d
    selected = {(3, i['pc']) for i in program['instructions']}
    effect_returns = []
    original_stops = []
    effect_curve_index = None

    class Trace:
        def run(self, cpu, stop):
            nonlocal minimum, source_pending, effect_pending, effect_curve_index
            for _ in range(500000):
                if (cpu.pc, cpu.sp) == stop:
                    return
                tag, pc = point(cpu)
                minimum = min(minimum, cpu.sp)
                if collect_cuts and (tag, pc) in selected:
                    key = tag, pc, cpu.p & 5
                    if key not in cuts:
                        assert len(cuts) < 400
                        z = Q.clone(cpu)
                        z.memory.combined_terminal = stop
                        cuts[key] = z
                def token():
                    return ((m[0x101+cpu.sp]+256*m[0x102+cpu.sp]+1) & 65535, cpu.sp+2)
                if (tag, pc) == (3, phase):
                    assert source_pending is None
                    source_pending = dict(token=token(), move=False, clock=False)
                    counts['source_entries'] += 1
                if source_pending and (tag, pc) == (3, move):
                    source_pending['move'] = True
                if source_pending and (tag, pc) == (3, clock):
                    source_pending['clock'] = True
                if source_pending and (pc, cpu.sp) == source_pending['token']:
                    assert source_pending['move'] and source_pending['clock']
                    counts['source_returns'] += 1
                    if effect_returns:
                        counts['post_effect_source_returns'] += 1
                    source_pending = None
                if candidate and (tag, pc) == (3, labels['DkAcceptHead']):
                    head_records.append(dict(hero=state(m), query=list(m.ram[2][0x3e:0x42]),
                        wall=list(m.ram[2][0x42:0x46]), mode=m.ram[2][0x8da]))
                if (tag, pc) == (effect_tag, effect_pc):
                    assert effect_pending is None
                    effect_pending = dict(token=token(), before=state(m), tile=cpu.a,
                        row=N.get(m, 'R2'), buffer=N.get(m, 'R6')+256*N.get(m, 'R7'))
                    counts['native_effect_entries'] += 1
                    effect_curve_index = len(curve)
                if effect_pending and (pc, cpu.sp) == effect_pending['token']:
                    p = effect_pending
                    at = p['buffer']+p['row']
                    effect_returns.append(dict(before=p['before'], after=state(m), tile=p['tile'],
                        cell=at, after_tile=m[at], bounce=N.get(m, 'BlockBounceTimer')))
                    counts['native_effect_returns'] += 1
                    effect_pending = None
                if tag == 3 and bytes(m[(pc+i) & 65535] for i in range(3)) == bytes.fromhex('8d6bc0') and m.ram[2][0x6b] == 3 and cpu.a == 4:
                    original_stops.append(dict(PC=pc, hero=state(m), query=list(m.ram[2][0x3e:0x42]), wall=list(m.ram[2][0x42:0x46])))
                cpu.step()
            raise AssertionError('Contact Main instruction bound')

    for update in range(90):
        pad = 130 if update < 8 else 2
        B.main_step(m, pad, Trace())
        v = state(m)
        curve.append(dict(update=update+1, pad=pad, hero=v, actor=platform(m)))
        assert v['lives'] == 2 and v['source'] != 5 and v['engine'] != 11, ('Post-contact injury', update, v)
        assert v['status'] == 0 and not any(a['id'] == 46 for a in actors(m))
        if effect_returns and counts['post_effect_source_returns'] >= 25 and v['source'] == v['prior'] == 1:
            break
    assert source_pending is None and effect_pending is None
    if candidate:
        assert len(head_records) == len(effect_returns) == 1
        event, returned = head_records[0], effect_returns[0]
        assert event['hero']['source'] == 3 and event['hero']['age'] > 0
        assert event['query'][1] == event['wall'][3] == 159
        assert event['hero']['source_origin'] == prefix['launch']['hero']['y']+15 > 159
        cam = event['hero']['camera']
        assert [event['wall'][0]+cam, event['wall'][1], event['wall'][2]+cam, event['wall'][3]] == [384, 144, 399, 159]
        assert returned['tile'] == 81 and returned['after_tile'] == 35 and returned['bounce'] == 16
        assert counts['post_effect_source_returns'] >= 25 and m.ram[2][0x4b6] == 0
        assert original_stops and original_stops[0]['PC'] == labels['OriginalFall']+2
    else:
        assert not head_records and not effect_returns and original_stops
        assert original_stops[0]['PC'] == 0xa3b9
    report = dict(passed=True, ROM_SHA256=H(raw), candidate=candidate, prefix=prefix,
        original_stops=original_stops, accepted_heads=head_records,
        native_effect_returns=effect_returns, work=dict(counts), curve=curve,
        terminal=state(m), minimum_SP=minimum, effect_curve_index=effect_curve_index,
        gameplay_state_grants=0, added_entities=0, outputs=0,
        scope='Actual normal-NMI linked menu/cold/current416 rider and underside384 contact; no Mesen or Mushroom acquisition.')
    return report, cuts


def fixtures(parent, candidate, info):
    seed, _ = cold(parent)
    with patch.object(Previous.B, 'COOKIE', C.PARENT_COOKIE):
        return dict(rectangles=Previous.rect_funding(seed, parent, candidate, info),
            source=Previous.source_closure(parent, candidate, info),
            indirect=Previous.indirect_reads(seed, parent, candidate, info),
            capture=Previous.capture(seed, parent, candidate, info),
            effect_gates=Previous.effect_gates(seed, candidate, info),
            native_effect=Previous.native_effect(seed, candidate, info))


def interrupts(cuts):
    counts, minimum, examples = Counter(), 255, []
    addresses = (*range(0x15a), *range(0x200, 0x800), *range(0x5c00, 0x8000))
    def native(m):
        return bytes(m[at] for at in addresses)
    def delta(left, right):
        return {at: (a, b) for at, a, b in zip(addresses, left, right, strict=True) if a != b}
    for original in cuts.values():
        for kind in ('IRQ', 'busyNMI'):
            if kind == 'IRQ' and original.p & 4:
                continue
            b, control = Q.clone(original), Q.clone(original)
            for cpu in (b, control):
                N.put(cpu.memory, NmiDisable=255)
            # Same reached registers/SP/mappings/data, but the reference NMI
            # interrupts a staged native IdleLoop PC rather than bridge code.
            # No foreground instruction executes at that reference PC.
            safe_pc = W.address(control.memory.bundle, 'IdleLoop')
            control.pc = safe_pc
            before = b.pc, b.sp, registers(b, 0xef)
            stack = live_stack(b)
            private = tuple(map(bytes, b.memory.ram))
            smc = bytes(b.memory[0x15a:0x17b])
            skipped = N.get(b.memory, 'NmiSkipped')
            baseline_native = native(b.memory)
            audio_pc = W.address(b.memory.bundle, 'AudioUpdate')
            audio_tag = ((W.location(b.memory.bundle, 'AudioUpdate')-16)//8192) | 128
            audio_pending, audio_before, audio_changes = None, None, None
            def observe(cpu):
                nonlocal minimum, audio_pending, audio_before, audio_changes
                minimum = min(minimum, cpu.sp)
                m = cpu.memory
                if point(cpu) == (audio_tag, audio_pc):
                    assert audio_pending is None and audio_changes is None
                    audio_pending = ((m[0x101+cpu.sp]+256*m[0x102+cpu.sp]+1)&65535, cpu.sp+2)
                    audio_before = native(m)
                if audio_pending == (cpu.pc, cpu.sp):
                    audio_changes = delta(audio_before, native(m))
                    audio_pending = None
            for cpu in (b, control):
                if kind == 'IRQ':
                    cpu.irq()
                else:
                    cpu.nmi()
                Verify.finish(cpu, before[:2] if cpu is b else (safe_pc, before[1]), observe if cpu is b else None)
            assert registers(b, 0xef) == before[2] and live_stack(b) == stack
            assert tuple(map(bytes, b.memory.ram)) == private and bytes(b.memory[0x15a:0x17b]) == smc
            assert N.get(b.memory, 'NmiSkipped') == (skipped+int(kind == 'busyNMI')) & 255
            changed = delta(baseline_native, native(b.memory))
            if kind == 'busyNMI':
                assert audio_changes is not None and audio_pending is None
                at = N.address(b.memory.bundle, 'NmiSkipped')
                assert changed.pop(at) == (skipped, (skipped+1)&255)
                assert all(audio_changes.get(at) == value for at, value in changed.items()), ('Non-audio native busy-NMI write', before[:2], changed, audio_changes)
                # AudioUpdate's mapper shadow is intentionally restored by
                # ExitNMI after the audio call returns. Every such transient
                # must equal the interrupted value again at the ISR return.
                initial = dict(zip(addresses, baseline_native, strict=True))
                restored = set(audio_changes)-set(changed)
                assert all(b.memory[at] == initial[at] for at in restored)
                counts['busyNMI_all_other_native_changes_owned_by_AudioUpdate'] += 1
            else:
                assert not changed
            if len(examples) < 4:
                examples.append(dict(kind=kind, PC=before[0], audio_changed_addresses=list(changed)))
            control.pc = before[0]  # Resume the identical paused foreground.
            Verify.equal(b, control, ('Matched native-PC ISR result', kind, before[:2]))
            for cpu in (b, control):
                Verify.finish(cpu, original.memory.combined_terminal)
            Verify.equal(b, control, ('Matched native-PC full Main', kind, before[:2]))
            counts[kind] += 1
    assert counts['IRQ'] and counts['busyNMI']
    return dict(cuts=len(cuts), cases=dict(counts), minimum_ISR_SP=minimum,
        native_side_effect_examples=examples, busy_NMI_exact_counter_increment=True,
        exact_full_native_WRAM_PPU_VRAM_and_Main_comparison=True,
        reference='Staged IdleLoop PC with identical reached AXY/P/SP/mappings/native data; real ISR, no foreground instruction at that PC.',
        actual_native_ISR_and_Main_continuation=True,
        scope='Declared busy-NMI/IRQ instruction cuts on the genuine contact suffix, not physical timing.')


def controller(raw, *, frozen_narrow=False):
    """Standalone normal-menu native witness; root owns any Mesen invocation."""
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    from run_sonic_original_motion_smoke_1122 import value
    assert H(raw) == C.CANDIDATE
    parent = C.inverse(raw)
    p = C.program(parent)
    bundle = dict(W.Symbols.bundle(), raw=raw)
    names = ('SelectedCharacter', 'GameEngineSubroutine', 'NumberofLives', 'PlayerStatus',
        'PlayerSize', 'Player_X_Position', 'Player_PageLoc', 'Player_Y_Position', 'Player_State',
        'ScreenLeft_X_Pos', 'ScreenLeft_PageLoc', 'Enemy_Flag', 'Enemy_ID', 'Enemy_State',
        'Enemy_X_Position', 'Enemy_PageLoc', 'Enemy_Y_Position', 'BlockBounceTimer',
        'WorldNumber', 'LevelNumber', 'CheatInvincible', 'CheatStartLevel',
        'CrossoverMenuState', 'CrossoverMenuIndex', 'GamePauseStatus')
    capture = [i['pc'] for i in p['instructions'] if i['op'] == 'STA' and i['operand'] == 0xc4b6]
    assert len(capture) == 1
    config = dict(sha=H(raw), fields={n: W.address(bundle, n) for n in names},
        cookie=list(raw[C.COOKIE_AT:C.COOKIE_AT+16]), capture=capture[0],
        flush=p['symbols']['DkHeadFlush'], fall=p['symbols']['OriginalFall']+2,
        effect=p['symbols']['NativeHeadEffect'],
        effect_offset=W.location(bundle, 'NativeRarePlayerHeadCollisionCore')-16)
    policy = NATIVE_POLICY
    if not frozen_narrow:
        edits = (
            ('local birth,boarded,launch,flushed',
             'local birth,boarded,launch,flushed\nlocal windowNative2={count=0}'),
            (' pose=ram(0x71),age=ram(0x7e)',
             " native_state=r('Player_State'),pose=ram(0x71),age=ram(0x7e)"),
            ('  physical_frames=frame,script_RAM_writes=false',
             '  window_native_state2=windowNative2,physical_frames=frame,script_RAM_writes=false'),
            ("if phase=='left'and xx<=401 then", "if phase=='left'and xx<=402 then"),
            ('xx>=400 and xx<=401 and ram(0x71)==0', 'xx>=400 and xx<=402 and ram(0x71)==0'),
            ("elseif phase=='window'then\n  assert", """elseif phase=='window'then
  if r('Player_State')==2 and windowNative2.last_tick~=ticks then
   windowNative2.count=windowNative2.count+1;windowNative2.last_tick=ticks
   if not windowNative2.first then windowNative2.first=snapshot()end;windowNative2.last=snapshot()
  end
  assert"""),
            ('and(ram(0x14)|ram(0x15))&128==0 then',
             "and ram(0x6c)==1 and r('Player_State')==0 and ram(0x210)==yy+15 and(ram(0x14)|ram(0x15))&128==0 then"),
        )
        for before, after in edits:
            assert policy.count(before) == 1, before
            policy = policy.replace(before, after, 1)
    text = 'local C='+value(config)+'\n'+policy
    if frozen_narrow:
        assert H(text.encode()) == '928f4c2f236d4afea02c1c91c35ef3ffd47aa9e1d1da2f21a9cda277e8a36660'
    assert not any(s in text for s in ('emu.write', 'emu.setState', 'io.open', 'takeScreenshot', 'loadState', 'saveState'))
    LuaRuntime().compile(text)
    return text


NATIVE_POLICY = r'''local L=C.fields
local frame,ticks,bits,game,done=0,0,0,false,false
local phase,phaseAt,hold,rearm,priorTop='approach',0,0,0,nil
local mainPending,workPending,effectPending
local entries,returns,moveCalls,clockCalls=0,0,0,0
local follows,events,heads,effects,falls={},{},{},{},{}
local birth,boarded,launch,flushed
local function read(a)return emu.read(a,emu.memType.nesDebug)end
local function r(n,i)return read(L[n]+(i or 0))end
local function ram(a)return emu.read(2*8192+a,emu.memType.nesWorkRam)end
local function x()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function cam()return r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')end
local function snapshot()return {frame=frame,Main=ticks,x=x(),y=r('Player_Y_Position'),camera=cam(),
 source=ram(0x6b),prior=ram(0x6c),source_y=ram(0x210),facing=ram(0x6d),direction=ram(0x54),
 pose=ram(0x71),age=ram(0x7e),held=ram(0x14),sample=ram(0x15),origin=ram(0x76),
 lives=r('NumberofLives'),status=r('PlayerStatus'),engine=r('GameEngineSubroutine'),phase=phase}end
local function json(v)
 local t=type(v);if t=='nil'then return'null'elseif t=='string'then return string.format('%q',v)
 elseif t~='table'then return tostring(v)end
 local out={};if #v>0 then for _,q in ipairs(v)do out[#out+1]=json(q)end;return'['..table.concat(out,',')..']'end
 for k,q in pairs(v)do out[#out+1]=string.format('%q',tostring(k))..':'..json(q)end
 table.sort(out);return'{'..table.concat(out,',')..'}'
end
local function finish(ok,why)
 if done then return end;done=true;bits=0
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=why,ROM_SHA256=C.sha,controller_only=true,
  terminal=snapshot(),birth=birth,boarded=boarded,launch=launch,events=events,heads=heads,
  effects=effects,original_falls=falls,source_entries=entries,source_returns=returns,
  move_calls=moveCalls,clock_calls=clockCalls,post_effect_returns=effects[1]and returns-effects[1].returns or 0,
  physical_frames=frame,script_RAM_writes=false,outputs_written=0}))
 emu.stop(ok and 0 or 1)
end
local function guarded(name,fn)return function(...)
 if done then return end;local ok,why=pcall(fn,...);if not ok then finish(false,name..': '..tostring(why))end
end end
local function mapped(pc,kind,address)local p=emu.convertAddress(pc);return p and p.memType==emu.memType[kind]and p.address==address end
local function private(pc,bank)return mapped(pc,'nesWorkRam',bank*8192+(pc&8191))end
local function active()return r('SelectedCharacter')==40 and r('GameEngineSubroutine')==8 and ram(0x8fe)==2 end
local function actor(i)return {slot=i,id=r('Enemy_ID',i),flag=r('Enemy_Flag',i),state=r('Enemy_State',i),
 x=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),y=r('Enemy_Y_Position',i)}end
local function platform()
 for i=0,5 do local a=actor(i);if a.flag~=0 and a.id==37 and a.x==416 then return a end end
end
local function token()
 local c=emu.getState();local sp=c['cpu.sp'];local pc=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535
 local m=emu.convertAddress(pc);return {pc=pc,sp=(sp+2)&255,kind=m and m.memType,address=m and m.address}
end
local function matches(p,c)
 if not p or c['cpu.pc']~=p.pc or c['cpu.sp']~=p.sp then return false end
 if p.kind then local m=emu.convertAddress(p.pc);assert(m and m.memType==p.kind and m.address==p.address,'Mapped actual return')end
 return true
end
local function follow(pc)
 if follows[pc]then return end;follows[pc]=true
 emu.addMemoryCallback(guarded('return',function()
  local c=emu.getState()
  if matches(workPending,c)then assert(workPending.move and workPending.clock,'Original Move+Clock returned');returns=returns+1;workPending=nil end
  if matches(effectPending,c)then
   local p=effectPending;effectPending=nil
   assert(read(p.cell)==35 and r('BlockBounceTimer')==16,'Actual native brick erase and bounce')
   assert(ram(0x6b)==4 and r('Player_Y_Position')==p.before.y,'Original upward-stop response retained')
   effects[#effects+1]={before=p.before,after=snapshot(),tile=p.tile,cell=p.cell,after_tile=read(p.cell),bounce=r('BlockBounceTimer'),returns=returns}
  end
  if matches(mainPending,c)then mainPending=nil;ticks=ticks+1 end
 end),emu.callbackType.exec,pc)
end
local function drive()
 assert(ticks<2200 and r('NumberofLives')==2 and ram(0x68)==0 and ram(0x6b)~=5 and r('PlayerStatus')==0,'Healthy finite unpowered route')
 assert(r('WorldNumber')==0 and r('LevelNumber')==0 and r('CheatInvincible')==0 and r('CheatStartLevel')==0,'Natural Easy1-1')
 for bank=2,3 do for i,v in ipairs(C.cookie)do assert(emu.read(bank*8192+0x1fdf+i,emu.memType.nesWorkRam)==v,'Actual owner header')end end
 local xx,yy=x(),r('Player_Y_Position');local p=platform();local ground=ram(0x6b)==1 and r('Player_State')==0
 if p and birth then assert(p.slot==birth.slot and read(0x646+p.slot)==5,'Committed32px DK helper collision box')end
 for i=0,5 do local a=actor(i);assert(a.flag==0 or a.id~=37 or a.x~=336,'No private336 helper');assert(a.flag==0 or a.id~=46,'No injected/reward item in brick test')end
 local ride=p and ram(0x6b)==1 and yy<176 and yy+32==p.y
 if phase=='approach'and xx>=426 then phase='board';phaseAt=ticks end
 if phase=='board'and ride then boarded=snapshot();boarded.actor=p;phase='left';phaseAt=ticks;hold=0 end
 if phase=='left'and xx<=401 then phase='window';phaseAt=ticks;hold=0;priorTop=p and p.y end
 if phase=='approach'then
  assert(ticks-phaseAt<1600,'Approach bound')
  for i=0,5 do local a=actor(i);local dx=a.x-xx
   if ground and ticks>=rearm and a.flag==1 and(a.id==2 or a.id==6)and a.state&32==0 and a.y>=172 and dx>=8 and dx<=30 then hold=ticks+8;rearm=ticks+47 end
  end
  return 1|(ticks<hold and 128 or 0)
 elseif phase=='board'then
  assert(ticks-phaseAt<400,'Board bound')
  if p and ground and ticks>=rearm and p.y>=192 and p.y<=208 then hold=ticks+8;rearm=ticks+47 end
  return ticks<hold and 128 or 0
 elseif phase=='left'then assert(ticks-phaseAt<90,'Left staging bound');return 2
 elseif phase=='window'then
  assert(ticks-phaseAt<400,'Existing416 ascent window')
  if p and ride and p.y>=178 and p.y<=180 and priorTop and p.y<priorTop and(ram(0x14)|ram(0x15))&128==0 then
   assert(xx>=400 and xx<=401 and ram(0x71)==0,'Genuine supported ordinary launch')
   launch=snapshot();launch.actor=p;phase='bump';phaseAt=ticks;hold=ticks+8;return 130
  end
  priorTop=p and p.y;return 0
 end
 assert(ticks-phaseAt<110,'Underside witness bound');return 2|(ticks<hold and 128 or 0)
end
emu.addMemoryCallback(guarded('main entry',function()
 if not game or not active()or not private(0xd65e,2)then return end
 assert(not mainPending,'No nested motor');mainPending=token();follow(mainPending.pc)
end),emu.callbackType.exec,0xd65e)
emu.addMemoryCallback(guarded('source entry',function()
 if not game or not active()or not private(0xb8f0,3)then return end
 assert(not workPending,'No nested source work');entries=entries+1;workPending=token();follow(workPending.pc)
end),emu.callbackType.exec,0xb8f0)
emu.addMemoryCallback(guarded('move',function()if workPending and private(0xa2e8,3)then workPending.move=true;moveCalls=moveCalls+1 end end),emu.callbackType.exec,0xa2e8)
emu.addMemoryCallback(guarded('clock',function()if workPending and private(0xaf2d,3)then workPending.clock=true;clockCalls=clockCalls+1 end end),emu.callbackType.exec,0xaf2d)
emu.addMemoryCallback(guarded('birth',function()
 if not game or not active()or not private(0xd1f0,2)then return end
 local i=emu.getState()['cpu.x'];if i>5 then return end;local a=actor(i)
 if a.id~=37 or a.x~=416 then return end
 assert(not birth and a.flag==1 and a.y==192 and read(0x646+i)==6 and a.x-cam()>=256 and a.x-cam()<=287,'Real offscreen stock416 constructor')
 birth={frame=frame,Main=ticks,slot=i,left=416,center=432,initial_top=192,constructor_box=6,collision_width=32,camera=cam()}
end),emu.callbackType.exec,0xd1f0)
emu.addMemoryCallback(guarded('accepted head',function()
 if not game or not active()or not private(C.capture,3)then return end
 local v=snapshot();local left,top,right,bottom=ram(0x42)+cam(),ram(0x43),ram(0x44)+cam(),ram(0x45)
 assert(#heads==0 and phase=='bump'and v.source==3 and v.age>0 and left==384 and right==399 and top==144 and bottom==159,'Real original underside384 contact')
 assert(bottom-ram(0x3f)>=0 and bottom-ram(0x3f)<=1 and bottom<v.origin,'Original entered top contact')
 v.world_cell={left,top,right,bottom};v.query={ram(0x3e),ram(0x3f),ram(0x40),ram(0x41)};heads[1]=v
end),emu.callbackType.exec,C.capture)
emu.addMemoryCallback(guarded('original fall',function()
 if not game or not active()or not private(C.fall,3)then return end
 assert(heads[1]and ram(0x6b)==3 and emu.getState()['cpu.a']==4,'Original fall store preserved');falls[#falls+1]=snapshot()
end),emu.callbackType.exec,C.fall)
emu.addMemoryCallback(guarded('flush',function()
 if not game or not active()or not private(C.flush,3)or ram(0x4b6)==0 then return end
 assert(heads[1]and #falls==1 and ram(0x4b6)==144 and ticks==heads[1].Main,'Exact same-Main event commit');flushed=true
end),emu.callbackType.exec,C.flush)
emu.addMemoryCallback(guarded('native effect',function()
 if not game or not mapped(C.effect,'nesPrgRom',C.effect_offset)then return end
 local c=emu.getState();assert(flushed and #effects==0 and not effectPending and c['cpu.a']==81 and ticks==heads[1].Main and ram(0x4b6)==0,'One consumed native brick effect')
 effectPending=token();effectPending.before=snapshot();effectPending.tile=c['cpu.a'];effectPending.cell=read(9)+256*read(10)+read(5)
 assert(effectPending.cell==0x448,'Exact authored brick384 cell');follow(effectPending.pc)
end),emu.callbackType.exec,C.effect)
local function wait(pred)for _=1,1000 do if pred()then return end;coroutine.yield()end;error('Menu readiness bound')end
local function press(pad)bits=pad;for _=1,4 do coroutine.yield()end;bits=0;for _=1,8 do coroutine.yield()end end
local title=coroutine.create(function()
 assert((os.getenv('SMB_STDOUT_ROM_SHA')or C.sha)==C.sha,'Exact head-bridge image')
 wait(function()return frame>=70 and read(0x6004)==1 and r('GamePauseStatus')==0 end)
 press(16);wait(function()return r('CrossoverMenuState')==2 end)
 for _,pad in ipairs({4,4,1,1,1,4})do press(pad)end
 assert(r('CrossoverMenuIndex')==27 and r('SelectedCharacter')==28);press(32);assert(r('SelectedCharacter')==40);press(16);wait(active);game=true
end)
if CPU_CONTROLLER_OPENING then frame=541;game=true end
emu.addEventCallback(guarded('input',function()
 if game and active()then bits=drive()end
 emu.setInput({right=bits&1~=0,left=bits&2~=0,down=bits&4~=0,up=bits&8~=0,start=bits&16~=0,select=bits&32~=0,a=bits&128~=0,b=bits&64~=0},0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guarded('frame',function()
 frame=frame+1;assert(frame<12000,'Physical frame bound')
 if not game then local ok,why=coroutine.resume(title);assert(ok,why);return end
 assert(r('NumberofLives')==2 and ram(0x6b)~=5 and r('GameEngineSubroutine')~=11,'Healthy original response')
 if effects[1]and returns-effects[1].returns>=25 and not mainPending and not workPending and not effectPending then
  assert(birth and boarded and launch and #heads==1 and #falls==1 and #effects==1 and ram(0x6b)==1 and ram(0x6c)==1 and ram(0x68)==0 and r('PlayerStatus')==0,'Accepted contact/effect and25 returned source movements')
  finish(true,'Original underside brick384 hit, native bump and25 source returns')
 end
end),emu.eventType.endFrame)
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--fixtures', action='store_true')
    ap.add_argument('--interrupts', action='store_true')
    args = ap.parse_args()
    installed = C.M.ROM.read_bytes()
    parent = C.inverse(installed) if H(installed) == C.CANDIDATE else installed
    candidate, composition = C.proposal(parent)
    assert C.inverse(candidate) == parent
    print('DK HEAD COMPOSE '+json.dumps({k: v for k, v in composition.items() if k != 'labels'}, separators=(',', ':')), flush=True)
    before, _ = contact_route(parent)
    print('DK HEAD BASELINE '+json.dumps({k: v for k, v in before.items() if k != 'curve'}, separators=(',', ':')), flush=True)
    after, cuts = contact_route(candidate, collect_cuts=args.interrupts)
    assert before['prefix'] == after['prefix'], 'Original approach/motor/support changed'
    report = dict(passed=True, composition=composition, baseline=before, candidate=after,
        bindings={Path(p).name: H(Path(p).read_bytes()) for p in (C.__file__, __file__)}, outputs=0, Mesen=False)
    if args.fixtures:
        report['fixtures'] = fixtures(parent, candidate, composition)
    if args.interrupts:
        report['interrupts'] = interrupts(cuts)
    receipt = H(json.dumps(report, sort_keys=True, separators=(',', ':')).encode())
    compact = {k: v for k, v in after.items() if k != 'curve'}
    compact.update(receipt_SHA256=receipt, bindings=report['bindings'])
    if args.fixtures:
        compact['fixtures'] = report['fixtures']
    if args.interrupts:
        compact['interrupts'] = report['interrupts']
    print('DK HEAD PASS '+json.dumps(compact, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
