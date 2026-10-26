"""Actual mapper IRQ/RTI preservation at reached private hot-control boundaries."""
from pathlib import Path
import argparse,hashlib,json
from chip_hot_control_cpu_v2 import D,setup,clone,run,compare,phys
from check_tmnt_render_oa import load,address,location
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def state(m,c):
 g=next(g for g in m.bundle['segs'].values()if g.get('name')=='"SMCCODE"');lo=int(g['start'],0);hi=lo+int(g['size'],0)
 return(c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp,bytes(m[:0x100])+bytes(m[lo:hi])+bytes(m[0x200:0x800])+bytes(m[0x5c00:0x8000]),tuple(m.banks))
def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=load(a.candidate);f=D/'chip-idle-profiler-v1/fixture-v4';ss=[json.loads(x)for x in(f/'profile-snapshots.jsonl').read_text().splitlines()];raw=(f/'profile-snapshots.ram').read_bytes();cfg=json.loads((f/'configuration.json').read_text());s=next(x for x in ss if x['kind']=='component-entry'and x['detail']=='GameLoop');m,c=setup(b,s,raw,cfg)
 spans=[]
 for n,size in [('X5OwnMovement',49),('X5NewMovementFinish',60),('CdCameraMovementAdmission',73),('TnFastSideGate',43),('MmNativeSideShortcut',37),('MmSideDispatchPrefix',12)]:
  spans.append(((location(b,n)-16)//8192,address(b,n),address(b,n)+size,n))
 seen=set();skipped=set();writes=set();minimum=255;actual_side_states=[]
 def attach(m,c):
  nonlocal minimum
  step=c.step
  def injected():
   nonlocal minimum
   bank=phys(m,c.pc);owners=[n for k,lo,hi,n in spans if bank==k and lo<=c.pc<hi]
   key=(bank,c.pc)
   if owners and key not in seen:
    if c.p&4:skipped.add(key)
    else:
     seen.add(key);before=state(m,c);m[0x5204]=128;wi=len(m.writes);c.irq();assert c.pc==0x8000
     for _ in range(400):
      if c.pc==before[0]and c.sp==before[5]:break
      minimum=min(minimum,c.sp);step()
     else:raise AssertionError(('IRQ failed RTI',key))
     assert state(m,c)==before,('IRQ changed caller/SMC state',key)
     writes.update(at for at,v in m.writes[wi:]if 0x2000<=at<0x5c00)
   return step()
  c.step=injected
 attach(m,c)
 ret=((m[0x100+(c.sp+1)%256]|m[0x100+(c.sp+2)%256]<<8)+1)&65535;sp=(c.sp+2)&255
 for _ in range(100000):
  if c.pc==address(b,'MmNativeSideShortcut'):
   mm,cc=clone(b,m,c);actual_side_states.append((mm,cc))
  if c.pc==ret and c.sp==sp:break
  c.step()
 else:raise AssertionError('Main timeout')
 assert len(actual_side_states)==4
 # Exercise unchanged real turtle/Mac admission branches from the exact same
 # source-component query inputs. No claim of full foreign gameplay state.
 for ch in[4,12,14,15,17,19,20]:
  mm,cc=clone(b,*actual_side_states[0]);mm[address(b,'SelectedCharacter')]=ch;attach(mm,cc);run(mm,cc)
 assert writes and writes<=set([0x2005,0x2006,0x5128,0x5130]),writes
 proof=dict(passed=True,native_executed=False,ROM_sha256=sha(a.candidate),actual_compiled_IRQ_RTI_injections=len(seen),minimum_SP=minimum,hardware_store_addresses=sorted(writes),reached_boundaries=[dict(bank=k,PC=p)for k,p in sorted(seen)],I_masked_boundaries_skipped=[dict(bank=k,PC=p)for k,p in sorted(skipped-seen)],scope='Actual unchanged compiled mapper IRQ/vector/RTI at reached modified control instructions. Exact resumedAXYP/SP/applicationRAM/copiedSMC/banks. Untimed CPU bus, explicit mapper pending status, no actual NMI/PPU/DMA/DMC timing or native cadence claim.',checker_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k not in['reached_boundaries','I_masked_boundaries_skipped']},indent=2))
if __name__=='__main__':main()
