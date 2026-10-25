"""Execute both real numeric printers at queue boundaries and deferred flush."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import load,Memory,address,location
from check_reported_contacts_pp import run,qualified

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    bundles=[]
    for path in [a.baseline,a.rom]:
        b=load(path);b['debug']=path.with_suffix('.dbg').read_text();bundles.append(b)
    old,new=bundles;cases=0;rejected=0;differential=0
    labels={(id(b),entry):qualified(b,entry,'OutputNumbers')for b in bundles for entry in ['NativeRarePrintStatusBarNumbersCore','HudPrintStatusNumbersLocal']}
    def arena(b,entry,offset=0,char=0,variant=0,mode=1):
        m=Memory(b);m.page(1,(location(b,entry)-16)//8192);m[address(b,'CurrentBank')]=m.banks[1]|128
        for n,v in dict(OperMode=mode,OperMode_Task=3,GameEngineSubroutine=8,SelectedCharacter=char,Z2Variant=variant,VRAM_Buffer1_Offset=offset).items():m[address(b,n)]=v
        for i in range(128):m[address(b,'VRAM_Buffer1')+i]=0x57
        for i in range(24):m[address(b,'DisplayDigits')+i]=i%10
        if 'NativeStatusPending' in b['syms']:m[address(b,'NativeStatusPending')]=0
        m.writes=[];return m
    def queue(m,b):return bytes(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+128])
    for entry,slot,offset,identity in itertools.product(['NativeRarePrintStatusBarNumbersCore','HudPrintStatusNumbersLocal'],range(6),range(256),[(0,0),(4,0),(4,1)]):
        m=arena(new,entry,offset,*identity);before=queue(m,new)
        c=run(new,m,entry,a=(slot-1)&15,pc=labels[id(new),entry])
        suppressed=identity==(4,1)and 1<=slot<=4
        length=[6,6,6,2,2,3][slot];fits=offset+length<81
        expect=not suppressed and fits
        assert c.sp==0xed,('stack',entry,slot,offset,c.sp)
        assert queue(m,new)[84:]==before[84:],('Buffer2 changed',entry,slot,offset,identity)
        assert m[address(new,'VRAM_Buffer1_Offset')]==(offset+length+3 if expect else offset)
        mask=m[address(new,'NativeStatusPending')]
        assert mask==(0 if expect or suppressed else 1<<slot),(entry,slot,offset,identity,mask)
        if not expect:
            assert queue(m,new)==before;rejected+=1
        elif identity!=(4,1):
            prior=arena(old,entry,offset,*identity)
            d=run(old,prior,entry,a=(slot-1)&15,pc=labels[id(old),entry])
            assert queue(m,new)==queue(prior,old),(entry,slot,offset)
            assert (c.a,c.x,c.y,c.p&0xcf)==(d.a,d.x,d.y,d.p&0xcf)
            for n in ['R0','R1','R2','R3']:assert m[address(new,n)]==prior[address(old,n)],n
            differential+=1
        cases+=1
    flushes=[]
    for identity in [(0,0),(4,0),(4,1)]:
        m=arena(new,'X5NativeStatusFlush',80,*identity);m[address(new,'NativeStatusPending')]=63
        m[address(new,'R0')]=0x73;before=queue(m,new)
        run(new,m,'X5NativeStatusFlush')
        expected=63^(30 if identity==(4,1) else 0)
        assert m[address(new,'NativeStatusPending')]==expected
        assert queue(m,new)==before and m[address(new,'R0')]==0x73
        m[address(new,'VRAM_Buffer1_Offset')]=0
        m[address(new,'VRAM_Buffer1')]=0
        # Updated digits must be read on retry, rather than stale packet data.
        for i in range(24):m[address(new,'DisplayDigits')+i]=(i+3)%10
        run(new,m,'X5NativeStatusFlush')
        assert m[address(new,'NativeStatusPending')]==0
        assert queue(m,new)[84:]==before[84:]
        offset=m[address(new,'VRAM_Buffer1_Offset')];at=0;packets=[]
        while at<offset:
            start=address(new,'VRAM_Buffer1')+at;length=m[start+2]
            assert length in [2,3,6]
            packets.append(list(m[start:start+length+3]));at+=length+3
        assert at==offset and m[address(new,'VRAM_Buffer1')+offset]==0
        assert len(packets)==(2 if identity==(4,1)else 6)
        assert m[address(new,'R0')]==0x73
        flushes.append(dict(identity=identity,packets=packets,offset=offset))
    # Suppressing a score must not turn an unrelated world/coin byte to space.
    m=arena(new,'HudUpdateNumberLocal',0,4,1);m[address(new,'VRAM_Buffer1')]=0
    run(new,m,'HudUpdateNumberLocal',a=2)
    assert m[address(new,'VRAM_Buffer1_Offset')]==0
    assert m[address(new,'VRAM_Buffer1')]==0
    proof=dict(passed=True,ROM_sha256=sha(a.rom),baseline_ROM_sha256=sha(a.baseline),numeric_cases=cases,rejected_or_suppressed=rejected,unchanged_valid_cases=differential,flushes=flushes,
        scope='Actual linked CPU code; buffer bounds, stack, native digits and bounded eventual retry. Native frame/IRQ proofs separate.')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
if __name__=='__main__':main()
