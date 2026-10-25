"""Interrupt every instruction of the linked shallow collision routers."""
from pathlib import Path
import argparse
import hashlib
import inspect
import itertools
import json
import check_collision_dispatch_oj as component
import check_tmnt_primary_irq_od as irq
from check_tmnt_render_oa import load,address


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.baseline),load(a.rom)
    source=inspect.getsource(component.run)
    anchor="    app={at:m[at] for at,v in m.writes if at not in allowed}"
    assert source.count(anchor)==1
    source=source.replace(anchor,"    allowed|={0x2005,0x2006,0x5128,0x5204,address(bundle,'IrqNewScroll')}\n    assert m[address(bundle,'IrqNewScroll')]==0\n"+anchor)
    namespace=dict(component.__dict__);namespace['NesMPU']=irq.InterruptProbe
    exec(compile(source,'<IRQ collision adapter>','exec'),namespace);run=namespace['run']
    cases=0;paths=[]
    profiles=[(i,i,0)for i in range(20)]+[(9,9,1),(9,255,1),(6,19,0),(19,6,0),(15,14,0),(255,255,0)]
    for entry,(char,acc,roll),crouch,(rh,state),flags in itertools.product(['ExpandedCollisionAdder','ExpandedCollisionBox'],profiles,[0,1],[(0,0),(0,1),(1,1)],[0x30,0x71]):
        spec=(char,acc,roll,crouch,1,rh,state,flags,(0xfe,0x81))
        irq.INJECT=0;expected=run(old,entry,spec)
        stores=[(at,v)for at,v in irq.LAST.memory.writes if at in [0x2005,0x2006,0x5128,0x5204]]
        irq.INJECT=None;plain=run(new,entry,spec);assert plain[0]==expected[0]
        count=len(irq.LAST.path)
        for instruction in range(count):
            irq.INJECT=instruction;actual=run(new,entry,spec)
            assert irq.LAST.interrupted and actual[0]==expected[0],(entry,spec,instruction)
            actual_stores=[(at,v)for at,v in irq.LAST.memory.writes if at in [0x2005,0x2006,0x5128,0x5204]]
            assert actual_stores==stores
            cases+=1
        paths.append(dict(entry=entry,profile=[char,acc,roll],crouch=crouch,RollHurt=rh,state=state,flags=flags,instruction_boundaries=count))
    q=dict(passed=True,accepted=False,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),
        cases=cases,paths=len(paths),component_sha256=hashlib.sha256(Path(component.__file__).read_bytes()).hexdigest(),
        scope='Actual linked IRQ at every instruction boundary of both public queries and their real leaf/return paths. All20IDs, Roll override, mismatched/unsupported input, crouch/hurt/state and flag seeds. IRQ restores PC/registers/meaningfulP/SP/live stack; completed query A/X/Y/fullP/SP, application state, final mappings and ordered IRQ stores match the interrupted old path. Only exact IRQ hardware/temporary IrqNewScroll stores are admitted beyond the original query exclusions. No timed audio-NMI or campaign claim.')
    (a.output/'paths.json').write_text(json.dumps(paths,indent=2)+'\n');(a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
