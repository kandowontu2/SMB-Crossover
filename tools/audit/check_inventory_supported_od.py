"""Compare the actual legacy-inventory support predicate on every raw ID."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from check_tmnt_render_oa import load,Memory,address,location
from verify_native_relocation import NesMPU


def run(b,char,variant,mode,flags,case):
    m=Memory(b);physical=(location(b,'InventorySupported')-16)//8192;m.page(1,physical);m.page(2,88)
    for n,v in {'CurrentBank':physical|128,'CurrentBankC':216,'SelectedCharacter':char,'RlVariant':variant,
                'Cv3Variant':variant,'Z2Variant':variant,'CrossoverBehaviorVersion':mode}.items():m[address(b,n)]=v
    m[0x1fe]=255;m[0x1ff]=0x7e;m.writes=[]
    c=NesMPU(memory=m,pc=address(b,'InventorySupported'));c.sp=0xfd;c.a=(case*37)&255;c.x=(case*71)&255;c.y=(case*53)&255;c.p=flags
    for _ in range(10000):
        if c.pc==0x7f00:break
        c.step()
    else:raise AssertionError(('Inventory support timeout',char,variant,mode,hex(flags),hex(c.pc),m.banks))
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
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.baseline),load(a.rom)
    rows=[];fast=[];legacy=[]
    cases=list(itertools.product(range(20),[0,1,3,255],[0,1],[0x30,0x31,0x71,0xf1,0x39,0x3d,0xee,0xff]))
    cases+=list(itertools.product(range(20,256),[0],[0],[0x30,0xee]))
    for i,(char,variant,mode,flags)in enumerate(cases):
        x=run(old,char,variant,mode,flags,i);y=run(new,char,variant,mode,flags,i)
        assert x[:4]==y[:4],(char,variant,mode,hex(flags),i,x[0],y[0],
            [(hex(j),x[1][j],y[1][j])for j in range(0x8000)if x[1][j]!=y[1][j]][:12],x[3],y[3])
        native=char in [13,14,16,17,18,19]
        if native:
            assert y[0][:3]==(char,char,(i*53)&255)and y[0][3]&1==0
            fast.append(x[4]-y[4])
        else:legacy.append(y[4]-x[4])
        rows.append(dict(character=char,variant=variant,mode=mode,flags=flags,old_cycles=x[4],new_cycles=y[4],fast=native))
    q=dict(passed=True,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),
           cases=len(rows),fast_cases=len(fast),legacy_cases=len(legacy),cycles_saved_native=[min(fast),max(fast)],
           added_cycles_legacy=[min(legacy),max(legacy)],raw_character_ids=256,
           scope='Actual linked InventorySupported, every raw ID, full modes/alternate/flag matrix for all20internal IDs and out-of-range probes. Varying input A/X/Y. Exact output A/X/Y/meaningfulP/SP, application RAM outside discarded stack/SMC/safecall scratch/mapper latches, ordered non-banking hardware writes and final banks. This predicate differential does not prove physical reward delivery or gameplay timing.')
    (a.output/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n');(a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
