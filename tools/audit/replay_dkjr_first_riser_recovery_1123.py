"""Separate ordinary-input first-riser fallback for the private draw proposal.

Keep the installed full controller and its draw-only rebind byte-for-byte.
Only a failed first-riser attempt admits the existing backward-jump controls.
This module never stages a ROM, launches Mesen, or writes generated files.
"""
import argparse
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from unittest.mock import patch

import compose_dkjr_mushroom_slot_order_1123 as Parent
import probe_special_draw_routing_1123 as Draw

H = lambda value: sha256(value).hexdigest()
OLD = '   if finalRiser>=4 and finalRiser<=6 then\n'
NEW = '   if (finalRiser==1 and finalRiserAttempts>0 or finalRiser>=4) and finalRiser<=6 then\n'


def controllers(raw, candidate=None):
    """Return unchanged parent/negative plus a separate controller-only branch."""
    assert H(raw) == Parent.CANDIDATE
    expected, _ = Draw.proposal(raw)
    candidate = expected if candidate is None else candidate
    assert candidate == expected and Draw.inverse(candidate) == raw
    baseline = Parent.full_controller(raw).encode()
    assert baseline.count(Parent.CANDIDATE.encode()) == 2
    negative = baseline.replace(Parent.CANDIDATE.encode(), H(candidate).encode())
    assert negative.count(OLD.encode()) == 1
    recovery = negative.replace(OLD.encode(), NEW.encode(), 1)
    assert recovery.replace(NEW.encode(), OLD.encode(), 1) == negative
    for text in (baseline, negative, recovery):
        assert not any(s in text for s in (b'emu.write', b'emu.setState', b'io.open',
                                          b'takeScreenshot', b'loadState', b'saveState'))
        Draw.Cadence.LuaRuntime().compile(text.decode())
    return dict(parent=baseline, negative=negative, recovery=recovery)


def policy(text, model=None):
    """Execute the emitted final-stair fragment, with read-only native state."""
    begin = text.index(" if phase=='final-stairs'then\n")
    end = text.index(" if phase=='final-cap'then\n", begin)
    fragment = text[begin:end]
    lua = Draw.Cadence.LuaRuntime(unpack_returned_tuples=True)
    if model is not None:
        N = Parent.Check.N
        lua.globals().read = lambda at: model[at]
        lua.globals().ram = lambda bank, at: model.ram[bank][at]
        lua.globals().camera = lambda: N.get(model, 'ScreenLeft_X_Pos') + 256*N.get(model, 'ScreenLeft_PageLoc')
        lua.globals().nativeX = lambda: N.get(model, 'Player_X_Position') + 256*N.get(model, 'Player_PageLoc')
        lua.globals().nativeY = lambda: N.get(model, 'Player_Y_Position')
    else:
        lua.execute('''mock={x=2911,y=144,facing=1,held=0,fresh=0}
function read()return 0 end
function ram(bank,at)
 if at==0x6b or at==0x6c then return 1 end
 if at==0x6d then return mock.facing end
 if at==0x14 then return mock.held end
 if at==0x15 then return mock.fresh end
 return 0
end
function camera()return 2832 end
function nativeX()return mock.x end
function nativeY()return mock.y end''')
    code = '''local fast=true
local finalRiser,finalRiserStart,finalRiserAttempts=1,nil,0
local finalWaitX,finalWaitStart,finalLandAt,rootFinalPrep
local finalLaunches={{2912,2912,2907},{2923,2928,2925},{2939,2944,2941},
 {2955,2960,2957},{2971,2976,2973},{2987,2991,2992,2989}}
local phase,hold,rearm,updates='final-stairs',0,0,0
local events={}
local function remember(name)events[#events+1]={update=updates,name=name,x=nativeX(),y=nativeY()}end
local function setPhase(name)phase=name end
return function(age)
 updates=age;local player,y=nativeX(),nativeY()
 local settled=ram(2,0x6b)==1 and read(0x1e)==0
 local right,left,bits=false,false,0
 local function drive()
''' + fragment + '''
 bits=(right and 1 or 0)|(left and 2 or 0)|(updates<hold and 128 or 0)
 end
 drive()
 return bits,finalRiser,events
end'''
    return lua, lua.execute(code), H(fragment.encode())


def records(rows):
    return [dict(row) for row in rows.values()]


def mock_trace(text, recover):
    lua, drive, digest = policy(text)
    rows, tail, error, launch = [], [], None, None
    mock = lua.globals().mock
    for age in range(201):
        try:
            pad, _, events = drive(age)
        except Exception as exc:
            error = str(exc).split('\n', 1)[0]
            break
        rows = records(events)
        tail.append(dict(update=age, pad=pad, x=mock.x, facing=mock.facing))
        tail = tail[-8:]
        if any(r['name'] == 'final-backward-jump-1' for r in rows):
            launch = dict(tail[-1])
            break
        if recover and pad == 2:
            mock.x -= 1
            mock.facing = 0
    if recover:
        assert not error and launch and launch['pad'] == 129 and launch['x'] == 2900 and launch['facing'] == 0
    else:
        assert error and 'No height gained on final riser 1' in error
        assert len(rows) == 4 and {r['x'] for r in rows} == {2911}
    return dict(actual_fragment_SHA256=digest, mock_no_height_domain=True,
                events=rows, tail=tail, error=error, backward_launch=launch)


def state(m):
    row = Parent.Check.Head.state(m)
    row.update(native_state=Parent.Check.N.get(m, 'Player_State'), fresh=m.ram[2][0x15],
               source_rect=list(m.ram[2][0x3e:0x46]))
    return row


def linked(raw, candidate, programs):
    """Natural menu/prefix; clone only after reaching the actual first riser."""
    Check = Parent.Check
    m, opening = Check.Head.cold(candidate)
    ticks, branch = 0, None
    output = __import__('sys').stdout
    class AtBranch(Exception):
        pass
    def after(mem):
        nonlocal ticks, branch
        ticks += 1
        v = state(mem)
        if ticks % 1200 == 0:
            print('FIRST_RISER_PREFIX ' + json.dumps(dict(Main=ticks, state=v)), file=output, flush=True)
        if 2909 <= v['x'] <= 2912 and v['y'] == 144 and v['source'] == v['prior'] == 1 and v['native_state'] == 0:
            branch = Check.Route.L.clone(mem)
            raise AtBranch
    with patch.object(Check.Route.Frames, 'frame', Check.normal_frame):
        with redirect_stdout(io.StringIO()):
            try:
                Check.Route.route(m, candidate, 12000,
                                  controller_text=programs['negative'].decode(), after_frame=after)
            except AtBranch:
                pass
    assert branch is not None, ('Natural first-riser prefix not reached', ticks, state(m))
    rows = []
    for name in ('negative', 'recovery'):
        q = Check.Route.L.clone(branch)
        _, drive, fragment = policy(programs[name].decode(), q)
        events, trace, error, passed, seen_jump = [], [], None, False, False
        for age in range(220):
            before = state(q)
            try:
                pad, riser, event_rows = drive(age)
            except Exception as exc:
                error = str(exc).split('\n', 1)[0]
                break
            events = records(event_rows)
            q.controller_pad = pad
            Check.normal_frame(q)
            v = state(q)
            if age < 4 or pad != trace[-1]['pad'] or v['source'] != before['source'] or v['y'] != before['y'] or age % 12 == 0:
                trace.append(dict(update=age, pad=pad, **v))
            seen_jump |= bool(v['fresh'] & 128 and v['source'] == 3)
            if v['x'] >= 2912 and v['y'] == 128 and v['source'] == v['prior'] == 1 and v['native_state'] == 0:
                passed = True
                break
            assert v['lives'] == 2 and v['source'] != 5 and v['engine'] != 11, (name, age, v)
        rows.append(dict(branch=name, passed=passed, updates=age+1, accepted_fresh_jump=seen_jump,
                         actual_fragment_SHA256=fragment, events=events, trace=trace,
                         error=error, final=state(q)))
        print('FIRST_RISER_LINKED_BRANCH ' + json.dumps(rows[-1], separators=(',', ':')), flush=True)
    assert rows[1]['passed'], 'Recovery did not reach the real first upper surface'
    return dict(opening=opening, genuine_prefix_Main=ticks, initial=state(branch), branches=rows,
                ordinary_inputs_only=True, gameplay_or_geometry_writes=False,
                full_stage_or_physical_cadence_claim=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--linked', action='store_true')
    args = parser.parse_args()
    raw = Draw.Cadence.Timing.ROM.read_bytes()
    candidate, _ = Draw.proposal(raw)
    print('FIRST_RISER_PHASE binding ' + H(candidate), flush=True)
    programs = controllers(raw, candidate)
    receipt = dict(parent_SHA256=H(raw), candidate_SHA256=H(candidate),
                   controller_SHA256={k: H(v) for k, v in programs.items()},
                   negative=mock_trace(programs['negative'].decode(), False),
                   recovery=mock_trace(programs['recovery'].decode(), True),
                   new_game_bytes=0, new_helpers=0, outputs_written=0)
    print('FIRST_RISER_CONTROLLER ' + json.dumps(receipt, separators=(',', ':')), flush=True)
    if args.linked:
        receipt['linked'] = linked(raw, candidate, programs)
    encoded = json.dumps(receipt, sort_keys=True, separators=(',', ':'))
    print('FIRST_RISER_RECEIPT_SHA256 ' + H(encoded.encode()), flush=True)


if __name__ == '__main__':
    main()
