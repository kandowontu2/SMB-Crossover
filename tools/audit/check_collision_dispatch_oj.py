"""Compare actual collision leaves and measure the intervening bank routing."""
from pathlib import Path
import argparse
import csv
import hashlib
import itertools
import json
from check_tmnt_render_oa import load,Memory,address,location
from verify_native_relocation import NesMPU


def run(bundle,entry,spec):
    char,a,roll,crouch,hurt,roll_hurt,state,flags,regs=spec
    m=Memory(bundle);entry_bank=(location(bundle,entry)-16)//8192
    if 0xa000<=address(bundle,entry)<0xc000:
        bank=entry_bank;m.page(1,bank)
    else:
        assert address(bundle,entry)>=0xe000 and entry_bank==127
        bank=87
    seed=dict(CurrentBank=bank|128,SelectedCharacter=char,RlVariant=roll,RgCrouch=crouch,
        GuestHurtTicks=hurt,RlHurt=roll_hurt,Player_State=state)
    for n,v in seed.items():m[address(bundle,n)]=v
    m[0x1fe]=0xef;m[0x1ff]=0xff;m.writes=[]
    c=NesMPU(memory=m,pc=address(bundle,entry));c.sp=0xfd;c.a=a;c.x,c.y=regs;c.p=flags
    minimum=c.sp
    for _ in range(5000):
        if c.pc==0xfff0:break
        c.step();minimum=min(minimum,c.sp)
    else:raise AssertionError(('CPU timeout',entry,spec,hex(c.pc),m.banks))
    allowed=set(range(0x100,0x200))|set(range(0x5114,0x5118))
    for n in ['CurrentBank','CurrentBankC','safecall_a']:allowed.add(address(bundle,n))
    app={at:m[at] for at,v in m.writes if at not in allowed}
    assert not app,(entry,spec,app)
    assert m.banks==[126,bank,88,127] and m[address(bundle,'CurrentBank')]==bank|128
    switches=sum(at==0x5115 for at,v in m.writes)
    return(c.a,c.x,c.y,c.p,c.sp),c.processorCycles,0xfd-minimum,switches


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.baseline),load(a.rom)
    specs=set()
    for char,roll,crouch,hurt,rh,state,flags,regs in itertools.product(range(20),[0,1],[0,1],[0,1],[0,1],[0,1,3],[0x30,0x71],[(3,7),(0xfe,0x81)]):
        specs.add((char,char,roll,crouch,hurt,rh,state,flags,regs))
    for char,acc,roll,flags in itertools.product([0,6,9,13,14,15,16,17,18,19,255],range(256),[0,1],[0x30,0x71]):
        specs.add((char,acc,roll,1,1,1,1,flags,(0xfe,0x81)))
    for char,roll in itertools.product(range(256),[0,255]):
        specs.add((char,char,roll,0,0,0,0,0x71,(3,7)))
    summaries={};cases=0
    with(a.output/'cases.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['entry','character','inputA','Roll','crouch','hurt','RollHurt','state','flags','X','Y','oldCycles','newCycles','oldStack','newStack','oldMapperWrites','newMapperWrites'])
        for entry in ['ExpandedCollisionAdder','ExpandedCollisionBox']:
            by_char={}
            for spec in sorted(specs):
                before,after=run(old,entry,spec),run(new,entry,spec)
                assert before[0]==after[0],(entry,spec,before,after)
                w.writerow([entry,*spec[:8],*spec[8],before[1],after[1],before[2],after[2],before[3],after[3]])
                if spec[0]<20 and spec[1]==spec[0]:
                    s=by_char.setdefault(str(spec[0]),dict(cases=0,cycles_saved_min=10000,cycles_saved_max=-10000,old_stack_max=0,new_stack_max=0))
                    saving=before[1]-after[1];s['cases']+=1
                    s['cycles_saved_min']=min(s['cycles_saved_min'],saving);s['cycles_saved_max']=max(s['cycles_saved_max'],saving)
                    s['old_stack_max']=max(s['old_stack_max'],before[2]);s['new_stack_max']=max(s['new_stack_max'],after[2])
                cases+=1
            summaries[entry]=by_char
    q=dict(passed=True,accepted=False,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),
        cases=cases,summaries=summaries,registers='Exact A/X/Y/fullP/SP',application_RAM_writes=0,final_bank_mappings_exact=True,
        scope='Actual assembled old/new adder and box queries, not stubbed targets. Legal IDs with raw A=ID cover Roll/hurt/crouch/state/flags/register combinations; mismatched rawA spans all256 values for11IDs, and all256selected IDs are sampled. Application RAM and final mappings remain exact. Cycles/stack are isolated instruction measurements, not native frame/PPU/NMI or complete-contact proof.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items() if k!='summaries'},indent=2))
    print(json.dumps(summaries,indent=2))


if __name__=='__main__':main()
