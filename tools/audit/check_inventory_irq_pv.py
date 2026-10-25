"""Keep the mode predicate's old boolean/register contract, repair its A input."""
from pathlib import Path
import argparse,hashlib,itertools,json
import check_inventory_stack_og as component
import check_tmnt_primary_irq_od as irq
from check_tmnt_render_oa import load
def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.baseline),load(a.rom);component.NesMPU=irq.InterruptProbe
 profiles=[(0,0,0,0),(1,0,0,0),(2,0,0,0),(3,0,0,0),(4,0,0,0),(4,0,0,1),(4,0,0,2),(5,0,0,0),(5,0,1,0),(5,0,2,0),(5,0,3,0),(5,0,4,0),(6,0,0,0),(9,0,0,0),(9,1,0,0),(9,255,0,0),(11,0,0,0),(15,0,0,0),(19,0,0,0),(255,255,255,255)]
 cases=paths=0;minimum=255
 for (char,roll,cv3,z2),mode,regs in itertools.product(profiles,[0,1,255],[(0x56,7,0xa3),(0,255,0)]):
  spec=(char,mode,roll,cv3,z2,0x30,regs);irq.INJECT=0;before=component.run(old,spec,allow_irq=True)
  aa,xx,yy,pp,sp=before[0];want=(regs[0],xx,yy,(pp&~0x82)|(0x80 if regs[0]&128 else 0)|(2 if regs[0]==0 else 0),sp)
  irq.INJECT=None;plain=component.run(new,spec);assert plain[0]==want,(spec,plain[0],want)
  count=len(irq.LAST.path);minimum=min(minimum,plain[2])
  for boundary in range(count):
   irq.INJECT=boundary;actual=component.run(new,spec,allow_irq=True)
   assert irq.LAST.interrupted and actual[0]==want and actual[3]==before[3],(spec,boundary,actual[0],want)
   minimum=min(minimum,actual[2]);cases+=1
  paths+=1
 q=dict(passed=True,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),paths=paths,injected_IRQ_boundaries=cases,minimum_SP=minimum,
  scope='Actual linked IRQ at every tested predicate/farcall/leaf/return boundary; old boolean C, X/Y/V/D/I/SP, banks and ordered IRQ writes retained. A and its N/Z intentionally match the original requested item. No timed audio-NMI claim; actual native tests are separate.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q),flush=True)
if __name__=='__main__':main()
