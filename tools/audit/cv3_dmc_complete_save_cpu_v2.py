"""Actual old Save loop versus same-PC unrolled helper, including real IRQ/RTI."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import load,address,location
from cv3_dmc_complete_cpu_v1 import LaneArena
from verify_native_relocation import NesMPU
IRQ_PORTS=[0x2005,0x2006,0x5128,0x5204]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def state(c):return(c.a,c.x,c.y,c.p&0xcf,c.sp)
def run(q,seed,flags,interrupt=False):
 pc=address(q.b,'Save');at=location(q.b,'Save');assert(at-16)//8192==28
 q.m.page(2,28);q.set('CurrentBankC',156);q.put(IrqPPUCTRL=1,IrqNewScroll=0x53)
 for i in range(256):q.m[i]=(73*i+31*seed+seed*seed)&255
 for name in ['RgAudioZp','RgAudioCpuZp']:
  for i in range(24):q.set(name,(i*29+seed*19+(7 if name=='RgAudioCpuZp'else 0))&255,i)
 q.m.writes=[];c=NesMPU(memory=q.m,pc=pc);c.a,c.x,c.y,c.p,c.sp=(seed*3)&255,(seed*7)&255,23,flags,0xfd;n=0
 while c.pc!=pc+18:
  assert n<1000
  if interrupt:
   before=(state(c),c.pc,list(q.m.banks),q.get('CurrentBankC'));c.irq();assert c.pc==address(q.b,'IrqScrollSplit')
   for _ in range(100):
    c.step()
    if c.pc==before[1]and c.sp==before[0][-1]:break
   else:raise AssertionError('No actual RTI')
   assert(state(c),c.pc,list(q.m.banks),q.get('CurrentBankC'))==before
  c.step();n+=1
 writes=[(a,v)for a,v in q.m.writes if not 0x100<=a<0x200 and not(interrupt and a in IRQ_PORTS)]
 return c,writes,n
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=[load(a.prepared/n)for n in['held-candidate.nes','candidate.nes']];rows=[];irqs=0
 for b,n in[(old,'held-candidate'),(new,'candidate')]:
  matched=[]
  for line in(a.prepared/(n+'.dbg')).read_text().splitlines():
   if not line.startswith('sym\t')or'name="Save"'not in line:continue
   rec=dict(s.split('=',1)for s in line[4:].split(',')if'='in s)
   if b['segs'][rec.get('seg','0')].get('name')=='"CV_WRAP"':matched.append(rec)
  assert len(matched)==1;b['syms']['Save']=matched[0]
 for seed,flags in itertools.product(range(256),(0x20,0x21,0x60,0x61,0xa0,0xa1,0xe0,0xe1)):
  qs=[LaneArena(b,5)for b in[old,new]];rs=[run(q,seed,flags)for q in qs]
  assert state(rs[0][0])==state(rs[1][0])and rs[0][1]==rs[1][1]
  assert all(qs[0].m[i]==qs[1].m[i]for i in range(0x8000)if not 0x100<=i<0x200)
  assert qs[0].m.banks==qs[1].m.banks
  rows.append(rs[1][0].processorCycles-rs[0][0].processorCycles)
 for seed,flags in itertools.product((0,7,255),(0x20,0x21,0x60,0x61)):
  qs=[LaneArena(new,5)for _ in range(2)];cs=[run(q,seed,flags,bool(i))for i,q in enumerate(qs)];assert state(cs[0][0])==state(cs[1][0])and cs[0][1]==cs[1][1],(seed,flags,state(cs[0][0]),state(cs[1][0]),cs[0][1][:8],cs[1][1][:8])
  assert all(qs[0].m[i]==qs[1].m[i]for i in range(0x8000)if not 0x100<=i<0x200 and i not in IRQ_PORTS);irqs+=cs[1][2]
 ob,nb=old['raw'],new['raw'];diffs=[i for i,(u,v)in enumerate(zip(ob,nb))if u!=v];start=16+28*8192
 # No writes below this point: ROM layout checked after CPU cases.
 assert all(start+0x1837<=i<start+0x1837+247 or location(old,'Save')<=i<location(old,'Save')+18 for i in diffs)
 result=dict(passed=True,candidate_sha256=sha(a.prepared/'candidate.nes'),held_sha256=sha(a.prepared/'held-candidate.nes'),valid_Save_cases=len(rows),same_ordered_memory_writes_and_all_RAM_except_transient_stack=True,AXYP_SP_mapper_exact=True,Save_cycle_delta_values=sorted(set(rows)),actual_IRQ_RTI_boundaries=irqs,only_held_ROM_changes=dict(bank=28,unreachable_slack=[0xd837,0xd837+247],original_Save_body=[address(old,'Save'),address(old,'Save')+18]),scope='Assembled exact valid24-byte Save loop contract, full old/new AudioUpdate checked separately. No native cadence claim.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
