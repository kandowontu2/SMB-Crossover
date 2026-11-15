"""Actual opcode lifecycle parity: ordinary pause and explicit owning death API."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import check_battletoads_native_service_model_1114 as M

W,N,Frames=M.W,M.N,M.Frames


def run(raw):
    _,info=M.recipe(raw);pair=[M.cold(raw,enabled=False),M.cold(raw)];phases=[]
    for phase,pad,count in(('walk',1,32),('pause_edge',16,1),('paused',0,64),('resume_edge',16,1),('resumed',0,8)):
        states=set()
        for _ in range(count):
            for m in pair:m.controller_pad=pad;Frames.frame(m,whole_pass=True)
            M.compare(pair,180);states.add(N.get(pair[1],'GamePauseStatus'))
        phases.append(dict(phase=phase,Main=count,pad=pad,pause_values=sorted(states),state=M.Profile.state(pair[1])))
    assert all(v&1 for q in phases if q['phase']=='paused'for v in q['pause_values'])
    assert not N.get(pair[1],'GamePauseStatus')&1
    retired=[N.fork(m)for m in pair]
    for m in retired:N.invoke(m,'BtRetire');assert m.ram[3][0x1fe0]==0
    M.compare(retired,180)
    def component(arenas,results,label):
        # The arenas retain dead stack from the genuine preceding Main,
        # whose observed minimum SP184 is below these shallow calls.
        checked=[dict(row,minimum_SP=min(184,row['minimum_SP']))for row in results]
        M.Research.compare(arenas,checked,label)
    for slot in(0,2,9,29):
        arenas=[N.fork(m)for m in retired];out=[M.Research.execute(m,'slot'+str(slot),0x21,0)for m in arenas]
        component(arenas,out,'retired slot'+str(slot));assert not out[1]['P']&1
    # A genuine owning API request, not an enemy/pit collision. No direct
    # health, actor, engine, terrain, position or ability fields are written.
    death=[N.fork(m)for m in pair];out=[M.Research.execute(m,'slot7',0x21,0)for m in death]
    component(death,out,'actual public DeathStart API');requested=M.Profile.state(death[1])
    events=[];seen=Counter()
    for tick in range(360):
        for m in death:m.controller_pad=0;Frames.frame(m,whole_pass=True)
        M.compare(death,180);state=M.Profile.state(death[1]);seen[state['engine']]+=1
        if tick<4 or tick%40==39 or state['lives']<2:
            events.append(dict(Main=tick+1,state=state,cookie=bytes(death[1].ram[3][0x1fe0:0x1ff0]).hex()))
        if state['lives']<2 and state['engine']==8 and state['y']==176:break
    return dict(proposal=info,genuine_cold_and_ordinary_pause_resume=phases,
        actual_retirement_parity=True,retired_private0_2_and_NoOp9_29_C0_parity=True,
        component_stack_comparison_uses_proven_prior_Main_SP184=True,
        death_scope='Explicit public owning DeathStart slot7; component request, not natural enemy/pit death',
        actual_death_API_AXYP_SP_and_RAM_exact=True,after_death_request=requested,
        following_ordinary_neutral_Main=tick+1,death_engine_histogram=dict(seen),events=events,
        full_parent_overlay_lifecycle_state_maps_SMC_VRAM_exact=True,gameplay_state_seeds=0,
        ROM_composed=False,outputs=0,Mesen_run=False)


if __name__=='__main__':
    raw=M.Input.ROM.read_bytes();M.typed(raw)
    def forbid(*a,**k):raise RuntimeError('Lifecycle attempted file/Mesen output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(M.Cold.Runner.Native,'run',forbid):q=run(raw)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
