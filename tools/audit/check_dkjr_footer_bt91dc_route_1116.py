"""Actual currenta3fb unchanged-input fourth crossing, bounded source only."""
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json

import replay_dkjr_footer_bt91dc_current_1116 as F
import check_dkjr_carry_camera_route_1116 as R

C,N,B=F.C,R.N,R.B
H=lambda value:sha256(value).hexdigest()


def main():
    parent=C.BT.ROM.read_bytes();raw,composition=C.proposal(parent);assert C.inverse(raw)==parent
    text=F.source_controller(raw);opening,m=R.cold(raw)
    tick=0;positions=Counter();first=None;last=None;terminal=None
    class Crossed(Exception):pass
    def view(memory):
        r=memory.ram[2]
        return dict(sourceX=r[0x213],sourceY=r[0x210],origin=r[0x76],limit=r[0x7b],**B.state(memory))
    def observe(memory,c):
        nonlocal first,last
        tag=memory.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        if(tag,c.pc)==(199,0xac29)and c.x<6:
            world=N.get(memory,'Enemy_X_Position',c.x)+256*N.get(memory,'Enemy_PageLoc',c.x)
            positions[world]+=1
            if world==944:
                row=dict(tick=tick,slot=c.x,plane=N.get(memory,'Enemy_Y_Position',c.x),**view(memory))
                if first is None:first=row
                last=row
    output=__import__('sys').stdout
    def after(memory):
        nonlocal tick,terminal
        tick+=1
        if tick%1000==0:print('DKJR_CURRENT_FOURTH_PROGRESS '+str(tick),file=output,flush=True)
        state=B.state(memory)
        assert state['lives']==2 and state['source_state']!=5,('Actual current prefix injury',tick,state)
        if positions[944]>=3 and state['x']>=976 and state['y']==176 and state['state']==0 and state['source_state']==1:
            terminal=view(memory);raise Crossed()
    with redirect_stdout(io.StringIO()):
        try:result=B.route(m,raw,3500,controller_text=text,observe_extra=observe,after_frame=after)
        except Crossed:result=None
    assert terminal is not None,('Current fourth crossing not qualified',tick,B.state(m),(result or{}).get('receipt',{}).get('reason'))
    report=dict(passed=True,composition=composition,actual_CPU_ROM_SHA256=H(raw),controller_SHA256=H(text.encode()),
        opening=opening,source_updates=tick,actual_native_position_counts=dict(positions),
        first944=first,last944=last,terminal=terminal,ordinary_ed3e_inputs_unchanged=True,
        game_state_seeds=False,full_stage_or_25grounded12_qualification=False,
        scope='Actual current a3fb genuine compiled cold and all four early helper-assisted pipes through living grounded exit beyond fourth cap; no later stairs/native claim.',
        outputs=0,native_claim=False)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_CURRENT_FOURTH '+encoded,flush=True);print('DKJR_CURRENT_FOURTH_SHA256 '+H(encoded.encode()),flush=True)


if __name__=='__main__':main()
