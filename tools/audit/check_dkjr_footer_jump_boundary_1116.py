"""Ordinary-input jump boundary from one genuine first944 carry; no overlay."""
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path
import argparse

import check_dkjr_carry_camera_route_1116 as R

C,N,B=R.C,R.N,R.B
L=R.Cold.H.L
H=lambda value:sha256(value).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--parent',type=Path,required=True)
    args=ap.parse_args();parent=args.parent.read_bytes();raw,composition=C.proposal(parent)
    _,m=R.cold(raw);slot=None;updates=0
    class Captured(Exception):pass
    output=__import__('sys').stdout
    def prefix(memory,c):
        nonlocal slot
        tag=memory.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        if(tag,c.pc)==(199,0xac29) and c.x<6 and N.get(memory,'Enemy_ID',c.x)==37:
            if N.get(memory,'Enemy_X_Position',c.x)+256*N.get(memory,'Enemy_PageLoc',c.x)==944:slot=c.x
    def after(memory):
        nonlocal updates
        updates+=1
        if updates%1000==0:print('DKJR_FOOTER_JUMP_PROGRESS '+str(updates),file=output,flush=True)
        if slot is not None:raise Captured()
    with redirect_stdout(io.StringIO()):
        try:B.route(m,raw,4500,controller_text=R.F.source_controller(raw),observe_extra=prefix,after_frame=after)
        except Captured:pass
    assert slot is not None and N.get(m,'PlatformCollisionFlag',slot)==slot
    before=dict(B.state(m),previousAB=N.get(m,'PreviousA_B_Buttons'),
        held=N.get(m,'SavedJoypad1Bits'),passenger=N.get(m,'PlatformCollisionFlag',slot),slot=slot)
    assert not before['held']&128
    rows=[]
    for direction in(0,1,2):
        q=L.clone(m);counts=Counter();first=None;callback=[]
        for tick in range(12):
            q.controller_pad=128|direction
            def watch(memory,c):
                nonlocal first
                tag=memory.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
                if(tag,c.pc)==(2,0xd65e):counts['motor']+=1
                if(tag,c.pc)==(128,0xb453) and c.x==slot:
                    phase=memory.ram[2][0x6b];vy=N.get(memory,'Player_Y_Speed')
                    passenger=N.get(memory,'PlatformCollisionFlag',slot)
                    footer=memory[0x65b];plane=N.get(memory,'Enemy_Y_Position',slot)
                    value=dict(tick=tick,source=phase,vy=vy,passenger=passenger,
                        footer=footer,plane=plane,fraction=memory.ram[2][0x7f],
                        acceleration=int.from_bytes(memory.ram[2][0x82:0x84],'little'),
                        impulse=int.from_bytes(memory.ram[2][0x86:0x88],'little'),maps=list(memory.rawtags))
                    if phase==3:
                        counts['rising_source_LPC']+=1
                        if first is None:first=value
                        # Proposed descending-only conjunction, never justVY.
                        would_admit=vy<128 and not N.get(memory,'Player_State')&1 and passenger==slot and plane-footer==2
                        assert not would_admit,('Rising boundary would be captured',direction,value)
                        if vy<128:counts['rising_integer_nonnegative']+=1
                    if len(callback)<2:callback.append(value)
            B.Frames.frame(q,watch)
        rows.append(dict(direction=direction,first_rising_LPC=first,counts=dict(counts),first2=callback,end=B.state(q)))
    report=dict(passed=all(row['first_rising_LPC']is not None for row in rows),
        composition=composition,prefix_updates=updates,start=before,branches=rows,
        normal_input_forks_only=True,proposed_code_executed=False,source_scope_only=True,
        scope='One genuine downward944 carry and three fresh held-A direction branches; not a universal legal lifecycle proof, native or full-stage claim',
        output_files=0)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_FOOTER_JUMP '+encoded,flush=True)
    print('DKJR_FOOTER_JUMP_SHA256 '+H(encoded.encode()),flush=True)
    assert report['passed']


if __name__=='__main__':main()
