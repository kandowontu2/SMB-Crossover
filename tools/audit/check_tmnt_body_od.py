"""Compare the entire old/new body admission, including native enemy fallback."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from check_tmnt_render_oa import load, Memory, address, location
from verify_native_relocation import NesMPU


def execute(b, pose, face, ptr, state, offset, rotation, flags, character=19,
            engine=8, shadow=216, cached=None):
    m=Memory(b);m.page(1,4);m.page(2,88)
    for i in range(259):m[0x200+i]=(i*73+29)&255
    m[0x5ca0:0x5cb1]=[16,10,0,0,0,20,0,0,8,30,0,0,16,40,0,0,24]
    x,y,xpage,ypage=state
    seed={'R0':ptr&255,'R1':ptr>>8,'R2':0x96,'R3':0xa7,'R4':x,'R5':xpage,'R6':y,'R7':ypage,
          'CurrentBank':132,'CurrentBankC':shadow,'CurrentOAMOffset':offset,'SelectedCharacter':character,
          'GameEngineSubroutine':engine,'TnPose':pose,'PlayerFacingDir':face,
          'SmPosePtr':(ptr if cached is None else cached)&255,
          'GuestOamRotationActive':rotation[0],'RgOamRotation':rotation[1], 'RlOutlineBypass':0}
    for n,v in seed.items():m[address(b,n)]=v
    m[address(b,'SmPosePtr')+1]=(ptr if cached is None else cached)>>8
    m[0x1fe]=255;m[0x1ff]=0x7e;m.writes=[]
    c=NesMPU(memory=m,pc=address(b,'RlNativeRenderDispatch'));c.a=0x55;c.x=13;c.y=0;c.p=flags;c.sp=0xfd
    fast=goomba=0
    for _ in range(20000):
        if c.pc==0x7f00:break
        if 'TnBodyRender' in b['syms'] and c.pc==address(b,'TnBodyRender'):fast+=1
        if c.pc==address(b,'NativeGoombaFastBody'):goomba+=1
        c.step()
    else:raise AssertionError(('timeout',pose,face,ptr,state,offset,rotation,flags,hex(c.pc)))
    data=bytearray(m[:0x8000]);data[0x100:0x200]=bytes(256)
    return((c.a,c.x,c.y,c.p&0xcf,c.sp),bytes(data),
           [(at,v)for at,v in m.writes if 0x200<=at<=0x302],m.banks,c.processorCycles,fast,goomba)


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.baseline),load(a.rom)
    records=[];unique={};bounds=[];attrs=set()
    for face,suffix in [(1,'R'),(2,'L')]:
        lo,hi=location(old,'TnBody'+suffix+'Lo'),location(old,'TnBody'+suffix+'Hi');assert hi-lo==99
        for pose in range(99):
            ptr=old['raw'][lo+pose]|old['raw'][hi+pose]<<8;at=16+88*8192+ptr-0xc000;n=old['raw'][at]
            assert n%4==0 and n<=28
            assert old['raw'][at:at+1+n]==new['raw'][at:at+1+n]
            for j in range(1,n+1,4):
                t,attr,y,x=old['raw'][at+j:at+j+4];dx=x-256 if x&128 else x;dy=y-256 if y&128 else y
                assert -11<=dx<=19 and -16<=dy<=24 and attr&32==0
                attrs.add(attr);bounds.append((dx,dy))
            record=(pose,face,ptr);records.append(record);unique[ptr]=record
    rows=[]
    def check(record,state=(128,176,0,1),offset=0,rotation=(0,0),flags=0x30,tag='interior',**kw):
        x=execute(old,*record,state,offset,rotation,flags,**kw);y=execute(new,*record,state,offset,rotation,flags,**kw)
        assert x[:4]==y[:4],(tag,record,state,offset,rotation,flags,kw,x[0],y[0],
            [(hex(i),x[1][i],y[1][i])for i in range(0x8000)if x[1][i]!=y[1][i]][:12])
        assert x[6]==y[6],('native Goomba fallback lost',tag,record,x[6],y[6])
        rows.append(dict(tag=tag,record=record,state=state,offset=offset,rotation=rotation,flags=flags,
                         old_cycles=x[4],new_cycles=y[4],admitted=bool(y[5]),**kw))
    for record,off,rot,flags in itertools.product(records,[0,1,128,239,240,255],[(0,0),(1,4),(1,255)],[0x30,0xee]):
        check(record,offset=off,rotation=rot,flags=flags)
    states=[(11,16,0,1),(236,231,0,1),(10,16,0,1),(237,16,0,1),(11,15,0,1),(11,232,0,1),
            (0,0,0,1),(255,255,0,1),(128,176,1,1),(128,176,255,1),(128,176,0,0),(128,176,0,2)]
    for record,state,off,flags in itertools.product(unique.values(),states,[0,240],[0x30,0xee]):
        check(record,state=state,offset=off,rotation=(1,128),flags=flags,tag='boundary')
    for char,flags in itertools.product(range(256),[0x30,0xee]):check(records[9],character=char,flags=flags,tag='identity')
    for record,flags in itertools.product(records,[0x30,0xee]):
        check(record,engine=0,flags=flags,tag='menu')
        check(record,shadow=255,flags=flags,tag='wrong-bank-shadow')
        check(record,cached=0x5ca0,flags=flags,tag='wrong-cached-body')
    for pose,face,flags in itertools.product([99,127,255],[1,2],[0x30,0xee]):
        check((pose,face,records[9][2]),flags=flags,tag='invalid-pose')
    for flags in [0x30,0xee]:
        check((9,1,0x5ca0),flags=flags,tag='RAM-record')
        for name in ['MetaspriteData_GOOMBA_WALKING_1_LEFT','MetaspriteData_GOOMBA_WALKING_1_RIGHT',
                     'MetaspriteData_GOOMBA_WALKING_2_LEFT','MetaspriteData_GOOMBA_WALKING_2_RIGHT']:
            check((9,1,address(old,name)),cached=records[9][2],flags=flags,tag='native-Goomba')
    savings=[r['old_cycles']-r['new_cycles']for r in rows if r['tag']=='interior']
    q=dict(passed=True,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),
           cases=len(rows),table_entries=len(records),unique_records=len(unique),attributes=sorted(attrs),interior_cycles_saved=[min(savings),max(savings)],
           scope='Entire linked RlNativeRenderDispatch old/new admission, all198 body entries, signed coordinate/page edges, capacity/unaligned rotated OAM/overflow, raw identity IDs, menu/wrong-bank/pointer/pose fallbacks and exact native-Goomba admissions. Exact A/X/Y/meaningfulP/SP, all application RAM except discarded stack, ordered OAM and final banks. No native interruption, timing or route claim.')
    (a.output/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n');(a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
