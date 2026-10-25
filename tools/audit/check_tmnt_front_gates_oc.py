"""Compare real foreground gates, retaining every application byte and OAM write."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from check_tmnt_render_oa import load,Memory,address,location
from verify_native_relocation import NesMPU


def run(b,entry,original,seed,flags):
    m=Memory(b);bank=(location(b,original)-16)//8192;m.page(1,bank)
    m[address(b,'CurrentBank')]=bank|128
    for n,v in seed.items():
        if isinstance(n,tuple):n,i=n;m[address(b,n)+i]=v
        else:m[address(b,n)]=v
    m[0x1fe]=255;m[0x1ff]=0x7e;m.writes=[]
    c=NesMPU(memory=m,pc=address(b,entry));c.sp=0xfd;c.a=0x56;c.x=3;c.y=7;c.p=flags
    for _ in range(100000):
        if c.pc==0x7f00:break
        c.step()
    else:raise AssertionError(('Foreground gate timeout',entry,seed,hex(c.pc),m.banks))
    excluded=set(range(0x100,0x200))|set(range(0x5114,0x5118))
    for seg in b['segs'].values():
        if seg.get('name')=='"SMCCODE"':excluded.update(range(int(seg['start'],0),int(seg['start'],0)+int(seg['size'],0)))
    for n in ['safecall_a','SafecallA']:
        if n in b['syms']:excluded.add(address(b,n))
    memory=bytes(0 if i in excluded else m[i]for i in range(0x8000))
    oam=[(at,v)for at,v in m.writes if 0x200<=at<0x300]
    hardware=[(at,v)for at,v in m.writes if 0x4000<=at<0x4018 or 0x5000<=at<0x5114 or 0x5118<=at<0x5207]
    return(c.a,c.x,c.y,c.p&0xcf,c.sp),memory,oam,hardware,m.banks,c.processorCycles


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.baseline),load(a.rom)
    stats={};cases=0
    for original,gate in [('RlGraphicsDispatch','TnFastGraphicsGate'),('RlSpecialDrawDispatch','TnFastSpecialGate'),('KbDrawDispatch','TnFastDrawGate')]:
        rows=[]
        for char,variant,offset,flags in itertools.product(range(21),[0,1,2,3],[0,128,240],[0x30,0x71,0x39,0xee]):
            seed={'SelectedCharacter':char,'OperMode':1,'GameEngineSubroutine':8,'Player_Y_HighPos':1,
                  'Player_X_Position':64,'Player_Y_Position':176,'PlayerFacingDir':1,'CurrentOAMOffset':offset,
                  'TnVariant':variant,'TnSeq':128,'TnPose':9,'TnHudValid':0,('TnHealth',variant):128}
            before=run(old,original,original,seed,flags);after=run(new,gate,original,seed,flags)
            assert before[:5]==after[:5],(gate,char,variant,offset,hex(flags),before[0],after[0],
                [(hex(i),before[1][i],after[1][i])for i in range(0x8000)if before[1][i]!=after[1][i]][:15],before[4],after[4])
            rows.append(dict(character=char,variant=variant,offset=offset,flags=flags,old_cycles=before[5],new_cycles=after[5]));cases+=1
        native=[q['old_cycles']-q['new_cycles']for q in rows if q['character']==19]
        stats[gate]=dict(cases=len(rows),native_cycles_saved=[min(native),max(native)])
        (a.output/f'{gate}-cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
    q=dict(passed=True,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),
           cases=cases,stats=stats,scope='Actual linked gates with seeded inputs, all21internal character IDs, four turtle variants, three OAM offsets and four flag states. Exact final A/X/Y/meaningfulP/SP, all application RAM outside discarded CPU stack/SMC operands/safecall scratch, ordered OAM and non-banking hardware writes, final physical banks. Native IRQ and whole-campaign timing are separate.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
