"""Private draw controller: reuse backward recovery after early-riser failure.

No gameplay bytes, original controller, shared runner or native files change.
The bounded proof exercises the emitted Lua with declared mock stair inputs;
Root owns the real geometry replay and Mesen queue.
"""
from hashlib import sha256
import json
from pathlib import Path

import replay_dkjr_first_riser_recovery_1123 as Previous

H = lambda value: sha256(value).hexdigest()
PREVIOUS_SHA = 'f1c520e55b4dc42601d0a7180c17ef6d916958f76325b3d2abe63aa959d717f5'
PRIOR_PINS = dict(parent='66245a5e59d293dd62a848a4dfaa49bdc10023275e3f6bd2b43e0d5b05f47987',
                  negative='e1ad034cbfbc455f4184fcce2396fda0675df80e71031ccc0cf1f6ef59df7305',
                  recovery='4dd52e15a897f90c1ce546987d17716b793cf678a9fa85366005945a783402f3')
OLD = Previous.NEW
NEW = OLD.replace('finalRiser==1', 'finalRiser<=3')
# The optional1113 runner excluded riser3 from this wait, but that exception
# is absent from the pinned current root6699/ffd controller lineage.
CURRENT_WAIT = '(fast or finalRiser==1) and player>=takeoff-2'


def controllers(raw, candidate=None):
    assert H(Path(Previous.__file__).read_bytes()) == PREVIOUS_SHA
    prior = Previous.controllers(raw, candidate)
    assert {k: H(v) for k, v in prior.items()} == PRIOR_PINS
    first = prior['recovery']
    assert first.count(OLD.encode()) == first.count(CURRENT_WAIT.encode()) == 1
    updated = first.replace(OLD.encode(), NEW.encode(), 1)
    assert updated.replace(NEW.encode(), OLD.encode(), 1) == first
    assert updated.count(CURRENT_WAIT.encode()) == 1
    assert updated.count(b'{2939,2944,2941},') == first.count(b'{2939,2944,2941},') == 1
    Previous.Draw.Cadence.LuaRuntime().compile(updated.decode())
    return dict(parent=prior['parent'], negative=prior['negative'], first=first, recovery=updated)


def trace(text, riser, *, attempts=0, x_offset=0, y_offset=0,
          source=1, native=0, walk=True, limit=100):
    begin = text.index(" if phase=='final-stairs'then\n")
    end = text.index(" if phase=='final-cap'then\n", begin)
    fragment = text[begin:end]
    lua = Previous.Draw.Cadence.LuaRuntime(unpack_returned_tuples=True)
    anchor = 2912 + 16*(riser-1)
    lua.globals().mock = lua.table_from(dict(x=anchor+x_offset,
        y=144-16*(riser-1)+y_offset, facing=1, source=source, native=native,
        riser=riser, attempts=attempts, camera=anchor-80))
    drive = lua.execute('''
local fast=true
local finalRiser,finalRiserStart,finalRiserAttempts=mock.riser,mock.attempts>0 and 0 or nil,mock.attempts
local finalWaitX,finalWaitStart,finalLandAt,rootFinalPrep
local finalLaunches={{2912,2912,2907},{2923,2928,2925},{2939,2944,2941},
 {2955,2960,2957},{2971,2976,2973},{2987,2991,2992,2989}}
local phase,hold,rearm,updates='final-stairs',0,0,0
local events={}
local function camera()return mock.camera end
local function read()return mock.native end
local function ram(bank,at)
 if at==0x6b or at==0x6c then return mock.source end
 if at==0x6d then return mock.facing end
 return 0
end
local function remember(name)events[#events+1]={update=updates,name=name,x=mock.x,y=mock.y}end
local function setPhase(name)phase=name end
return function(age)
 updates=age;local player,y=mock.x,mock.y
 local settled=ram(2,0x6b)==1 and read(0x1e)==0
 local right,left,bits=false,false,0
 local function drive()
''' + fragment + '''
 bits=(right and 1 or 0)|(left and 2 or 0)|(updates<hold and 128 or 0)
 end
 drive()
 return bits,finalRiser,events
end''')
    rows, events, error = [], [], None
    for age in range(limit):
        try:
            pad, _, event_rows = drive(age)
        except Exception as exc:
            error = str(exc).split('\n', 1)[0]
            break
        events = Previous.records(event_rows)
        rows.append(dict(update=age, pad=pad, x=lua.globals().mock.x))
        if any(e['name'].startswith('final-backward-jump-') for e in events):
            assert rows[-1]['pad'] == 129 and [r['pad'] for r in rows[-5:-1]] == [0]*4
            assert events[-1]['original_facing'] == 0 and events[-1]['takeoff_stage'] == anchor-12
            assert rows[-1]['x'] == anchor-12
            break
        if walk and pad == 2:
            lua.globals().mock.x -= 1
            lua.globals().mock.facing = 0
    return dict(events=events, pads=rows, error=error)


def qualify(programs):
    before, after = programs['first'].decode(), programs['recovery'].decode()
    cases, rows = 0, []
    for riser in range(1, 7):
        old, new = trace(before, riser), trace(after, riser)
        if riser in (2, 3):
            assert old['error'] and f'No height gained on final riser {riser}' in old['error']
            assert not new['error'] and len(new['events']) == 2
            assert new['events'][0]['name'] == f'final-stair-jump-{riser}'
            assert new['events'][1]['name'] == f'final-backward-jump-{riser}'
        else:
            assert old == new, ('Changed existing riser path', riser)
        rows.append(dict(riser=riser, prior_error=old['error'], events=new['events'],
                         last_pads=new['pads'][-5:]))
        cases += 1
    blocked = trace(after, 3, x_offset=-1, walk=False, limit=12)
    assert not blocked['events'] and {r['pad'] for r in blocked['pads']} == {1}
    failed = trace(after, 3, attempts=1, x_offset=-1)
    assert failed['events'][0]['name'] == 'final-backward-jump-3' and not failed['error']
    cases += 2
    for source, native, y_offset in ((3, 0, 0), (1, 2, 0), (1, 0, -16)):
        guarded = trace(after, 3, attempts=1, source=source, native=native,
                        y_offset=y_offset, limit=3)
        assert not guarded['events'] and not guarded['error']
        cases += 1
    return dict(mock_cases=cases, actual_emitted_fragment=True, no_height_cases=rows,
                observed_2943_failed_attempt=failed['events'],
                current_early_wait_predicate_unchanged=True,
                historical_1113_third_riser_exception_not_linked_or_reintroduced=True,
                first_attempt_required=True, airborne_native_state_and_upper_floor_guards=True,
                real_geometry_or_native_recovery_claim=False)


def main():
    raw = Previous.Draw.Cadence.Timing.ROM.read_bytes()
    print('EARLY_RISERS_PHASE binding', flush=True)
    programs = controllers(raw)
    receipt = dict(parent_SHA256=H(raw), candidate_SHA256=Previous.Draw.CANDIDATE,
                   controller_SHA256={k: H(v) for k, v in programs.items()},
                   qualification=qualify(programs), new_game_bytes=0, new_helpers=0,
                   outputs_written=0)
    encoded = json.dumps(receipt, sort_keys=True, separators=(',', ':'))
    print('EARLY_RISERS_CONTROLLER ' + encoded, flush=True)
    print('EARLY_RISERS_RECEIPT_SHA256 ' + H(encoded.encode()), flush=True)


if __name__ == '__main__':
    main()
