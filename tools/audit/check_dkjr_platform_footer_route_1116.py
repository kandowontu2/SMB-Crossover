"""Unchanged ed3e control on the owning footer compound image, stdout only."""
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

C,N,B=F.C,R.N,R.B
H=lambda value:sha256(value).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--public',type=Path,required=True)
    ap.add_argument('--limit',type=int,default=15000)
    ap.add_argument('--input-kind',required=True,choices=('exact-6a3','bt91dc-reference-only'));args=ap.parse_args()
    public,binding=Input.normalize(args.public.read_bytes(),kind=args.input_kind)
    parent,_=C.Camera.proposal(public);raw,composition=C.proposal(parent)
    assert C.inverse(raw)==parent
    native=F.controller(raw);source=F.source_controller(raw)
    print('DKJR_FOOTER_ROUTE_PHASE frozen-Lua '+H(native.encode()),flush=True)
    opening,m=R.cold(raw)
    counts=Counter();by_world=Counter();fourth={};tick=0;first_bad=None
    body=C.Camera.payload(raw)
    linked=C.Plan.Funding.H.T.assemble(C.Plan.SOURCE,C.Plan.LAYOUT)
    native_branch=linked['symbols']['Native']
    bad_writers={0xa000+i for i in range(0x1fde)if body[i:i+3]==bytes.fromhex('8d6bc0')}
    def view(c):
        r=m.ram[2]
        return dict(tick=tick,PC=c.pc,SP=c.sp,A=c.a,P=c.p,**B.state(m),
            origin=r[0x76],limit=r[0x7b],prior=r[0x6c],
            saved_camera=r[0x435]+256*r[0x436],camera_delta=r[0x438])
    def observe(memory,c):
        nonlocal first_bad
        tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        if(tag,c.pc)==(199,0xac29) and c.x<6:
            slot=c.x;world=N.get(m,'Enemy_X_Position',slot)+256*N.get(m,'Enemy_PageLoc',slot)
            by_world[str(world)]+=1
            if world==944:
                record=view(c);record.update(actor_top=N.get(m,'Enemy_Y_Position',slot),slot=slot)
                fourth.setdefault('first',record);fourth['last']=record
        if tag==3 and c.pc in bad_writers and c.a==5 and first_bad is None:first_bad=view(c)
        if(tag,c.pc)==(128,native_branch):counts['footer_native_collision_branch']+=1
    output=__import__('sys').stdout
    def after(memory):
        nonlocal tick
        tick+=1
        if tick%1000==0:
            print('DKJR_FOOTER_ROUTE_PROGRESS '+json.dumps(dict(tick=tick,**B.state(m)),separators=(',',':')),file=output,flush=True)
    with redirect_stdout(io.StringIO()):
        result=B.route(m,raw,args.limit,controller_text=source,observe_extra=observe,after_frame=after)
    receipt=result.get('receipt')or{}
    report=dict(passed=bool(result['passed']),composition=composition,input_binding=binding,opening=opening,
        controller_Lua_SHA256=H(native.encode()),source_Lua_SHA256=H(source.encode()),
        helper_actual_positions=dict(by_world),fourth=fourth,first_source5_writer=first_bad,
        reason=receipt.get('reason'),last_events=receipt.get('events',[])[-8:],
        logical_source_updates=tick,terminal=B.state(m),counts=dict(counts),
        controls_changed=False,game_state_seeds=False,output_files=0,native_claim=False,
        endpoint_scope='25 living grounded completed private D65E motor returns, not full host Main')
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_FOOTER_ROUTE '+encoded,flush=True);print('DKJR_FOOTER_ROUTE_SHA256 '+H(encoded.encode()),flush=True)
    assert report['passed'],report['reason']


if __name__=='__main__':main()
