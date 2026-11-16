"""Genuine f544 multi-carry then normal fresh jumps, fractional rising observed."""
import argparse
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path

import replay_dkjr_platform_footer_current_1116 as F
import check_dkjr_carry_camera_route_1116 as R
import dkjr_footer_source_input_1116 as Input

C,N,B,L=F.C,R.N,R.B,R.Cold.H.L
H=lambda value:sha256(value).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--public',type=Path,required=True)
    ap.add_argument('--input-kind',required=True,choices=('exact-6a3','bt91dc-reference-only'))
    args=ap.parse_args();public,binding=Input.normalize(args.public.read_bytes(),kind=args.input_kind)
    parent,_=C.Camera.proposal(public);raw,composition=C.proposal(parent);_,m=R.cold(raw)
    slot=None;updates=0;positions=0;output=__import__('sys').stdout
    class Captured(Exception):pass
    def observe(memory,c):
        nonlocal slot,positions
        tag=memory.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        if(tag,c.pc)==(199,0xac29)and c.x<6:
            if N.get(memory,'Enemy_ID',c.x)==37 and N.get(memory,'Enemy_X_Position',c.x)+256*N.get(memory,'Enemy_PageLoc',c.x)==944:
                slot=c.x;positions+=1
    def after(memory):
        nonlocal updates
        updates+=1
        if updates%1000==0:print('DKJR_FOOTER_NEW_JUMP_PROGRESS '+str(updates),file=output,flush=True)
        if positions>=3 and memory.ram[2][0x6b]==1:raise Captured()
    with redirect_stdout(io.StringIO()):
        try:B.route(m,raw,4000,controller_text=F.source_controller(raw),observe_extra=observe,after_frame=after)
        except Captured:pass
    assert positions>=3 and slot is not None and N.get(m,'PlatformCollisionFlag',slot)==slot
    start=dict(B.state(m),positions=positions,held=N.get(m,'SavedJoypad1Bits'),passenger=slot)
    assert not start['held']&128
    head_pc=N.address(m.bundle,'NativeRarePlayerHeadCollisionCore')
    head_tag=((N.location(m.bundle,'NativeRarePlayerHeadCollisionCore')-16)//8192)|128
    rows=[];zero_rising=0
    for direction in(0,1,2):
        q=L.clone(m);counts=Counter();first=None;after_first=None
        for tick in range(40):
            q.controller_pad=128|direction
            def watch(memory,c):
                nonlocal first,after_first,zero_rising
                tag=memory.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
                if(tag,c.pc)==(head_tag,head_pc):counts['actual_native_head_effect']+=1
                if(tag,c.pc)!=(128,0xb453)or c.x!=slot:return
                r=memory.ram[2];acc=int.from_bytes(r[0x82:0x84],'little');imp=int.from_bytes(r[0x86:0x88],'little')
                rising=r[0x6b]==3 and acc<imp
                if not rising:return
                counts['true_rising_LPC']+=1
                vy=N.get(memory,'Player_Y_Speed');passenger=N.get(memory,'PlatformCollisionFlag',slot)
                plain=(N.get(memory,'Player_Y_Position')+30)&255
                assert memory[0x65b]==plain,('actual candidate expanded true rising body',direction,tick,vy,passenger,acc,imp)
                value=dict(tick=tick,vy=vy,passenger=passenger,fraction=r[0x7f],acceleration=acc,impulse=imp,
                    footer=memory[0x65b],plane=N.get(memory,'Enemy_Y_Position',slot))
                if first is None:first=value
                elif after_first is None:after_first=value
                if vy<128:
                    counts['fractional_rising_nonnegative_nativeVY']+=1;zero_rising+=1
                    assert passenger!=slot,('stale passenger admitted fractional rise',direction,value)
            B.Frames.frame(q,watch)
            if q.ram[2][0x6b]==5:counts['ordinary_off_support_fatal_fall']+=1;break
        assert first is not None and first['vy']>=128 and first['passenger']==slot
        assert after_first is not None and after_first['passenger']==255
        rows.append(dict(direction=direction,counts=dict(counts),first=first,second=after_first,terminal=B.state(q)))
    report=dict(passed=True,composition=composition,input_binding=binding,start=start,
        genuine_prefix_updates=updates,normal_input_branches=rows,
        actual_candidate_never_expands_true_rising_footer=True,
        actual_multi_carry_then_fresh_jump_clears_passenger=True,
        fractional_rising_nonnegative_nativeVY_samples=zero_rising,
        dynamic_near_apex_zero_coverage=zero_rising>0,
        retained_coverage_negative='First invocation required a fractional-zero occurrence at this genuine three-carry seed; none occurred. No controls or game fixtures were changed to manufacture one.',
        scope='Actual first-jump clearing and observed rising samples only; near-apex exclusion additionally requires the old-LPC flag-writer induction, not a universal dynamic-zero claim.',
        ordinary_direction_hazards_not_fullroute_claim=True,game_state_seeds=False,output_files=0,native_claim=False)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_FOOTER_NEW_JUMP '+encoded,flush=True);print('DKJR_FOOTER_NEW_JUMP_SHA256 '+H(encoded.encode()),flush=True)


if __name__=='__main__':main()
