"""Fresh exact-d52 movement callers plus explicitly supported wrapper bound."""
from pathlib import Path
import itertools,json,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_host_pipeline_controls_v1 as controls
import rogue_dawn_map_v1 as ref
from check_tmnt_render_oa import address
O=R/'build/rogue-dawn-host-pipeline-v2'

def main():
 controls.O=O;controls.B=O/'candidate.nes';controls.P=R/'build/roster-shared-celeste-small-v1.nes'
 controls.main()
 b=controls.d.old.scoped_load(controls.B);rows=[]
 # A declared conservative supported public wrapper entry216, not a claim
 # that it is the smallest possible integer. Real active admission was236.
 # It leaves source ControlStep at210, above its frozen minimum192.
 for kind,face,key in itertools.product(['head','floor','side','open'],[0,1],[0,128,129]):
  for seam in [None,('RdTxHead',95,'IRQ'),('RdHsPrepareActor',95,'lagNMI')]:
   if seam and(kind!='head' or face!=0 or key!=128):continue
   m=controls.base(b,kind,face,key)
   target=None if not seam else(address(b,seam[0]),seam[1],seam[2])
   c,low,tr=controls.d.call(m,'RdTxMovement',sp=216,seam=target)
   assert low>=128 and m[0x5c0b]==255 and m[0x5c3b]==0
   rows.append(dict(kind=kind,facing=face,input=key,entry_SP=216,minimum_SP=low,ISR=seam))
 old=json.loads((O/'controls.json').read_text());old['minimum_supported_public_wrapper_entry']=dict(SP=216,actual_admission_entry_SP=236,source_ControlStep_entry_SP=210,frozen_ControlStep_minimum_SP=192,stress_rows=rows,minimum_SP=min(r['minimum_SP']for r in rows),qualification='Conservative tested bound; actual source normal and catch-up call chains enter20bytes higher. Not a fictional SP224 caller substitute.')
 old['bindings'] += [ref.binding(p)for p in[Path(__file__),R/'tools/prepare_rogue_dawn_host_pipeline_v2.py']]
 (O/'controls.json').write_text(json.dumps(old,indent=2)+'\n');print(json.dumps(dict(wrapper_216_cases=len(rows),minimum_SP=min(r['minimum_SP']for r in rows))))
if __name__=='__main__':main()
