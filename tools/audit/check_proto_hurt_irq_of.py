"""Interrupt each actual instruction of the new injury-end banked path."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import check_proto_hurt_of as component
import check_tmnt_primary_irq_od as irq
from check_tmnt_render_oa import load, address


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.baseline),load(a.rom)
    component.NesMPU=irq.InterruptProbe;cases=0;paths=[]
    specs=[]
    for profile,state,low,reload,registers in itertools.product([(1,0),(1,1),(9,0)],[0,1],[11,64],[0,255],[(0x56,3,7),(0xa9,0xfe,0x81)]):
        specs.append(('MegaManHurtEnd',profile,state,low,reload,registers,None))
    for profile,low,reload,registers,mode in itertools.product([(1,0),(1,1),(9,0),(9,1),(13,0)],[64,129,130,224],[0,255],[(0x56,3,7),(0xa9,0xfe,0x81)],[0,0x81]):
        specs.append(('MegaManHurtDraw',profile,0,low,reload,registers,mode))
    for entry,profile,state,low,reload,registers,mode in specs:
        char,var=profile;args=(char,var,state,low,reload,0x30,registers)
        irq.INJECT=0;expected=component.run(old,entry,*args,mode=mode)
        if entry=='MegaManHurtEnd'and char in [1,9]:
            expected[1][address(old,'PlayerChrBank')]=low
            expected[1][address(old,'ReloadCHRBank')]=reload
        elif entry=='MegaManHurtDraw'and mode==0 and var==0 and((char==1 and low==129)or(char==9 and low==130)):
            expected[1][address(old,'PlayerChrBank')]=64 if char==1 else 224
            expected[1][address(old,'ReloadCHRBank')]=(reload+1)&255
        irq.INJECT=None;plain=component.run(new,entry,*args,mode=mode)
        # The plain path has no IRQ register stores. Compare those only on the
        # interrupted executions below, against the interrupted old helper.
        assert plain[0]==expected[0] and plain[3]==expected[3]
        count=len(irq.LAST.path)
        for instruction in range(count):
            irq.INJECT=instruction;actual=component.run(new,entry,*args,mode=mode)
            assert irq.LAST.interrupted and actual[:4]==expected[:4],(entry,profile,state,low,reload,registers,mode,instruction)
            cases+=1
        paths.append(dict(entry=entry,character=char,variant=var,state=state,low=low,reload=reload,registers=registers,mode=mode,instruction_boundaries=count))
    q=dict(passed=True,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),
           cases=cases,paths=len(paths),scope='Every actual instruction boundary through public injury-end and zero-timer draw paths, their farcalls and mapped cores. Includes MM/Proto/Bass/Roll/non-family, ground/air, logical/direct page/reload boundaries and two register sets. Linked hardware IRQ vector/handler restores PC/registers/meaningfulP/SP/live stack. Completed application RAM, non-banking stores and final mappings match the interrupted original with declared MM-family page deferral and legacy restore only during drawing. Native timed PPU/NMI/replays remain separate.')
    (a.output/'paths.json').write_text(json.dumps(paths,indent=2)+'\n')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
