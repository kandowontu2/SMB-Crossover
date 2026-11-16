"""One genuine corrected-route prefix, seven first-loss boundaries; no controls changed."""
import argparse
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path

import check_dkjr_carry_camera_route_1116 as Route

C,F,B,N=Route.C,Route.F,Route.B,Route.N
H=lambda value:sha256(value).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parent',type=Path,required=True)
    args=ap.parse_args()
    parent=args.parent.read_bytes();candidate,composition=C.proposal(parent)
    assert C.inverse(candidate)==parent
    text=F.source_controller(candidate)
    opening,m=Route.cold(candidate)
    native={}
    for name in ('LargePlatformCollision','PlayerCollisionCore'):
        pc=N.address(m.bundle,name);at=N.location(m.bundle,name);tag=((at-16)//8192)|128
        native[name]=(tag,pc)
        assert candidate[at:at+8]==parent[at:at+8]
    bindings={name:dict(tag=tag,PC=pc,file=N.location(m.bundle,name),
        preimage=candidate[N.location(m.bundle,name):N.location(m.bundle,name)+8].hex())
        for name,(tag,pc) in native.items()}
    body=C.payload(candidate)
    writers={0xa000+i for i in range(0x1fde) if body[i:i+3]==bytes.fromhex('8d6bc0')}
    origins={0xa000+i for i in range(0x1fde) if body[i:i+3]==bytes.fromhex('8d76c0')}
    counts=Counter();rows={};pending={};tick=0;slot=None;support_key=None
    last_carry=None
    def rects(offset):
        out=[]
        for at in range(offset,offset+16,4):
            if m.ram[2][at]==255:break
            out.append(list(m.ram[2][at:at+4]))
        return out
    def view(c):
        r=m.ram[2];q=dict(PC=c.pc,SP=c.sp,A=c.a,X=c.x,Y=c.y,P=c.p,tick=tick,**B.state(m),
            prior=r[0x6c],origin=r[0x76],limit=r[0x7b],fractionX=r[0x56],
            camera_saved=r[0x435]+256*r[0x436],camera_delta=r[0x438],
            bbox=list(m[0x658:0x65c]),query=list(r[0x3e:0x42]),window=list(r[0x8e8:0x8ec]),
            contact=list(r[0x42:0x46]),support=rects(0x800),ObjectOffset=N.get(m,'ObjectOffset'))
        if slot is not None:
            at=0x65c+4*slot
            q['helper']=dict(slot=slot,raw_top=N.get(m,'Enemy_Y_Position',slot),
                vy=N.get(m,'Enemy_Y_Speed',slot),passenger=N.get(m,'PlatformCollisionFlag',slot),
                bbox=list(m[at:at+4]))
        return q
    def token(c):
        return ((m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1)&65535,(c.sp+2)&255)
    def observe(_m,c):
        nonlocal slot,last_carry,support_key
        tag=m.rawtags[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1
        for name in tuple(pending):
            if pending[name]==(c.pc,c.sp):
                del pending[name]
                if name=='motor':
                    counts['motor_returns']+=1
                    if 'first_carry'in rows:counts['post_carry_motor_returns']+=1
                elif name.endswith('_plane'):
                    target=rows[name[:-6]]['plane']
                    target['return']=dict(PC=c.pc,SP=c.sp,A=c.a,P=c.p,WCount=m.ram[2][0x8dd])
                    target['return']['appended']=m.ram[2][0x8dd]>target['entry']['WCount']
                else:rows[name]['return']=view(c)
        if (tag,c.pc)==(2,0xd65e):
            counts['motor_entries']+=1;pending['motor']=token(c)
        if (tag,c.pc)==(199,0xac29):
            s=c.x
            if s<6 and N.get(m,'Enemy_ID',s)==37 and N.get(m,'Enemy_X_Position',s)+256*N.get(m,'Enemy_PageLoc',s)==944:
                slot=s;counts['944_positions']+=1;last_carry=view(c)
                rows.setdefault('first_carry',last_carry)
        if 'first_carry'not in rows:return
        if (tag,c.pc)==native['LargePlatformCollision'] and c.x==slot:
            counts['944_LPC_entries']+=1
            if 'native_LPC'not in rows:
                rows['native_LPC']=dict(entry=view(c));pending['native_LPC']=token(c)
        if (tag,c.pc)==native['PlayerCollisionCore'] and N.get(m,'ObjectOffset')==slot:
            counts['944_collision_core_entries']+=1
            if 'native_collision_core'not in rows:
                rows['native_collision_core']=dict(entry=view(c));pending['native_collision_core']=token(c)
        if tag!=3:return
        if c.pc==0xb065:
            counts['source_support_queries']+=1
            support_key='initial_support' if 'initial_support'not in rows else 'next_support' if 'next_support'not in rows else None
            if support_key:
                rows[support_key]=dict(entry=view(c));pending[support_key]=token(c)
        if c.pc==0xb5c8 and m.ram[2][0x8f0]==slot and m.ram[2][0x8db]>=3:
            counts['944_plane_candidates']+=1
            if support_key and 'plane'not in rows[support_key]:
                q=view(c);q.update(plane=c.a,candidate=list(m.ram[2][0x8e4:0x8e8]),WCount=m.ram[2][0x8dd])
                wl,wr,wt,wb=m.ram[2][0x8e8:0x8ec]
                q['horizontal']=q['candidate'][2]>=wl and wr>=q['candidate'][0]
                q['vertical']=wt<=c.a<=wb
                rows[support_key]['plane']=dict(entry=q);pending[support_key+'_plane']=token(c)
        if c.pc in writers and c.a==4 and m.ram[2][0x6b]!=4:
            rows.setdefault('source4_writer',view(c))
        if c.pc in origins and 'source4_writer'in rows:
            rows.setdefault('fresh_origin_writer',view(c))
        assert len(rows)<=7
    class Complete(Exception):pass
    output=__import__('sys').stdout
    def after(_m):
        nonlocal tick
        tick+=1
        if tick%1000==0:
            print('DKJR_CAMERA_VERTICAL_PROGRESS '+json.dumps(dict(tick=tick,**B.state(m)),separators=(',',':')),file=output,flush=True)
        if counts['post_carry_motor_returns']>=4 and 'fresh_origin_writer'in rows:raise Complete()
    with redirect_stdout(io.StringIO()):
        try:result=B.route(m,candidate,4500,controller_text=text,observe_extra=observe,after_frame=after)
        except Complete:result=None
    report=dict(diagnostic_complete='fresh_origin_writer'in rows,candidate_SHA256=C.CANDIDATE,
        composition=composition,opening=opening,native_binding_preimages=bindings,
        source_control_Lua_SHA256=H(text.encode()),counts=dict(counts),witnesses=rows,
        last_actual_944_position=last_carry,terminal=B.state(m),logical_source_updates=tick,
        route_pass_claim=False,native_claim=False,game_state_seeds=False,controls_changed=False,output_files=0)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_CAMERA_VERTICAL '+encoded,flush=True)
    print('DKJR_CAMERA_VERTICAL_SHA256 '+H(encoded.encode()),flush=True)
    assert report['diagnostic_complete']


if __name__=='__main__':main()
