"""Compare real outer UI/lifecycle calls, including all alternate dispatches."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from check_tmnt_render_oa import load,Memory,address,location
from verify_native_relocation import NesMPU


def run(b,char,variant,mode,scenario,flags,case):
    m=Memory(b);physical=(location(b,'X5BounceUiDispatch')-16)//8192;m.page(1,physical);m.page(2,88)
    seed={'CurrentBank':physical|128,'CurrentBankC':216,'SelectedCharacter':char,'RlVariant':variant,
          'Cv3Variant':variant,'Z2Variant':variant,'VvVariant':variant&3,'CrossoverBehaviorVersion':mode,
          'OperMode':0 if scenario==2 else 1,'OperMode_Task':3,'GameEngineSubroutine':11 if scenario==2 else 8,
          'NumberofLives':3,'Player_Y_HighPos':1,'Player_Y_Position':176,'Player_X_Position':64,
          'SavedJoypad1Bits':[0,0x21,255,0x31][scenario],'InvPrevious':1 if scenario==1 else 0,
          'GamePauseStatus':1 if scenario==1 else 0,'GuestHurtTicks':3 if scenario==2 else 0,
          'GuestHurtKind':char%12,'InvHudActive':0 if scenario==0 else 1,'InvDirty':1,
          'InvRefill':1 if scenario==3 else 0,'InvRefillTick':1,'InvRefillRemain':8,'InvDropAmount':13,
          'X5BounceOwner':[0,5,19,16][scenario],'X5BounceLife':3,'X5BounceKey':0,'X5BounceArea':0}
    for n,v in seed.items():m[address(b,n)]=v
    m[address(b,'InvAmmo')+1]=80
    m[0x1fe]=255;m[0x1ff]=0x7e;m.writes=[]
    c=NesMPU(memory=m,pc=address(b,'X5BounceUiDispatch'));c.sp=0xfd;c.a=(case*37)&255;c.x=(case*71)&255;c.y=(case*53)&255;c.p=flags
    for _ in range(50000):
        if c.pc==0x7f00:break
        c.step()
    else:raise AssertionError(('Outer UI timeout',char,variant,mode,scenario,hex(c.pc),m.banks))
    excluded=set(range(0x100,0x200))|set(range(0x5114,0x5118))
    for s in b['segs'].values():
        if s.get('name')=='"SMCCODE"':excluded.update(range(int(s['start'],0),int(s['start'],0)+int(s['size'],0)))
    for n in ['safecall_a','SafecallA']:
        if n in b['syms']:excluded.add(address(b,n))
    ram=bytes(0 if i in excluded else m[i]for i in range(0x8000))
    io=[(at,v)for at,v in m.writes if 0x4000<=at<0x4018 or 0x5000<=at<0x5114 or 0x5118<=at<0x5207]
    return(c.a,c.x,c.y,c.p&0xcf,c.sp),ram,io,list(m.banks),c.processorCycles


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.baseline),load(a.rom);rows=[];native=[];legacy=[]
    for i,(char,variant,mode,scenario,flags)in enumerate(itertools.product(range(20),[0,1,2,3],[0,1],range(4),[0x30,0x71,0x39,0xee])):
        x=run(old,char,variant,mode,scenario,flags,i);y=run(new,char,variant,mode,scenario,flags,i)
        assert x[:4]==y[:4],(char,variant,mode,scenario,hex(flags),x[0],y[0],
            [(hex(j),x[1][j],y[1][j])for j in range(0x8000)if x[1][j]!=y[1][j]][:15],x[3],y[3])
        fast=char in [13,14,16,17,19]
        (native if fast else legacy).append(x[4]-y[4])
        rows.append(dict(character=char,variant=variant,mode=mode,scenario=scenario,flags=flags,old_cycles=x[4],new_cycles=y[4],fast=fast))
    q=dict(passed=True,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),
           cases=len(rows),fast_cycles_saved=[min(native),max(native)],legacy_cycles_saved=[min(legacy),max(legacy)],
           scope='Actual complete X5BounceUiDispatch lifecycle/UI calls for all20internal IDs, four alternate values, Easy/Hard and idle/input/pause/injury/title/refill/stale-owner scenarios. Varying A/X/Y and four flag states. Exact final A/X/Y/meaningfulP/SP, application RAM except discarded stack/SMC/safecall scratch/mapper latches, ordered non-banking hardware writes and final banks. Does not certify natural reward collection, native timing or a campaign clear.')
    (a.output/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n');(a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
