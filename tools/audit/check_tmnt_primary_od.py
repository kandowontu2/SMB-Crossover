"""Compare baked primary weapon stores with the actual original renderer."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from check_tmnt_render_oa import load,Memory,address,location
from check_tmnt_audio_fallback_oc import qualified
from verify_native_relocation import NesMPU


def execute(b,pc,ptr,pose,face,state,offset,rotation,flags,shadow=216,actual=88):
    m=Memory(b);m.page(1,89);m.page(2,actual)
    for i in range(256):m[0x200+i]=(i*73+29)&255
    # Deliberately changed RAM descriptor for wrong-pointer fallback tests.
    m[0x5ca0:0x5cb1]=[16,10,0,0,0,20,0,0,8,30,0,0,16,40,0,0,24]
    x,y,page=state
    for n,v in {'R0':ptr&255,'R1':ptr>>8,'R2':0x96,'R3':0x83,'R4':x,'R5':page,'R6':y,'R7':0x84,
                'CurrentBank':217,'CurrentBankC':shadow,'CurrentOAMOffset':offset,'PlayerFacingDir':face,
                'GuestOamRotationActive':rotation[0],'RgOamRotation':rotation[1]}.items():m[address(b,n)]=v
    m[0x1fe]=255;m[0x1ff]=0x7e;m.writes=[]
    c=NesMPU(memory=m,pc=pc);c.a=0x55;c.x=pose;c.y=7;c.p=flags;c.sp=0xfd;fallback=0
    for _ in range(20000):
        if c.pc==0x7f00:break
        if c.pc==address(b,'MetaspriteRenderLoop'):fallback+=1
        c.step()
    else:raise AssertionError(('Primary CPU timeout',ptr,pose,face,state,offset,hex(c.pc),m.banks))
    excluded=set(range(0x100,0x200))|set(range(0x5114,0x5118))
    for s in b['segs'].values():
        if s.get('name')=='"SMCCODE"':excluded.update(range(int(s['start'],0),int(s['start'],0)+int(s['size'],0)))
    for n in ['safecall_a','SafecallA']:
        if n in b['syms']:excluded.add(address(b,n))
    ram=bytes(0 if i in excluded else m[i]for i in range(0x8000))
    oam=[(at,v)for at,v in m.writes if 0x200<=at<=0x302]
    return(c.a,c.x,c.y,c.p&0xcf,c.sp),ram,oam,list(m.banks),c.processorCycles,fallback


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.baseline),load(a.rom)
    oldpc=qualified(a.baseline)[('TnDraw','Draw')];newpc=address(new,'TnPrimaryRender');records=[];parts={};bounds=[]
    for face,suffix in [(1,'R'),(2,'L')]:
        lo,hi=location(old,'TnWeapon'+suffix+'Lo'),location(old,'TnWeapon'+suffix+'Hi');assert hi-lo==31
        for pose in range(31):
            ptr=old['raw'][lo+pose]|old['raw'][hi+pose]<<8;off=16+88*8192+ptr-0xc000;n=old['raw'][off]
            assert n%4==0 and n<=16
            assert old['raw'][off:off+1+n]==new['raw'][off:off+1+n]
            data=[list(old['raw'][off+j:off+j+4])for j in range(1,n+1,4)]
            for t,at,y,x in data:
                dx=x-256 if x&128 else x;dy=y-256 if y&128 else y;assert -20<=dx<=12 and -24<=dy<=8;bounds.append((dx,dy))
            records.append((pose,face,ptr));parts[ptr]=data
    rows=[];fast=slow=0
    def check(pose,face,ptr,state,offset,rotation,flags,tag,shadow=216,actual=88):
        nonlocal fast,slow
        x=execute(old,oldpc,ptr,pose,face,state,offset,rotation,flags,shadow,actual)
        y=execute(new,newpc,ptr,pose,face,state,offset,rotation,flags,shadow,actual)
        assert x[:4]==y[:4],(tag,pose,face,hex(ptr),state,offset,rotation,hex(flags),x[0],y[0],
            [(hex(j),x[1][j],y[1][j])for j in range(0x8000)if x[1][j]!=y[1][j]][:12],x[3],y[3])
        fast+=y[5]==0;slow+=y[5]>0
        rows.append(dict(tag=tag,pose=pose,face=face,pointer=ptr,state=state,offset=offset,rotation=rotation,flags=flags,
                         shadow=shadow,actual=actual,old_cycles=x[4],new_cycles=y[4],fallback=bool(y[5])))
    for (pose,face,ptr),offset,rotation,flags in itertools.product(records,[0,1,112,128,236,239,240,255],
            [(0,0),(1,4),(1,128),(1,255)],[0x30,0x71,0x39,0xee]):
        check(pose,face,ptr,(128,176,0),offset,rotation,flags,'interior')
    states=[(20,24,0),(243,247,0),(19,24,0),(244,24,0),(20,23,0),(20,248,0),(0,0,0),(255,255,0),(128,176,1),(128,176,255)]
    for (pose,face,ptr),state,offset,rotation,flags in itertools.product(records,states,[0,240],[(0,0),(1,255)],[0x30,0xee]):
        check(pose,face,ptr,state,offset,rotation,flags,'clipping-boundary')
    for (pose,face,ptr),flags in itertools.product(records,[0x30,0xee]):
        check(pose,face,0x5ca0,(128,176,0),0,(1,128),flags,'wrong-descriptor')
        check(pose,face,ptr,(128,176,0),0,(1,128),flags,'wrong-bank-shadow',shadow=255)
        check(pose,face,ptr,(128,176,0),0,(1,128),flags,'other-physical-bank',shadow=224,actual=96)
    for pose,face,flags in itertools.product([31,32,127,255],[1,2],[0x30,0xee]):
        check(pose,face,records[9][2],(128,176,0),0,(1,128),flags,'out-of-range-pose')
    for face,flags in itertools.product([0,3,255],[0x30,0xee]):
        check(9,face,records[9][2],(128,176,0),0,(1,128),flags,'other-facing-right')
    savings=[q['old_cycles']-q['new_cycles']for q in rows if q['tag']=='interior'and not q['fallback']]
    q=dict(passed=True,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),
           cases=len(rows),native_cases=fast,fallback_cases=slow,table_entries=len(records),unique_records=len(parts),
           signed_bounds=[[min(q[i]for q in bounds),max(q[i]for q in bounds)]for i in range(2)],
           interior_cycles_saved=[min(savings),max(savings)],
           scope='Actual linked old private Draw and new primary renderer for all62 facing/pose entries. Original immutable descriptor bytes, legal/edge/offscreen origins, capacity, unaligned/rotated OAM, wrong pointers/banks, invalid poses and flags. Exact A/X/Y/meaningfulP/SP, application RAM except discarded stack/SMC/safecall scratch/mapper latches, ordered OAM plus overflow bytes and final banks. Native synthetic-return interruption, timing and campaign proof remain separate.')
    (a.output/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n');(a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
