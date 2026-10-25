"""Interrupt every instruction of all eight native HUD icon paths."""
from pathlib import Path
import argparse
import hashlib
import json
import check_tmnt_world_oe as world
import check_tmnt_primary_irq_od as irq
from check_tmnt_render_oa import load,address,location


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.baseline),load(a.rom)
    world.NesMPU=irq.InterruptProbe;cases=0;paths=[]
    for face in ['R','L']:
        lo,hi=location(old,'TnWorld'+face+'Lo'),location(old,'TnWorld'+face+'Hi')
        for pose in [80,81,82,83]:
            ptr=old['raw'][lo+pose]|old['raw'][hi+pose]<<8
            for y in [16,23]:
                for rotation in [(0,0),(1,128)]:
                    args=(ptr,(128,y,0,1),112,rotation,0x30,0x20)
                    irq.INJECT=0;expected=world.run(old,address(old,'TnFastWorldRender'),*args)
                    irq.INJECT=None;world.run(new,address(new,'TnFastWorldRender'),*args);count=len(irq.LAST.path)
                    for instruction in range(count):
                        irq.INJECT=instruction;actual=world.run(new,address(new,'TnFastWorldRender'),*args)
                        assert irq.LAST.interrupted and actual[:4]==expected[:4],(face,pose,y,rotation,instruction,expected[0],actual[0])
                        cases+=1
                    paths.append(dict(face=face,pose=pose,y=y,rotation=rotation,instruction_boundaries=count))
    q=dict(passed=True,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),
           cases=cases,paths=len(paths),scope='Every actual instruction boundary for all8 source HUD icons atY16/23 and two OAM rotations, interrupted through the linked hardware IRQ vector/handler. Exact register/meaningful flags/SP/PC/live stack restore; completed application RAM except discarded stack/SMC/safecall bookkeeping/mapper latches, ordered OAM and final banks match the interrupted original helper. CPU interruption component, separate from native PPU/NMI timing and routes.')
    (a.output/'cases.json').write_text(json.dumps(paths,indent=2)+'\n');(a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
